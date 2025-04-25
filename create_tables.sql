-- select database
use Team9;
show tables;

-- drop table statements, "child" Associations table first
DROP TABLE IF EXISTS Associations; 
DROP TABLE IF EXISTS Genes;
DROP TABLE IF EXISTS Enhancers;

-- create tables 

CREATE TABLE Enhancers (
eid INTEGER NOT NULL AUTO_INCREMENT, 
name varchar(30),
chromosome VARCHAR(2), 
start INTEGER, 
end INTEGER, 
tf_counts VARCHAR(150),
tbs INTEGER,
PRIMARY KEY (eid), 
INDEX location (chromosome, start, end) 
) engine=innodb;

CREATE TABLE Genes ( 
gid INTEGER NOT NULL AUTO_INCREMENT,
geneid VARCHAR(20),
chromosome VARCHAR(2), 
start INTEGER, 
end INTEGER, 
symbol VARCHAR(20), 
immune_process VARCHAR(50), 
time_cluster ENUM('early_C2','mid_C3','late_C1','late_C4'), 
PRIMARY KEY (gid), 
INDEX location (chromosome, start, end) 
) engine=innodb;

CREATE TABLE Associations (  
eid INTEGER NOT NULL, 
gid INTEGER NOT NULL, 
imd_vs_ctrl DOUBLE,
cells_20e_vs_ctrl DOUBLE,
hksm_vs_20e DOUBLE,
costarr_20e_vs_ctrl DOUBLE,
exp_condition ENUM('Control', '20E', 'HKSM'),
activity DOUBLE, 
PRIMARY KEY (eid, gid, exp_condition), 
FOREIGN KEY (eid) REFERENCES Enhancers (eid) ON UPDATE CASCADE ON DELETE CASCADE, 
FOREIGN KEY (gid) REFERENCES Genes (gid) ON UPDATE CASCADE ON DELETE CASCADE 
) engine=innodb; 


-- loading in data
-- note that empty fields are designated by NULL 

load data local infile 'C:/Users/jkoda/Downloads/enhancer.csv' 
into table Enhancers
fields terminated by ','
ignore 1 lines
(name, chromosome, start, end, @tf_counts, @tbs)
set tf_counts = NULLIF(@tf_counts, ''),
  tbs = NULLIF(@tbs, '');

load data local infile 'C:/Users/jkoda/Downloads/genes.csv'
into table Genes
fields terminated by ','
ignore 1 lines
(geneid, chromosome, start, end, symbol, @immune_process, @time_cluster)
set immune_process = NULLIF(@immune_process, ''),
  time_cluster = NULLIF(@time_cluster, '');


-- for Associations table, need to create a temp table first
-- csv file only has enhancer name and gene id so need to join tables

DROP TABLE IF EXISTS TempAssociations;

CREATE TEMPORARY TABLE TempAssociations (
  enhancer_name VARCHAR(30),
  geneid VARCHAR(20),
  imd_vs_ctrl DOUBLE,
  cells_20e_vs_ctrl DOUBLE,
  hksm_vs_20e DOUBLE,
  costarr_20e_vs_ctrl DOUBLE,
  exp_condition ENUM('Control', '20E', 'HKSM'),
  activity DOUBLE
) engine=innodb;

load data local infile 'C:/Users/jkoda/Downloads/associations.csv'
into table TempAssociations
fields terminated by ','
ignore 1 lines
(enhancer_name, geneid, @imd_vs_ctrl, @cells_20e_vs_ctrl, @hksm_vs_20e, @costarr_20e_vs_ctrl, exp_condition, activity)
set imd_vs_ctrl = NULLIF(@imd_vs_ctrl, ''),
  cells_20e_vs_ctrl = NULLIF(@cells_20e_vs_ctrl, ''),
  hksm_vs_20e = NULLIF(@hksm_vs_20e, ''),
  costarr_20e_vs_ctrl = NULLIF(@costarr_20e_vs_ctrl, '');

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
insert into Associations (eid, gid, imd_vs_ctrl, cells_20e_vs_ctrl, hksm_vs_20e, costarr_20e_vs_ctrl, exp_condition, activity)
select e.eid, g.gid, t.imd_vs_ctrl, t.cells_20e_vs_ctrl, t.hksm_vs_20e, t.costarr_20e_vs_ctrl, t.exp_condition, t.activity
from TempAssociations t join Enhancers e on t.enhancer_name = e.name join Genes g on t.geneid = g.geneid;


select * from Genes;
select * from Enhancers;
select * from Associations