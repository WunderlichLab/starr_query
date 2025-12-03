# Drosophila Immune Enhancer Atlas

A web-based database for exploring enhancer-gene associations in Drosophila melanogaster immune response, 
built from STARR-seq data.

# About This Database
This website helps you search and visualize how enhancers regulate genes during the Drosophila immune response. 
The database includes three main search tools:

Search by Proximity (Tab 1): Find genes near a specific enhancer by entering chromosomal coordinates or an enhancer name.

Search by Genes (Tab 2): Enter a gene name and find all the enhancers that regulate it.

Search by Activity Info (Tab 3): Find enhancers based on their activity patterns (like activity class or chromatin accessibility). 

All search results can be downloaded as CSV, TSV, or Excel files for further analysis. Each tab also includes visualizations to help you understand the data distribution.

## Repo Structure

```
project_folder/
├── base_data/
│   ├── Allsamples_tpm.csv
│   ├── dmel-all-r6.64.gtf
│   ├── Drosophila_melanogaster.BDGP6.54.115.gtf
│   ├── EG_activity_class.csv]
│   ├── EG_activity_class_modified.csv
│   ├── EG_all_clean_09_05.csv
│   ├── EnhancerGene20E_df_clean_09_09.csv
│   ├── EnhancerGeneCon_df_clean_09_09.csv
│   └── EnhancerGeneHKSM_df_clean_09_09.csv
├── processed_data/
│   ├── associations.csv
│   ├── enhancer.csv
│   ├── genes.csv
│   └── tab3_data.csv
├── app.py
├── templates/
│   ├── tab_1.html
│   ├── tab_2.html
│   ├── tab_3.html
│   └── template.html
├── templates/
│   ├── images/
    │   ├── wunder_lab_clear.png
    │   └── activity_class_venn.png
│   └── design.css
├── requirements.txt
├── data_extract.ipynb       # Preprocessing data
├── create_tables.sql        # Creating tables for database
└── README.md                # Project description and setup instructions
```


## Moving Project to New Computer
### What You'll Need
Before starting, make sure you have these programs installed on your computer:

1. Python 3.8 or newer
2. Git
3. MariaDB or MySQL

This is the database software that stores all the enhancer data
Follow the installation wizard and remember the password you set!

#### Step 1: Download the Data Files

Go to the Google Drive link: [https://drive.google.com/drive/folders/1SoevyQVR2uid_NShFBZ_pLEu-M1_vrhQ?usp=sharing]   
Download the proccessed_data folder.

#### Step 2: Get the Website Code

Create a folder on your computer where you want to keep the website files.

Open Terminal (Mac/Linux) or Command Prompt (Windows)

Navigate to your folder by typing this command (adjust the path to match where you created your folder):

```cd your/file/path```

Download the code by typing:

```git clone https://github.com/WunderlichLab/starr_query.git```

Move into the downloaded folder:

```cd starr_query```

Move the processed_data folder to starr_query folder

#### Step 3: Set Up the Database
```
CREATE DATABASE enhancer_db;
 mysql -u root -p enhancer_db < path/to/your/downloaded/create_tables.sql
```

Replace path/to/your/downloaded/file.sql with the actual location of your file

#### Step 4: Configure the Website

Create a configuration file:

In your website folder, create a new file called .env
You can do this by opening Notepad (Windows) or TextEdit (Mac)

Add these lines to the file (replace the values with your actual database details):

```
   DB_HOST=localhost
   DB_USER=root
   DB_PASS=your_database_password
   DB_NAME=enhancer_db
   DB_PORT=3306
```
Save the file as .env in the main website folder

Make sure it's named exactly .env (with the dot at the beginning)


#### Step 5: Install Required Python Packages

In your Terminal/Command Prompt, make sure you're still in the website folder
Install the packages by typing:

```
pip install flask mariadb python-dotenv
```
Wait for the installation to complete (this might take a minute or two)

#### Step 6: Run the Website!

Start the website by typing:

```
python app.py
```

Open your web browser (Chrome, Firefox, Safari, etc.)
Go to this address:

   http://localhost:5000

That's it! The database should now be running on your computer


## Stopping the Website
When you're done using the database:

Go back to your Terminal/Command Prompt
Press Ctrl + C to stop the server