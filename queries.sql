USE Team9;

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
WHERE g.symbol = 'CG14626' # Input is gene symbol
AND a.activity >= 500; # activity score filter

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
WHERE g.geneid = 'FBgn0000667' # Input is FB gene id
AND a.activity >= 500; # activity score filter

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
WHERE e.chromosome = 'X' # Chr input
AND e.start >= 1052748 # start
AND e.end <= 1573675; # end
