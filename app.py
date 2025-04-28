#!/usr/bin/env python3

from flask import Flask, render_template, request
from datetime import datetime, date
import mariadb

app = Flask(__name__)

def connect_db():
    #connect to database on host
    connection = mariadb.connect(
        host = "bioed-new.bu.edu",
        user = "yuki",
        password = "yukiito914",
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
            e.tbs AS TotalBindingSites,
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
    symbol = request.form.get('symbol')
    geneid = request.form.get('geneid')
    activity_score = request.form.get('activity_score')

    if activity_score is None or activity_score == "":
        activity_score = 500  # default value
    else:
        activity_score = int(activity_score)

    enhancers = get_enhancers_by_gene(symbol, geneid, activity_score)

    enhancers_parsed = []
    for e in enhancers:
        chrom, start, end = parse_enhancer_id(e[0])  # e[0] = eid
        enhancers_parsed.append(e + (chrom, start, end))

    return render_template('find_enhancer_results.html', enhancers=enhancers_parsed)


if __name__ == '__main__':
    app.run(debug=True)
