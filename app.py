#!/usr/bin/env python3
from flask import Flask, render_template, request
import mariadb
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def connect_db():
    connection = mariadb.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
    )
    return connection

## Tab 1

def get_genes_by_enhancer(chr, start, end):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
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
            WHERE e.chromosome = %s
            AND e.start >= %s
            AND e.end <= %s
        """

        cursor.execute(query, (chr, start, end))
        rows = cursor.fetchall()

        rows = list(set(rows))

        enhancer_dict = {}
        for row in rows:
            (
                enhancer_id,
                en_length,
                exp_condition,
                act_score,
                gene_symbol,
                gene_id,
                tpm_ctrl,
                tpm_imd,
                tpm_20e,
                immune_process,
                time_cluster
            ) = row

            if enhancer_id not in enhancer_dict:
                enhancer_dict[enhancer_id] = {
                    'enhancer_id': enhancer_id,
                    'en_length': en_length,
                    'act_score': act_score,
                    'exp_condition': exp_condition,
                    'gene_interactions': []
                }

            enhancer_dict[enhancer_id]['gene_interactions'].append({
                'gene_symbol': gene_symbol or gene_id,
                'tpm_ctrl': tpm_ctrl,
                'tpm_imd': tpm_imd,
                'tpm_20e': tpm_20e,
                'immune_process': immune_process,
                'time_cluster': time_cluster
            })

        # {'2L:484243-485063': {'enhancer_id': '2L:484243-485063', 'en_length': 820, 'act_score': 0.0, 'exp_condition': 'IMD', 'immune_process': None, 'time_cluster': None,
        # 'gene_interactions': [{'gene_symbol': 'lncRNA:CR46258', 'gene_id': 'FBgn0267991', 'tpm_ctrl': 1.95097, 'tpm_imd': 0.30911, 'tpm_20e': 1.08807},
        # {'gene_symbol': 'MED15', 'gene_id': 'FBgn0027592', 'tpm_ctrl': 99.10049, 'tpm_imd': 70.32382, 'tpm_20e': 100.93579},
        # {'gene_symbol': 'ush', 'gene_id': 'FBgn0003963', 'tpm_ctrl': 41.77297, 'tpm_imd': 18.94429, 'tpm_20e': 33.82258},
        # {'gene_symbol': 'cbt', 'gene_id': 'FBgn0043364', 'tpm_ctrl': 78.24543, 'tpm_imd': 32.20612, 'tpm_20e': 48.50113},
        # {'gene_symbol': 'CG4297', 'gene_id': 'FBgn0031258', 'tpm_ctrl': 13.5922, 'tpm_imd': 2.315, 'tpm_20e': 6.39681}]},
        # '2L:484243-485251': {'enhancer_id': '2L:484243-485251', 'en_length': 1008, 'act_score': 1240.48, 'exp_condition': '20E', 'immune_process': None, 'time_cluster': None,
        # 'gene_interactions': [{'gene_symbol': 'lncRNA:CR46258', 'gene_id': 'FBgn0267991', 'tpm_ctrl': 1.95097, 'tpm_imd': 0.30911, 'tpm_20e': 1.08807},
        # {'gene_symbol': 'MED15', 'gene_id': 'FBgn0027592', 'tpm_ctrl': 99.10049, 'tpm_imd': 70.32382, 'tpm_20e': 100.93579},
        # {'gene_symbol': 'ush', 'gene_id': 'FBgn0003963', 'tpm_ctrl': 41.77297, 'tpm_imd': 18.94429, 'tpm_20e': 33.82258},
        # {'gene_symbol': 'cbt', 'gene_id': 'FBgn0043364', 'tpm_ctrl': 78.24543, 'tpm_imd': 32.20612, 'tpm_20e': 48.50113},
        # {'gene_symbol': 'CG4297', 'gene_id': 'FBgn0031258', 'tpm_ctrl': 13.5922, 'tpm_imd': 2.315, 'tpm_20e': 6.39681}]}}
        conn.close()

        # convert dict to list for template
        return list(enhancer_dict.values())


    except mariadb.Error as e:
        print(f"Database error: {e}")
        return []


## Tab 2
def get_enhancers_by_gene(symbol=None, geneid=None, activity_score=500):
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT
            e.name AS enhancer_name,
            e.en_length AS en_length,
            a.activity AS act_score,
            a.exp_condition AS exp_condition,
            g.symbol AS gene_symbol,
            g.geneid AS gene_id,
            g.tpm_ctrl AS tpm_ctrl,
            g.tpm_imd AS tpm_imd,
            g.tpm_20e AS tpm_20e,
            e.chromosome AS chromosome,
            e.start AS start,
            e.end AS end
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
            return []

        cursor.execute(query, params)
        result = cursor.fetchall()

        conn.close()
        return result

    except mariadb.Error as e:
        print(f"Error connecting/querying database: {e}")
        return []

'''def get_enhancers_by_range(chr, start, end):
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT
            e.name AS enhancer_name,
            e.en_length AS en_length,
            a.activity AS act_score,
            a.exp_condition AS exp_condition,
            g.symbol AS gene_symbol,
            g.geneid AS gene_id,
            g.tpm_ctrl AS tpm_ctrl,
            g.tpm_imd AS tpm_imd,
            g.tpm_20e AS tpm_20e,
            g.chromosome AS chromosome,
            g.start AS start,
            g.end AS end
        FROM Enhancers e
        JOIN Associations a ON e.eid = a.eid
        JOIN Genes g ON a.gid = g.gid
        WHERE g.chromosome = %s
          AND g.start >= %s
          AND g.end <= %s
        """

        cursor.execute(query, (chr, start, end))
        result = cursor.fetchall()

        conn.close()
        return result

    except mariadb.Error as e:
        print(f"Error connecting/querying database: {e}")
        return []'''

'''def get_gene_symbol_by_geneid(geneid):
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
        return None'''


@app.route('/')
def index():
    return render_template('template.html')

@app.route('/submit_enhancer', methods=['POST'])
def find_gene():
    chr = request.form['chr']
    start = int(request.form['start'])
    end = int(request.form['end'])
    enhancers = get_genes_by_enhancer(chr, start, end)

    return render_template('tab_1.html', enhancers=enhancers)


@app.route('/submit_gene', methods=['POST'])
def find_enhancer():
    # 1) pull inputs
    symbol    = request.form.get("symbol","").strip()
    geneid    = request.form.get("geneid","").strip()
    activity_score = float(request.form.get("activity_score", 500))
    condition = request.form.get("condition","").strip().lower()
    '''chrom     = request.form.get("chr","").strip()
        start_str = request.form.get("start","").strip()
        end_str   = request.form.get("end","").strip()'''

    # 2) detect modes
    has_gene   = bool(symbol or geneid)

    if not (has_gene):
        return render_template(
            'tab_2.html',
            enhancers=[],
            chart_data=[["Activity Score"]],
            error_message=(
              "Please specify either a gene (symbol or gene_id) "
            )
        )

    ''' if not (has_gene or has_region):
        return render_template(
            'tab_2.html',
            enhancers=[],
            chart_data=[["Activity Score"]],
            error_message=(
              "Please specify either a gene (symbol or gene_id) "
              "or a chromosomal region (chr+start+end)."
            )
        )'''

    # 3) fetch
    gene_enhancers = get_enhancers_by_gene(symbol or None, geneid or None, activity_score) if has_gene else []
    '''region_enhancers = get_enhancers_by_range(chrom, int(start_str), int(end_str)) if has_region else []'''

    '''# 4) combine
    if has_gene and has_region:
        gene_names   = {e["enhancer_name"] for e in gene_enhancers}
        region_names = {e["enhancer_name"] for e in region_enhancers}
        keep = gene_names & region_names
        final_list = [e for e in gene_enhancers if e["enhancer_name"] in keep]
    elif has_gene:
        final_list = gene_enhancers
    else:
        final_list = region_enhancers'''
    # Gene enhancers looks like this:
    # {'enhancer_name': '3R:16986049-16986948', 'en_length': 899, 'act_score': 1247.73, 'exp_condition': '20E',
    # 'gene_symbol': 'Abd-B', 'gene_id': 'FBgn0000015', 'tpm_ctrl': 0.026, 'tpm_imd': 0.03749, 'tpm_20e': 0.03821,
    # 'chromosome': '3R', 'start': 16986049, 'end': 16986948}

    # 5) filter by condition
    if condition:
        final_list = [e for e in gene_enhancers if e["exp_condition"].strip().lower() == condition]
    else:
        final_list = gene_enhancers

    # 6) build chart data
    chart_data = [["Activity Score", "Enhancer Name", "Condition"]]
    for rec in final_list:
        chart_data.append([rec["act_score"], rec["enhancer_name"], rec["exp_condition"]])

    return render_template(
        'tab_2.html',
        enhancers=final_list,
        chart_data=chart_data,
        error_message=""
    )

if __name__ == '__main__':
    app.run(debug=True)
