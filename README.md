# Drosophila Immune Enhancer Atlas

A web-based database for exploring enhancer-gene associations in *Drosophila melanogaster* immune response, built from STARR-seq data.

---

## Overview

This application enables users to search and visualize enhancer–gene relationships using three main query modes:

- **Search by Proximity (Tab 1)**: Query genes near a genomic region or enhancer
- **Search by Gene (Tab 2)**: Identify enhancers associated with a gene
- **Search by Activity Info (Tab 3)**: Filter enhancers by activity class and accessibility

The system consists of:
- **Frontend**: HTML/CSS interface for user interaction
- **Backend**: Flask application handling queries and logic
- **Database**: MySQL database storing processed enhancer–gene data

---

## Project Structure
```
project_folder/
├── base_data/ # Raw datasets (reference only)
├── processed_data/ # Cleaned data used for database upload
│ ├── associations.csv
│ ├── enhancer.csv
│ ├── genes.csv
│ └── tab3_data.csv
├── app.py # Main backend (Flask application)
├── templates/ # Frontend HTML templates
│ ├── tab_1.html
│ ├── tab_2.html
│ ├── tab_3.html
│ └── template.html
├── static/ # CSS, JS, images
├── table_upload.py # Script to load data into MySQL
├── sql_files/ # SQL scripts for schema creation
├── requirements.txt # Python dependencies
├── data_extract.ipynb # Data preprocessing notebook
└── README.md
```

---

## System Components

### Database
- MySQL (hosted locally or via Aiven)
- Stores enhancer, gene, and association data
- Schema defined in `sql_files/`

### Backend
- Flask application (`app.py`)
- Handles all queries and filtering logic
- Connects to database via environment variables

### Frontend
- HTML templates rendered by Flask
- Visualizations generated using JavaScript (Google Charts)

---

## Deployment Overview

The application can be deployed using:

- **VPS (recommended)**: DigitalOcean / Vultr  
  - Full control, lower cost, long-term stability  
- **Managed services**: Render + Aiven  
  - Easier setup, higher cost, less control  

---

## Configuration

Sensitive credentials are stored in a `.env` file:
```
DB_HOST=
DB_USER=
DB_PASS=
DB_NAME=
DB_PORT=
```


IMPORTANT: This file is not included in version control and must be configured separately.

---

## Data Management

### Source Data
- Raw data is stored in `base_data/`
- Processed data used for the application is stored in `processed_data/`

### Database Loading
- Data is loaded into MySQL using `table_upload.py`
- Tables are created using SQL scripts in `sql_files/`

### Updating Data
To update the dataset:
1. Replace files in `processed_data/`
2. Re-run the data upload script: 
```
python table_upload.py
```
