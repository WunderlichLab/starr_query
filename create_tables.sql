-- select database
USE starr_query;
SHOW tables;

-- drop table statements, "child" Associations table first
DROP TABLE IF EXISTS Associations; 
DROP TABLE IF EXISTS Genes;
DROP TABLE IF EXISTS Enhancers;

-- create tables 

CREATE TABLE Enhancers (
eid INTEGER NOT NULL AUTO_INCREMENT, 
name VARCHAR(30),
chromosome VARCHAR(2),
exp_condition ENUM('Control','20E','IMD'),
start INTEGER,
end INTEGER,
en_length INTEGER,
tf_counts VARCHAR(150),
tbs INTEGER,
PRIMARY KEY (eid), 
INDEX location (chromosome, start, end) 
) ENGINE=innodb;

CREATE TABLE Genes ( 
gid INTEGER NOT NULL AUTO_INCREMENT,
geneid VARCHAR(20),
chromosome ENUM('3R','3L','2R','2L','X','Y','4'),
start INTEGER,
end INTEGER,
gene_length INTEGER,
symbol VARCHAR(20), 
immune_process VARCHAR(50), 
time_cluster ENUM('early_C2','mid_C3','late_C1','late_C4'),
tpm_ctrl DOUBLE,
tpm_20e DOUBLE,
tpm_imd DOUBLE,
PRIMARY KEY (gid), 
INDEX location (chromosome, start, end) 
) ENGINE=innodb;

CREATE TABLE Associations (  
eid INTEGER NOT NULL, 
gid INTEGER NOT NULL,
imd_vs_ctrl DOUBLE,
imd_vs_20e DOUBLE,
20e_vs_ctrl DOUBLE,
tpm_ctrl DOUBLE,
tpm_20e DOUBLE,
tpm_imd DOUBLE,
exp_condition ENUM('Control', '20E', 'IMD'),
activity DOUBLE, 
PRIMARY KEY (eid, gid, exp_condition), 
FOREIGN KEY (eid) REFERENCES Enhancers (eid) ON UPDATE CASCADE ON DELETE CASCADE, 
FOREIGN KEY (gid) REFERENCES Genes (gid) ON UPDATE CASCADE ON DELETE CASCADE 
) engine=innodb; 


-- loading in data
-- note that empty fields are designated by NULL 

LOAD DATA LOCAL INFILE '/Users/anushka/BU/starr_query/processed_data/enhancer.csv'
INTO TABLE Enhancers
FIELDS TERMINATED BY ','
IGNORE 1 LINES
(name, chromosome, start, end, en_length, exp_condition, @tf_counts,@tbs)
set tf_counts = NULLIF(@tf_counts, ''),
  tbs = NULLIF(@tbs, '');

load data local infile '/Users/anushka/BU/starr_query/processed_data/genes.csv'
into table Genes
fields terminated by ','
ignore 1 lines
(geneid, chromosome, start, end, symbol, @immune_process, @time_cluster, gene_length, tpm_ctrl, tpm_20e, tpm_imd)
set immune_process = NULLIF(@immune_process, ''),
  time_cluster = NULLIF(@time_cluster, '');


-- for Associations table, need to create a temp table first
-- csv file only has enhancer name and gene id so need to join tables

DROP TABLE IF EXISTS TempAssociations;

CREATE TEMPORARY TABLE TempAssociations (
  enhancer_name VARCHAR(30),
  geneid VARCHAR(20),
  imd_vs_ctrl DOUBLE,
  imd_vs_20e DOUBLE,
  20e_vs_ctrl DOUBLE,
  exp_condition ENUM('Control', '20E', 'HKSM'),
  activity DOUBLE
) engine=innodb;

load data local infile '/Users/anushka/BU/starr_query/processed_data/associations.csv'
into table TempAssociations
fields terminated by ','
ignore 1 lines
(enhancer_name, geneid, @imd_vs_20e, @20e_vs_ctrl, @imd_vs_ctrl, exp_condition, activity)
set imd_vs_ctrl = NULLIF(@imd_vs_ctrl, ''),
  imd_vs_20e = NULLIF(@imd_vs_20e, ''),
  20e_vs_ctrl = NULLIF(@20e_vs_ctrl, '');

-- took too long to insert data from Temp table to Associations table so creating indexes
CREATE INDEX idx_enhancer_name ON Enhancers(name);
CREATE INDEX idx_geneid ON Genes(geneid);
SHOW INDEX FROM Enhancers;
SHOW INDEX FROM Genes;

-- checking how long query takes
SELECT COUNT(*)
FROM TempAssociations t
JOIN Enhancers e ON t.enhancer_name = e.name
JOIN Genes g ON t.geneid = g.geneid
limit 100;

-- inserting data
insert into Associations (eid, gid, imd_vs_ctrl, imd_vs_20e, 20e_vs_ctrl, exp_condition, activity, tpm_20e, tpm_imd, tpm_ctrl)
select e.eid, g.gid, t.imd_vs_ctrl, t.imd_vs_20e, t.20e_vs_ctrl, t.exp_condition, t.activity, g.tpm_20e, g.tpm_imd, g.tpm_ctrl
from TempAssociations t join Enhancers e on t.enhancer_name = e.name join Genes g on t.geneid = g.geneid;


select * from Genes;
select * from Enhancers;
select * from Associations;