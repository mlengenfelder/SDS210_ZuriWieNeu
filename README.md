# ZüriWieNeu – Spatial Analysis of reported urban issues in the City of Zurich

**Project Description:** 
This project structures and analyzes urban issue reports from the "ZüriWieNeu" platform in Zurich (2013–2025). By applying spatial joins and clustering algorithms (DBSCAN), the analysis answers questions regarding report density, dominant problem categories, spatial hotspots of frustrated reports, and long-term reporting trends.

## Data Sources
The raw data is not included in this repository. Please download the data from the Open Data Portal Zurich before running the code. Access the links below and make sure to select _Ausschnitt: Gesamter Datensatz_ and _Format: GPKG_. Then click download. Follow the further instructions of the website. 

**Statistische Quartiere (Neighborhoods):** 
[Download here](https://www.stadt-zuerich.ch/geodaten/download/Statistische_Quartiere?format=10005)

**ZüriWieNeu Reports:** 
[Download here](https://www.stadt-zuerich.ch/geodaten/download/Zueri_wie_neu?format=10005)

##  Setup Instructions

### Step 1: Clone the Repository
First, download this repository to your local computer and enter the directory:
'''bash
cd ~/Desktop
git clone https://github.com/mlengenfelder/SDS210_ZuriWieNeu
cd SDS210_ZuriWieNeu
'''

### Step 2: Create and Activate the Environment
conda env create -f environment.yml
conda activate zuriwieneu_env

### Step 3: Initialize the Directory Tree
* Open your Jupyter environment, open the notebook ZuriWieNeu_Spatial_Analysis.ipynb, select zuriwieneu_env as your kernel, and run the very first setup cell (Section 1).
* Running this cell automatically creates the local folder path structure (data/raw/, data/processed/, outputs/figures/, etc.) that is missing from the repository.

### Step 4: Download and Position the Raw Data
Now that the paths exist, download the raw data from the Open Data Portal Zurich. Access the links above in the Data source section. 

Rename the whole, downloaded folder accordingly:
* The Statistische Quartiere to: **Quartiere_ZH_GPKG**
* The Reports to: **Reports_GPKG**

Finally, move both renamed folders into your newly generated project folder:

* SDS210_ZuriWieNeu/data/raw/

## Execution Order
* Open the ZuriWieNeu_Spatial_Analysis.ipynb notebook.
* Ensure your notebook kernel is set to zuriwieneu_env.
* Run the remaining cells sequentially from top to bottom (Cell-wise is highly recommended).
* Custom helper functions (such as CRS handling, frustration flagging, and DBSCAN clustering) are imported automatically from the local utils.py file.
* All outputs (interactive maps, plots, and metrics) will be saved in the outputs/ and data / processed. 