-- select database
USE starr_query;
SHOW tables;

DROP TABLE IF EXISTS Activity_class_info;

CREATE TABLE Activity_class_info (
    ac_eid INTEGER NOT NULL AUTO_INCREMENT,
    enhancer_name VARCHAR(30),
    activity_class ENUM('Control','20E','HKSM','Control + 20E','Control + HKSM','HKSM + 20E', 'Constitutive'),
    accessibility ENUM('Always open','Always closed','HKSM closed','HKSM opened'),
    geneid VARCHAR(30),
    dist_to_enh INTEGER,
    time_cluster VARCHAR(30),
    broad_immune_role VARCHAR(30),
    PRIMARY KEY (ac_eid)
) ENGINE=innodb;


-- For activity class info table
-- Load data into temporary table
LOAD DATA LOCAL INFILE '/Users/anushka/BU/starr_query/processed_data/tab3_data.csv'
INTO TABLE Activity_class_info
FIELDS TERMINATED BY ','
IGNORE 1 LINES
(enhancer_name, activity_class, accessibility, geneid, @dist_to_enh, @time_cluster, @broad_immune_role)
SET
  dist_to_enh = NULLIF(@dist_to_enh, ''),
  time_cluster = NULLIF(@time_cluster, ''),
  broad_immune_role = NULLIF(@broad_immune_role, '');

ALTER TABLE Activity_class_info
ADD gene_symbol VARCHAR(30);

UPDATE Activity_class_info AS ac
INNER JOIN Genes AS g ON ac.geneid = g.geneid
SET ac.gene_symbol = g.symbol;