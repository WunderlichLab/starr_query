#!/usr/bin/env python3

from flask import Flask, render_template, request
from datetime import datetime, date
import mariadb

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
        SELECT g.symbol AS GeneSymbol, e.name AS EnhancerID, g.start AS GeneStart, g.end AS GeneEnd, g.immune_process AS ImmuneProcess, g.time_cluster AS TimeCluster
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
        WHERE chromosome = %s
          AND start >= %s
          AND end <= %s
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


def parse_enhancer_id(eid):
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
    symbol = request.form.get("symbol", "").strip()
    geneid = request.form.get("geneid", "").strip()
    chr = request.form['chr']
    start = int(request.form['start'])
    end = int(request.form['end'])
    activity_score = request.form.get("activity_score", type=float, default=0)
    condition = request.form.get("condition", "").strip()

    error_message = ""
    all_enhancers = {}
    enhancers_parsed = []
    histogram_scores = []

    try:
        if not (0 <= activity_score_threshold <= 1000):
            error_message = "Activity score threshold must be between 0 and 1000."
    except ValueError:
        error_message = "Invalid activity score input."

    if not ((gene_symbol or gene_id) or (chr and start is not None and end is not None)):
        error_message = "You must enter either gene symbol/ID or a chromosome range to query enhancer data."

    if error_message:
        return render_template('find_enhancer_results.html', enhancers=[], chart_data=json.dumps([["Activity Score"]]), error_message=error_message)

    if symbol or geneid:
        gene_enhancers = get_enhancers_by_gene(symbol or None, geneid or None, activity_score=0)
        for e in gene_enhancers:
            chrom, start_pos, end_pos = parse_enhancer_name(e[1])
            all_enhancers[e[0]] = {
                "EnhancerID": e[0],
                "EnhancerName": e[1],
                "ActivityScore": e[6],
                "ExpCondition": e[7],
                "Chromosome": chrom,
                "Start": int(start_pos),
                "End": int(end_pos)
            }

    if chr and start is not None and end is not None:
        region_enhancers = get_enhancers_by_range(chr, start, end)
        region_eids = set(e[0] for e in region_enhancers)

        if not all_enhancers:
            for e in region_enhancers:
                chrom, start_pos, end_pos = parse_enhancer_name(e[1])
                all_enhancers[e[0]] = {
                    "EnhancerID": e[0],
                    "EnhancerName": e[1],
                    "ActivityScore": e[6],
                    "ExpCondition": e[7],
                    "Chromosome": chrom,
                    "Start": int(start_pos),
                    "End": int(end_pos)
                }
        else: # Take the inner join from both filters
            all_enhancers = {eid: data for eid, data in all_enhancers.items() if eid in region_eids}

    if not all_enhancers:
        return render_template('find_enhancer_results.html', enhancers=[], chart_data=json.dumps([["Activity Score"]]), error_message="No enhancers found matching criteria.")

    for eid, data in all_enhancers.items():
        score = data.get("ActivityScore")
        exp_condition = data.get("ExpCondition", "")

        if score is not None and score < activity_score_threshold:
            continue
        if condition:
            if not exp_condition or exp_condition.lower() != condition.lower():
                continue

        enhancers_parsed.append(data)

        if condition and score is not None:
            histogram_scores.append([float(score)])

    chart_data = [["Activity Score"]]
    if condition and histogram_scores:
        chart_data += histogram_scores

    return render_template(
        'find_enhancer_results.html',
        enhancers=enhancers_parsed,
        chart_data=json.dumps(chart_data),
        error_message=""
    )


if __name__ == '__main__':
    app.run(debug=True)
