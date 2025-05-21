# Large-scale Enhancer Screen Database

This project aims to develop a database to systematically capture and query data from a large-scale enhancer screen.   

Enhancers are sequences that promote the expression of the associated gene sequences. The underlying dataset utilizes STARR-seq to measure Drosophila enhancer activity and gene expression across experimental conditions exploring regulatory mechanisms in immune responses. At the moment, the dataset provided by the Wunderlich lab contains data from three experimental conditions:  
- Control
- Hormone Treatment (20E)
- Immune Treatment (HKSM with 20E)
  
Integrating information regarding: 
- Genomic Enhancer Coordinates
- Associated Genes
- Gene Expression Changes (LogFC)
- Immune Pathway Annotations
- Transcription Factor Motifs
- Enhancer Activity Scores
  
Our database will incorporate this data to allow researchers easy access and retrieval of enhancer-gene interactions. It will be designed for supporting structured queries on enhancer activity, gene expression patterns, and motif enrichment.  

## Repo Structure

```
project_folder/
├── app.py
├── templates/
│   ├── find_enhancer_results.html
│   ├── fine_gene_results.html
│   └── template.html
├── templates/
│   ├── images/
    │   └── wunderlich_lab_clear.png
│   └── design.css
├── db_schema.sql
├── requirements.txt
├── 1_creating_files.ipynb   # Preprocessing data
├── create_tables.sql        # Creating tables for database
├── queries.sql              # Database queries
└── README.md                # Project description and setup instructions
```
```#``` indicate files not necessary for database website implementation

## Moving Project to New Computer
### New Computer Requirements
- internet server (Apache or similar)
- mod_wsgi (works with Apache to serve flask programs)
- mariadb

### Database Structure
db_schema.sql contains the database structure which contains CREATE TABLE instructions. Restore the structure on the new computer using:
```
mariadb -u your_user -p -e "CREATE DATABASE your_database_name;"
mariadb -u your_user -p your_database_name < db_schema.sql
```
Then, upload the data manually (LOAD DATA LOCAL INFILE) once the tables are created.

### Python Packages
On the new computer, install all the Python packages with the following:
```
pip3 install -r requirements.txt
```

### File Organization
The files will have the same organization as shown earlier (Repo Structure) on the new computer, but the project_folder will be dependent on
the mod_wsgi setup.

## Website Tour
### Introduction tab
![image](https://github.com/user-attachments/assets/28ec5be2-a0a7-4287-b354-9b02c9a56898)
### Enhancer→Gene tab
![image](https://github.com/user-attachments/assets/bde351e7-e686-4433-9ae9-dac4b1a35270)
### Gene→Enhancer tab
![image](https://github.com/user-attachments/assets/6b65a835-fc1a-4b1e-b40a-686bb5021f26)
![image](https://github.com/user-attachments/assets/b1bccfbd-f94f-480b-8f28-1528bcc13cf4)
### Help Page
![image](https://github.com/user-attachments/assets/a451fdbb-7b68-48ad-8714-87050f4603d3)
![image](https://github.com/user-attachments/assets/f9d1d473-31e1-4881-8288-45e4ebbb2103)

