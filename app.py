#!/usr/bin/env python3

from flask import Flask, render_template, request
import json
import mariadb
from flask import jsonify

app = Flask(__name__)

def connect_db():
    #connect to database on host
    connection = mariadb.connect(
        host = "bioed-new.bu.edu",
        user = "garytwu",
        password = "cinderella",
        database = "Team9",
        port = 4253
    )
    return connection

def get_genes_by_enhancer(chr, start, end):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
        SELECT g.symbol AS GeneSymbol, g.geneid AS GeneID, e.name AS EnhancerID, g.start AS GeneStart, g.end AS GeneEnd, g.immune_process AS ImmuneProcess, g.time_cluster AS TimeCluster
        FROM Enhancers e
        JOIN Associations a ON e.eid = a.eid
        JOIN Genes g ON a.gid = g.gid
        WHERE e.chromosome = %s
        AND e.start >= %s
        AND e.end <= %s
        """
        try:
            cursor.execute(query, (chr, start, end))
            result = cursor.fetchall()

        except mariadb.Error as e:
            # error handling for query execution
            print(f"Error executing query: {e}")
            result = []  # return an empty list if there is an error

        conn.close()
        return result

    except mariadb.Error as e:
        # error handling for connection
        print(f"Error connecting to the database: {e}")
        return []

def get_enhancers_by_range(chr, start, end):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
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
        FROM Enhancers e
        JOIN Associations a ON e.eid = a.eid
        WHERE e.chromosome = %s
          AND e.start >= %s
          AND e.end <= %s
        """

        try:
            cursor.execute(query, (chr, start, end))
            result = cursor.fetchall()

        except mariadb.Error as e:
            # error handling for query execution
            print(f"Error executing query: {e}")
            result = []  # return an empty list if there is an error

        conn.close()
        return result

    except mariadb.Error as e:
        print(f"Error connecting to the database: {e}")
        return []

def get_enhancers_by_gene(symbol=None, geneid=None, activity_score=500):

    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
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
        WHERE a.activity >= %s
        """

        params = [activity_score]

        if symbol:
            query += " AND g.symbol = %s"
            params.append(symbol)
        elif geneid:
            query += " AND g.geneid = %s"
            params.append(geneid)
        else:
            return "Please input either symbol or geneid."

        try:
            cursor.execute(query, params)
            result = cursor.fetchall()

        except mariadb.Error as e:
            # error handling for query execution
            print(f"Error executing query: {e}")
            result = []  # return an empty list if there is an error

        conn.close()
        return result

    except mariadb.Error as e:
        # error handling for connection
        print(f"Error connecting to the database: {e}")
        return []

def get_gene_symbol_by_geneid(geneid):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = "SELECT symbol FROM Genes WHERE gid = %s"
        cursor.execute(query, (geneid,))
        result = cursor.fetchone()

        conn.close()
        if result:
            return result[0]  # symbol
        else:
            return None
    except mariadb.Error as e:
        print(f"Error fetching gene symbol: {e}")
        return None


def parse_enhancer_name(eid):
    # e.g. 2L:10426653-10427192(+)
    try:
        chrom_part, rest = eid.split(':')
        start, rest2 = rest.split('-')
        end = rest2.split('(')[0]
        return chrom_part, start, end
    except Exception as e:
        print(f"Error parsing eid {eid}: {e}")
        return None, None, None


@app.route('/')
def home():
    return render_template('template.html')

@app.route('/submit_enhancer', methods=['POST'])
def find_gene():
    chr = request.form['chr']
    start = int(request.form['start'])
    end = int(request.form['end'])
    genes = get_genes_by_enhancer(chr, start, end)

    return render_template('find_gene_results.html', genes=genes)

@app.route('/submit_gene', methods=['POST'])
def find_enhancer():
    # 1) pull inputs
    symbol    = request.form.get("symbol","").strip()
    geneid    = request.form.get("geneid","").strip()
    chrom     = request.form.get("chr","").strip()
    start_str = request.form.get("start","").strip()
    end_str   = request.form.get("end","").strip()
    activity_score = int(request.form.get("activity_score", 500))
    condition = request.form.get("condition","").strip().lower()

    # 2) detect modes
    has_gene   = bool(symbol or geneid)
    has_region = bool(chrom and start_str and end_str)

    # 3) require at least one
    if not (has_gene or has_region):
        return render_template('find_enhancer_results.html',
            enhancers=[],
            chart_data=[["Activity Score"]],
            error_message=(
              "Please specify either a gene (symbol or gene_id) "
              "or a chromosomal region (chr+start+end)."
            )
        )

    # 4) fetch by gene
    gene_enhancers = []
    if has_gene:
        gene_enhancers = get_enhancers_by_gene(
            symbol or None, geneid or None, activity_score
        )

    # 5) fetch by region
    region_enhancers = []
    if has_region:
        start = int(start_str); end = int(end_str)
        region_enhancers = get_enhancers_by_range(chrom, start, end)

    # 6) combine: inner‐join if both, else whichever list exists
    if has_gene and has_region:
        gene_eids   = {e[0] for e in gene_enhancers}
        region_eids = {e[0] for e in region_enhancers}
        keep = gene_eids & region_eids
        final_list = [e for e in gene_enhancers if e[0] in keep]
    elif has_gene:
        final_list = gene_enhancers
    else:
        final_list = region_enhancers

    # 7) (parse eid, filter by condition, build histogram data…)
    enhancers_parsed = []
    for e in final_list:
        chrom, start_str, end_str = parse_enhancer_name(e[1])
        enhancers_parsed.append({
            "EnhancerID":      e[0],
            "EnhancerName":    e[1],
            "ActivityScore":   e[6],
            "ExpCondition":    e[7],
            "Chromosome":      chrom,
            "Start":           int(start_str),
            "End":             int(end_str),
        })

    chart_data = [["Activity Score"]]
    for rec in enhancers_parsed:
        chart_data.append([ rec["ActivityScore"] ])

    return render_template(
        'find_enhancer_results.html',
        enhancers=enhancers_parsed,
        chart_data=chart_data,
        error_message=""
    )

if __name__ == '__main__':
    app.run(debug=True, port=5002)
