USE starr_query;

SELECT 
e.eid AS EnhancerID,
e.name AS EnhancerName,
a.imd_vs_ctrl AS IMDvsCTRL_LogFC,
a.cells_20e_vs_ctrl AS Cells20EvsCTRL_LogFC,
a.hksm_vs_20e AS HKSMvs20E_LogFC,
a.costarr_20e_vs_ctrl AS CoSTARR20EvsCTRL_LogFC,
a.activity AS ActivityScore,
a.exp_condition AS ExpCondition,
e.tf_counts AS TFCounts,
e.tbs AS TotalBindingSites
FROM Genes g
JOIN Associations a ON g.gid = a.gid
JOIN Enhancers e ON a.eid = e.eid
WHERE g.symbol = 'CG14626' 
AND a.activity >= 500; 

SELECT 
e.eid AS EnhancerID,
e.name AS EnhancerName,
a.imd_vs_ctrl AS IMDvsCTRL_LogFC,
a.cells_20e_vs_ctrl AS Cells20EvsCTRL_LogFC,
a.hksm_vs_20e AS HKSMvs20E_LogFC,
a.costarr_20e_vs_ctrl AS CoSTARR20EvsCTRL_LogFC,
a.activity AS ActivityScore,
a.exp_condition AS ExpCondition,
e.tf_counts AS TFCounts,
e.tbs AS TotalBindingSites
FROM Genes g
JOIN Associations a ON g.gid = a.gid
JOIN Enhancers e ON a.eid = e.eid
WHERE g.geneid = 'FBgn0000667'
AND a.activity >= 500;

SELECT 
g.symbol AS GeneSymbol,
e.name AS EnhancerID,
g.start AS GeneStart,
g.end AS GeneEnd,
g.immune_process AS ImmuneProcess,
g.time_cluster AS TimeCluster
FROM Enhancers e
JOIN Associations a ON e.eid = a.eid
JOIN Genes g ON a.gid = g.gid
WHERE e.chromosome = 'X' 
AND e.start >= 1052748 
AND e.end <= 1573675; 


SELECT
            e.name AS enhancer_id,
            a.activity AS act_score,
            e.en_length AS en_length,
            g.symbol AS gene_symbol,
            g.geneid AS gene_id,
            a.tpm_ctrl AS tpm_ctrl,
            a.tpm_imd AS tpm_imd,
            a.tpm_20e AS tpm_20e,
            g.immune_process AS immune_process,
            g.time_cluster AS time_cluster
        FROM Enhancers e
        JOIN Associations a ON e.eid = a.eid
        JOIN Genes g ON a.gid = g.gid
        WHERE e.chromosome = '2L'
        AND e.start >= 0
        AND e.end <= 100000;

            SELECT
                e.name AS enhancer_id,
                e.en_length AS en_length,
                e.exp_condition AS exp_condition,
                a.activity AS act_score,
                g.symbol AS gene_symbol,
                g.geneid AS gene_id,
                a.tpm_ctrl AS tpm_ctrl,
                a.tpm_imd AS tpm_imd,
                a.tpm_20e AS tpm_20e,
                g.immune_process AS immune_process,
                g.time_cluster AS time_cluster
            FROM Enhancers e
            JOIN Associations a ON e.eid = a.eid
            JOIN Genes g ON a.gid = g.gid
            WHERE e.chromosome = '2L'
            AND e.start >= 107649
            AND e.end <= 108363;



SELECT e.name as enhancer_id,
       e.en_length AS en_length,
       e.exp_condition AS exp_condition,
       a.activity AS act_score,
       g.symbol AS gene_symbol,
       g.geneid AS gene_id,
       a.tpm_ctrl AS tpm_ctrl,
       a.tpm_imd AS tpm_imd,
       a.tpm_20e AS tpm_20e,
       g.immune_process AS immune_process,
       g.time_cluster AS time_cluster
FROM Enhancers e
JOIN Associations a ON e.eid = a.eid
JOIN Genes g ON g.gid = a.gid
WHERE activity > 400;


            SELECT
                e.name AS enhancer_id,
                e.en_length AS en_length,
                e.hksm_atac AS hksm_atac,
                e.con_atac as con_atac,
                e.accessibility AS accessibility,
                e.chromosome AS chromosome,
                e.start AS estart,
                e.end AS eend,
                e.exp_condition AS exp_condition,
                a.activity AS act_score,
                g.symbol AS gene_symbol,
                g.geneid AS gene_id,
                a.tpm_ctrl AS tpm_ctrl,
                a.tpm_imd AS tpm_imd,
                a.tpm_20e AS tpm_20e,
                g.immune_process AS immune_process,
                g.time_cluster AS time_cluster
            FROM Enhancers e
            JOIN Associations a ON e.eid = a.eid
            JOIN Genes g ON a.gid = g.gid
            WHERE e.chromosome = '2L'
              AND e.start >= 1234566
              AND e.end <= 2345677
            ORDER BY e.name, e.exp_condition, g.symbol


SELECT DISTINCT activity_class FROM Associations WHERE activity_class IS NOT NULL ORDER BY activity_class

SELECT
                e.name AS enhancer_id,
                e.en_length AS en_length,
                a.accessibility AS accessibility,
                e.chromosome AS chromosome,
                e.start AS estart,
                e.end AS eend,
                e.exp_condition AS exp_condition,
                a.activity AS act_score,
                g.symbol AS gene_symbol,
                g.geneid AS gene_id,
                g.tpm_ctrl AS tpm_ctrl,
                g.tpm_imd AS tpm_imd,
                g.tpm_20e AS tpm_20e,
                g.immune_process AS immune_process,
                g.time_cluster AS time_cluster
            FROM Enhancers e
            JOIN Associations a ON e.eid = a.eid
            JOIN Genes g ON a.gid = g.gid
where
    e.name = '2L:10395542-10396127'


SELECT ac.ac_eid            AS enhancer_id,
                       ac.enhancer_name     AS enhancer_name,
                       ac.activity_class    AS activity_class,
                       ac.accessibility     AS accessibility,
                       ac.geneid            AS gene_id,
                       ac.dist_to_enh       AS dist_to_enh,
                       ac.time_cluster      AS time_cluster,
                       ac.broad_immune_role AS broad_immune_role
                FROM Activity_class_info AS ac
                WHERE 1 = 1;

SELECT DISTINCT activity_class FROM Activity_class_info WHERE activity_class IS NOT NULL ORDER BY activity_class;
SELECT DISTINCT accessibility FROM Activity_class_info WHERE accessibility IS NOT NULL ORDER BY accessibility
SELECT DISTINCT broad_immune_role FROM Activity_class_info WHERE broad_immune_role IS NOT NULL ORDER BY broad_immune_role;