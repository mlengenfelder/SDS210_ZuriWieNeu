import pandas as pd
import geopandas as gpd
from sklearn.cluster import DBSCAN


def check_and_fix_crs(gdf, gdf_name, target_crs='EPSG:2056'):
    """
    Checks the CRS of a GeoDataFrame and corrects it if necessary.

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        The input GeoDataFrame to check.
    gdf_name : str
        The name of the GeoDataFrame.
    target_crs : str, optional
        The target Coordinate Reference System (default is 'EPSG:2056').

    Returns
    -------
    geopandas.GeoDataFrame
        The GeoDataFrame with the corrected CRS.
    """
    if gdf.crs is None:
        print(f'!!! Warning: {gdf_name} has no defined CRS! Set to {target_crs}...')
        return gdf.set_crs(target_crs)
    elif gdf.crs != target_crs:
        print(f'{gdf_name} CRS is {gdf.crs}. Convert to {target_crs}...')
        return gdf.to_crs(target_crs)
    else:
        print(f'{gdf_name} is already in Target CRS: {target_crs}')
        return gdf


def flag_frustrated_reports(text_series, keywords):
    """
    Flags reports as frustrated based on a list of keywords or exclamation marks.

    Parameters
    ----------
    text_series : pandas.Series
        A series containing the text descriptions of the reports.
    keywords : list of str
        A list of words indicating frustration.

    Returns
    -------
    pandas.Series
        A boolean series where True indicates a frustrated report.
    """
    search_pattern = '|'.join([r'\b' + word + r'\b' for word in keywords]) + r'|!+'

    return text_series.str.contains(search_pattern, case=False, na=False)


def prepare_reports_base(gdf, keywords):
    """
    Calculates basic temporal metrics and flags frustrated reports.

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        The raw reports GeoDataFrame.
    keywords : list of str
        List of keywords to flag frustration.

    Returns
    -------
    geopandas.GeoDataFrame
        The enriched reports GeoDataFrame.
    """
    gdf = gdf.copy()

    gdf['year']  = gdf['requested_datetime'].dt.year
    gdf['month'] = gdf['requested_datetime'].dt.month

    gdf.loc[gdf['status'] == 'fixed - council', 'solving_duration'] = (
        (gdf['updated_datetime'] - gdf['requested_datetime'])
        .dt.total_seconds() / (24 * 3600)).round(2)

    gdf['is_frustrated'] = flag_frustrated_reports(gdf['detail'], keywords)
        
    return gdf


def prepare_quartiere_base(gdf):
    """
    Calculates the area in square kilometers for each Quartier.

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        The raw Quartiere GeoDataFrame.

    Returns
    -------
    geopandas.GeoDataFrame
        The enriched Quartiere GeoDataFrame with an 'area_km2' column.
    """
    gdf = gdf.copy()

    gdf['area_km2'] = (gdf.geometry.area / 10**6).round(2)
   
    return gdf


def sjoin_and_stats(reports_gdf, quartiere_gdf, period_1, period_2, min_avg=10):
    """
    Performs a spatial join and calculates aggregated statistics per Quartier.

    Parameters
    ----------
    reports_gdf : geopandas.GeoDataFrame
        The prepared reports GeoDataFrame.
    quartiere_gdf : geopandas.GeoDataFrame
        The prepared Quartiere GeoDataFrame.
    period_1 : list of int
        List of years defining the first comparative period.
    period_2 : list of int
        List of years defining the second comparative period.
    min_avg : int, optional
        Minimum average reports required to calculate growth rate (default is 10).

    Returns
    -------
    tuple
        A tuple containing (reports_gdf, quartiere_gdf, category_count, growth_df).
    """
    reports_gdf = reports_gdf.copy()
    quartiere_gdf = quartiere_gdf.copy()

    reports_gdf = gpd.sjoin(
        reports_gdf,
        quartiere_gdf[['qname', 'geometry']],
        how='left',
        predicate='within'
    ).drop(columns='index_right', errors='ignore')

    unassigned_points = reports_gdf['qname'].isna().sum()
    print(f'Number of unassigned points: {unassigned_points}')

    reports_gdf = reports_gdf.dropna(subset=['qname'])
    unassigned_points = reports_gdf['qname'].isna().sum()

    if unassigned_points == 0:
        print(f'Unassigned points were successfully dropped to {unassigned_points}!')
    else:
        print(f'!!! Warning: There are still {unassigned_points} Points!')

    metrics_df = reports_gdf.groupby('qname').agg(
        report_count=('service_request_id', 'count'),
        avg_solving_days=('solving_duration', 'mean'),
        frustration_rate=('is_frustrated', 'mean')
    ).reset_index()

    metrics_df['avg_solving_days'] = (metrics_df['avg_solving_days']).round(1)
    metrics_df['frustration_rate'] = (metrics_df['frustration_rate'] * 100).round(1)

    quartiere_gdf = quartiere_gdf.merge(metrics_df, on='qname', how='left')
    quartiere_gdf['reports_per_km2'] = (quartiere_gdf['report_count'] / quartiere_gdf['area_km2']).round(0).astype('Int64')

    category_count = pd.crosstab(reports_gdf['qname'], reports_gdf['service_name'])
    category_count['top_category'] = category_count.idxmax(axis=1)
   
    quartiere_gdf = quartiere_gdf.merge(category_count['top_category'].reset_index(), on='qname', how='left')

    annual_counts = pd.crosstab(reports_gdf['qname'], reports_gdf['year'])

    growth_df = pd.DataFrame({
        'avg_Period_1': annual_counts.reindex(columns=period_1, fill_value=0).mean(axis=1),
        'avg_Period_2': annual_counts.reindex(columns=period_2, fill_value=0).mean(axis=1)
    })

    growth_df = growth_df[growth_df['avg_Period_1'] >= min_avg].copy()
    growth_df['growth_rate'] = (((growth_df['avg_Period_2'] - growth_df['avg_Period_1']) / growth_df['avg_Period_1'])*100).round(0).astype('Int64')

    quartiere_gdf = quartiere_gdf.merge(growth_df[['growth_rate']], on='qname', how='left')

    return reports_gdf, quartiere_gdf, category_count, growth_df


def reports_clustering(reports_gdf, eps, min_samples):
    """
    Applies the DBSCAN algorithm to find spatial clusters of frustrated reports.

    Parameters
    ----------
    reports_gdf : geopandas.GeoDataFrame
        The enriched reports GeoDataFrame containing the 'is_frustrated' flag.
    eps : float
        The maximum distance between two samples for one to be considered in the neighborhood.
    min_samples : int
        The number of samples in a neighborhood for a point to be considered a core point.

    Returns
    -------
    tuple
        (frustrated_gdf, dbscan_clusters, dbscan_noise, cluster_polygons).
    """
    frustrated_gdf = reports_gdf[reports_gdf['is_frustrated']].copy()
    coords = frustrated_gdf.geometry.get_coordinates().values

    dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
    frustrated_gdf['cluster_id'] = dbscan.labels_

    dbscan_clusters = frustrated_gdf[frustrated_gdf['cluster_id'] != -1]
    dbscan_noise    = frustrated_gdf[frustrated_gdf['cluster_id'] == -1]

    cluster_polygons = dbscan_clusters.dissolve(by='cluster_id', aggfunc={'service_request_id': 'count'})
    cluster_polygons = cluster_polygons.rename(columns={'service_request_id': 'n_points'})
    cluster_polygons['geometry'] = cluster_polygons.geometry.convex_hull

    return frustrated_gdf, dbscan_clusters, dbscan_noise, cluster_polygons


def summary_questions(final_reports_gdf, final_quartiere_gdf, cluster_polygons):
    """
    Prints a formatted summary of the spatial analysis results answering the 4 questions.

    Parameters
    ----------
    final_reports_gdf : geopandas.GeoDataFrame
        The fully processed reports GeoDataFrame.
    final_quartiere_gdf : geopandas.GeoDataFrame
        The fully processed Quartiere GeoDataFrame.
    cluster_polygons : geopandas.GeoDataFrame
        The generated DBSCAN cluster polygons.
    """
    print('=' * 55)
    print('RESULTS: ZüriWieNeu–Analysis                  2013–2025')
    print('=' * 55)
    print(f'Analysed Reports:                            {len(final_reports_gdf):>10,}')
    print(f'Time period:                                2013 – 2025')
    print(f'Quartiere covered:                           {final_quartiere_gdf["qname"].nunique():>10}')
    print()

    top_density = final_quartiere_gdf.nlargest(1, 'reports_per_km2').iloc[0]
    print(f'Q1 – Highest Report density:                {top_density["qname"]}')
    print(f'                                     ({top_density["reports_per_km2"]:.0f} Reports/km2)')
    print()

    top_cat = final_quartiere_gdf['top_category'].value_counts().idxmax()
    print(f'Q2 – Dominant Problem-Category:     {top_cat}')
    print()

    top_frust = final_quartiere_gdf.nlargest(1, 'frustration_rate').iloc[0]
    n_clusters = len(cluster_polygons)
    print(f'Q3 – Highest frustration-Rate:          {top_frust["qname"]} ({top_frust["frustration_rate"]}%)')
    print(f'     DBSCAN:         {n_clusters} Frustration-Clusters identified')
    print()

    top_growth = final_quartiere_gdf.nlargest(1, 'growth_rate').iloc[0]
    print(f'Q4 – Strongest Growth:              {top_growth["qname"]} (+{top_growth["growth_rate"]}%)')
    print('=' * 55)