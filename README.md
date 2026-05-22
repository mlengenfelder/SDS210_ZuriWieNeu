# ZüriWieNeu – Spatial Analysis of reported urban issues in the City of Zurich

**Project Description:** 
This project structures and analyzes urban issue reports from the "ZüriWieNeu" platform in Zurich (2013–2025). By applying spatial joins and clustering algorithms (DBSCAN), the analysis answers questions regarding report density, dominant problem categories, spatial hotspots of frustrated reports, and long-term reporting trends.

## Data Sources
The raw data is not included in this repository. Please download the data from the Open Data Portal Zurich before running the code. Access the links below and make sure to select _Ausschnitt: Gesamter Datensatz_ and _Format: GPKG_. Then click download. Follow the further instructions of the website. 

**Statistische Quartiere (Neighborhoods):** 
[Download here](https://www.stadt-zuerich.ch/geodaten/download/Statistische_Quartiere?format=10005)

**ZüriWieNeu Reports:** 
[Download here](https://www.stadt-zuerich.ch/geodaten/download/Zueri_wie_neu?format=10005)

**Data Setup:** 
Rename the whole, downloaded folder accordingly:
* The Statistische Quartiere to: **Quartiere_ZH_GPKG**
* The Reports to: **Reports_GPKG**

##  Setup Instructions
First, download the linked GitHub repository to your computer:

'''bash
git clone .git
'''

To ensure maximum reproducibility, an `environment.yml` is provided. Create and activate the conda environment via:

'''bash
conda env create -f environment.yml
conda activate zuriwieneu_env
'''

git clone https://github.com/mlengenfelder/SDS210_ZuriWieNeu
cd <your-repo>
conda env create -f environment.yml
conda activate zuriwieneu_env

Place the two downloaded folders into:

`SDS210_ZuriWieNeu/data/raw/`

Rename them exactly like this:

* `Reports_GPKG`
* `Quartiere_ZH_GPKG`

## Execution Order

* Open the ZuriWieNeu_Spatial_Analysis.ipynb notebook.
* Run the notebook sequentially from top to bottom or as a whole (Restart & Run All, step-wise is recommended).
* The custom helper functions are imported automatically from utils.py.
* All outputs (interactive maps, plots, and metrics) will be saved in the outputs/ and data / processed. 