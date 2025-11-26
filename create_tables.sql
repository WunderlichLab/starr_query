

-- drop table statements, "child" Associations table first
DROP TABLE IF EXISTS Associations;
DROP TABLE IF EXISTS Genes;
DROP TABLE IF EXISTS Enhancers;


-- create tables
CREATE TABLE Enhancers (
eid INTEGER NOT NULL AUTO_INCREMENT,
name VARCHAR(30),
chromosome VARCHAR(2),
start INTEGER,
end INTEGER,
en_length INTEGER,
exp_condition ENUM('Control','20E','IMD'),
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
symbol VARCHAR(20),
immune_process VARCHAR(50),
time_cluster ENUM('early_C2','mid_C3','late_C1','late_C4'),
gene_length INTEGER,
tpm_ctrl DOUBLE,
tpm_20e DOUBLE,
tpm_imd DOUBLE,
PRIMARY KEY (gid),
INDEX location (chromosome, start, end)
) ENGINE=innodb;

CREATE TABLE Associations (
eid INTEGER NOT NULL,
gid INTEGER NOT NULL,
imd_vs_20e DOUBLE,
20e_vs_ctrl DOUBLE,
imd_vs_ctrl DOUBLE,
exp_condition ENUM('Control', '20E', 'IMD'),
activity DOUBLE,
accessibility VARCHAR(30),
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
(name, chromosome, start, end, en_length, exp_condition,
 @tf_counts, @tbs)
SET
  tf_counts     = NULLIF(@tf_counts, ''),
  tbs           = NULLIF(@tbs, '');

LOAD DATA LOCAL INFILE '/Users/anushka/BU/starr_query/processed_data/genes.csv'
INTO TABLE Genes
FIELDS TERMINATED BY ','
IGNORE 1 LINES
(geneid, chromosome, start, end, symbol, @immune_process, @time_cluster, gene_length, tpm_ctrl, tpm_20e, tpm_imd)
SET immune_process = NULLIF(@immune_process, ''),
  time_cluster = NULLIF(@time_cluster, '');

-- for Associations table, need to create a temp table first
-- csv file has enhancer name and gene id so need to join tables

DROP TABLE IF EXISTS TempAssociations;

CREATE TEMPORARY TABLE TempAssociations (
  enhancer_name VARCHAR(30),
  geneid VARCHAR(20),
  imd_vs_20e DOUBLE,
  20e_vs_ctrl DOUBLE,
  imd_vs_ctrl DOUBLE,
  exp_condition ENUM('Control', '20E', 'IMD'),
  activity DOUBLE,
  accessibility VARCHAR(30)
) ENGINE=innodb;

LOAD DATA LOCAL INFILE '/Users/anushka/BU/starr_query/processed_data/associations.csv'
INTO TABLE TempAssociations
FIELDS TERMINATED BY ','
IGNORE 1 LINES
(enhancer_name, geneid, @imd_vs_20e, @20e_vs_ctrl, @imd_vs_ctrl, exp_condition, activity, accessibility)
SET
  imd_vs_ctrl = NULLIF(@imd_vs_ctrl, ''),
  imd_vs_20e = NULLIF(@imd_vs_20e, ''),
  20e_vs_ctrl = NULLIF(@20e_vs_ctrl, '');

-- create indexes to speed up joins
CREATE INDEX idx_enhancer_name ON Enhancers(name);
CREATE INDEX idx_geneid ON Genes(geneid);

-- verify indexes were created
SHOW INDEX FROM Enhancers;
SHOW INDEX FROM Genes;

-- test query to check performance
SELECT COUNT(*)
FROM TempAssociations t
JOIN Enhancers e ON t.enhancer_name = e.name
JOIN Genes g ON t.geneid = g.geneid
LIMIT 100;

-- insert data from temp table to Associations table
INSERT INTO Associations (eid, gid, imd_vs_ctrl, imd_vs_20e, 20e_vs_ctrl, exp_condition, activity, accessibility)
SELECT e.eid, g.gid, t.imd_vs_ctrl, t.imd_vs_20e, t.`20e_vs_ctrl`, t.exp_condition, t.activity, t.accessibility
FROM TempAssociations t
JOIN Enhancers e ON t.enhancer_name = e.name
JOIN Genes g ON t.geneid = g.geneid;


-- verify data loaded successfully
SELECT COUNT(*) as num_genes FROM Genes;
SELECT COUNT(*) as num_enhancers FROM Enhancers;
SELECT COUNT(*) as num_associations FROM Associations;

-- check sample data
SELECT * FROM Genes LIMIT 5;
SELECT * FROM Enhancers LIMIT 5;
SELECT * FROM Associations LIMIT 5;