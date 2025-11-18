#!/usr/bin/env python3

from flask import Flask, render_template, request
import mariadb
import os
from dotenv import load_dotenv
from collections import namedtuple

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
def associations_by_region(chr, start, end, activity_score_min=0, exp_condition=None,
                          time_cluster=None, immune_process=None):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
            SELECT
                e.name AS enhancer_id,
                e.en_length AS en_length,
                a.accessibility AS accessibility,
                e.chromosome AS chromosome,
                e.start AS estart,
                e.end AS eend,
                a.exp_condition AS exp_condition,
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
            WHERE e.chromosome = %s
              AND e.start >= %s
              AND e.end <= %s
              AND a.activity >= %s
        """

        params = [chr, start, end, activity_score_min]

        if exp_condition:
            query += " AND a.exp_condition = %s"
            params.append(exp_condition)

        if time_cluster:
            query += " AND g.time_cluster = %s"
            params.append(time_cluster)

        if immune_process:
            query += " AND g.immune_process = %s"
            params.append(immune_process)

        query += " ORDER BY e.name, a.exp_condition, g.symbol"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Remove duplicates while preserving order
        seen = set()
        unique_rows = []
        for row in rows:
            if row not in seen:
                seen.add(row)
                unique_rows.append(row)

        enhancer_map = {}

        Enhancer = namedtuple('Enhancer', ['enhancer_id', 'en_length', 'chromosome', 'window_start', 'window_end', 'conditions'])
        Condition = namedtuple('Condition', ['exp_condition', 'activity', 'genes'])
        Gene = namedtuple('Gene', ['gene_symbol','gene_id', 'accessibility', 'tpm_ctrl', 'tpm_imd', 'tpm_20e', 'immune_process', 'time_cluster'])

        for row in unique_rows:
            (enhancer_id, en_length, accessibility,
             chrom, estart, eend,
             exp_condition, act_score, gene_symbol, gene_id,
             tpm_ctrl, tpm_imd, tpm_20e, immune_process, time_cluster
             ) = row

            window_start = max(0, estart - 5000)
            window_end = eend + 5000

            if enhancer_id not in enhancer_map:
                enhancer_map[enhancer_id] = {
                    'enhancer_id': enhancer_id,
                    'en_length': en_length,
                    'chromosome': chrom,
                    'window_start': window_start,
                    'window_end': window_end,
                    'conditions': {}
                }

            if exp_condition not in enhancer_map[enhancer_id]['conditions']:
                enhancer_map[enhancer_id]['conditions'][exp_condition] = {
                    'exp_condition': exp_condition,
                    'activity': act_score,
                    'genes': []
                }

            gene_obj = Gene(
                gene_symbol=gene_symbol,
                gene_id=gene_id,
                accessibility=accessibility,
                tpm_ctrl=tpm_ctrl,
                tpm_imd=tpm_imd,
                tpm_20e=tpm_20e,
                immune_process=immune_process,
                time_cluster=time_cluster
            )

            if gene_obj not in enhancer_map[enhancer_id]['conditions'][exp_condition]['genes']:
                enhancer_map[enhancer_id]['conditions'][exp_condition]['genes'].append(gene_obj)

        enhancers_details = []
        for enhancer_id in sorted(enhancer_map.keys()):
            enhancer_info = enhancer_map[enhancer_id]

            conditions_list = []
            for condition_name in sorted(enhancer_info['conditions'].keys()):
                condition_info = enhancer_info['conditions'][condition_name]
                c_tup = Condition(
                    exp_condition=condition_info['exp_condition'],
                    activity=condition_info['activity'],
                    genes=condition_info['genes']
                )
                conditions_list.append(c_tup)

            e_tup = Enhancer(
                enhancer_id=enhancer_info['enhancer_id'],
                en_length=enhancer_info['en_length'],
                chromosome=enhancer_info['chromosome'],
                window_start = enhancer_info['window_start'],
                window_end = enhancer_info['window_end'],
                conditions=conditions_list
            )
            enhancers_details.append(e_tup)

        conn.close()
        return enhancers_details

    except mariadb.Error as e:
        print(f"Database error: {e}")
        return []



## Tab 2
def associations_by_symbol(symbol=None, geneid=None, activity_score=500, exp_condition=None,
                          time_cluster=None, immune_process=None):
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT DISTINCT
            e.name AS enhancer_id,
            e.en_length AS en_length,
            a.accessibility as accessibility,
            a.dist_to_enh as dist_to_enh,
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

        if exp_condition:
            query += " AND a.exp_condition = %s"
            params.append(exp_condition)

        if time_cluster:
            query += " AND g.time_cluster = %s"
            params.append(time_cluster)

        if immune_process:
            query += " AND g.immune_process = %s"
            params.append(immune_process)

        query += " ORDER BY e.name, a.exp_condition"

        cursor.execute(query, params)
        result = cursor.fetchall()

        conn.close()
        return result

    except mariadb.Error as e:
        print(f"Error connecting/querying database: {e}")
        return []



## Tab 3
def get_activity_class_options():
    """Fetch unique activity classes, conditions, time clusters, and immune processes from database"""
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Get unique activity classes
        cursor.execute(
            "SELECT DISTINCT activity_class FROM Associations WHERE activity_class IS NOT NULL ORDER BY activity_class")
        activity_classes = [row[0] for row in cursor.fetchall()]

        # Get unique conditions
        cursor.execute("SELECT DISTINCT accessibility FROM Associations ORDER BY accessibility")
        conditions = [row[0] for row in cursor.fetchall()]

        # Get unique time clusters
        cursor.execute("SELECT DISTINCT time_cluster FROM Genes WHERE time_cluster IS NOT NULL ORDER BY time_cluster")
        time_clusters = [row[0] for row in cursor.fetchall()]

        # Get unique immune processes
        cursor.execute(
            "SELECT DISTINCT immune_process FROM Genes WHERE immune_process IS NOT NULL ORDER BY immune_process")
        immune_processes = [row[0] for row in cursor.fetchall()]

        conn.close()
        return {
            'activity_classes': activity_classes,
            'conditions': conditions,
            'time_clusters': time_clusters,
            'immune_processes': immune_processes
        }

    except mariadb.Error as e:
        print(f"Error fetching filter options: {e}")
        return {
            'activity_classes': [],
            'conditions': [],
            'time_clusters': [],
            'immune_processes': []
        }


def search_by_activity_class(activity_class=None, condition=None, activity_score_min=0,
                             time_cluster=None, immune_process=None):
    """Search enhancers by activity class and additional filters"""
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
                SELECT e.name           AS enhancer_id, 
                       e.en_length      AS en_length, 
                       a.accessibility  AS accessibility, 
                       e.chromosome     AS chromosome, 
                       e.start          AS estart, 
                       e.end            AS eend, 
                       a.activity       AS act_score, 
                       a.activity_class AS activity_class, 
                       a.exp_condition  AS exp_condition, 
                       g.symbol         AS gene_symbol, 
                       g.geneid         AS gene_id, 
                       g.tpm_ctrl       AS tpm_ctrl, 
                       g.tpm_imd        AS tpm_imd, 
                       g.tpm_20e        AS tpm_20e, 
                       g.immune_process AS immune_process, 
                       g.time_cluster   AS time_cluster
                FROM Enhancers e
                         JOIN Associations a ON e.eid = a.eid
                         JOIN Genes g ON a.gid = g.gid
                WHERE 1 = 1
                """

        params = []

        if activity_class:
            query += " AND a.activity_class = %s"
            params.append(activity_class)

        if condition:
            query += " AND a.accessibility = %s"
            params.append(condition)

        if time_cluster:
            query += " AND g.time_cluster = %s"
            params.append(time_cluster)

        if immune_process:
            query += " AND g.immune_process = %s"
            params.append(immune_process)

        query += " ORDER BY e.name, a.exp_condition, g.symbol"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Remove duplicates while preserving order
        seen = set()
        unique_rows = []
        for row in rows:
            if row not in seen:
                seen.add(row)
                unique_rows.append(row)

        # Structure data similar to Tab 1
        enhancer_map = {}

        Enhancer = namedtuple('Enhancer', ['enhancer_id', 'en_length',
                                           'chromosome', 'window_start', 'window_end', 'conditions'])
        Condition = namedtuple('Condition', ['exp_condition',
                                             'activity_class', 'genes'])
        Gene = namedtuple('Gene', ['gene_symbol', 'gene_id', 'accessibility',
                                   'tpm_ctrl', 'tpm_imd', 'tpm_20e',
                                   'immune_process', 'time_cluster'])

        for row in unique_rows:
            (enhancer_id, en_length, accessibility, chrom, estart, eend,
             act_score, act_class, exp_condition, gene_symbol, gene_id, tpm_ctrl, tpm_imd,
             tpm_20e, immune_process, time_cluster) = row

            window_start = max(0, estart - 5000)
            window_end = eend + 5000

            if enhancer_id not in enhancer_map:
                enhancer_map[enhancer_id] = {
                    'enhancer_id': enhancer_id,
                    'en_length': en_length,
                    'chromosome': chrom,
                    'window_start': window_start,
                    'window_end': window_end,
                    'conditions': {}
                }

            condition_key = f"{exp_condition}_{act_class}"
            if condition_key not in enhancer_map[enhancer_id]['conditions']:
                enhancer_map[enhancer_id]['conditions'][condition_key] = {
                    'exp_condition': exp_condition,
                    'activity': act_score,
                    'activity_class': act_class,
                    'genes': []
                }

            gene_obj = Gene(
                gene_symbol=gene_symbol,
                gene_id=gene_id,
                accessibility=accessibility,
                tpm_ctrl=tpm_ctrl,
                tpm_imd=tpm_imd,
                tpm_20e=tpm_20e,
                immune_process=immune_process,
                time_cluster=time_cluster
            )

            if gene_obj not in enhancer_map[enhancer_id]['conditions'][condition_key]['genes']:
                enhancer_map[enhancer_id]['conditions'][condition_key]['genes'].append(gene_obj)

        enhancers_details = []
        for enhancer_id in sorted(enhancer_map.keys()):
            enhancer_info = enhancer_map[enhancer_id]

            conditions_list = []
            for condition_key in sorted(enhancer_info['conditions'].keys()):
                condition_info = enhancer_info['conditions'][condition_key]
                c_tup = Condition(
                    exp_condition=condition_info['exp_condition'],
                    activity_class=condition_info['activity_class'],
                    genes=condition_info['genes']
                )
                conditions_list.append(c_tup)

            e_tup = Enhancer(
                enhancer_id=enhancer_info['enhancer_id'],
                en_length=enhancer_info['en_length'],
                chromosome=enhancer_info['chromosome'],
                window_start=enhancer_info['window_start'],
                window_end=enhancer_info['window_end'],
                conditions=conditions_list
            )
            enhancers_details.append(e_tup)

        conn.close()
        return enhancers_details

    except mariadb.Error as e:
        print(f"Database error: {e}")
        return []


## Tab 0
@app.route('/')
def index():
    filter_options = get_activity_class_options()
    return render_template('template.html', filter_options=filter_options, request=request)

## Tab 1
@app.route('/submit_region', methods=['POST'])
def find_gene():
    chr = request.form['chr']
    start = int(request.form['start'])
    end = int(request.form['end'])
    activity_score_min = float(request.form.get("activity_score_min", 0))
    exp_condition = request.form.get("condition", "").strip() or None
    time_cluster = request.form.get("time_cluster", "").strip() or None
    immune_process = request.form.get("immune_process", "").strip() or None

    enhancers = associations_by_region(chr, start, end, activity_score_min,
                                       exp_condition, time_cluster, immune_process)

    return render_template('tab_1.html', enhancers=enhancers)


## Tab 2
@app.route('/submit_gene', methods=['POST'])
def find_enhancer():
    symbol    = request.form.get("symbol","").strip()
    geneid    = request.form.get("geneid","").strip()
    activity_score = float(request.form.get("activity_score", 500))
    exp_condition = request.form.get("condition","").strip() or None
    time_cluster = request.form.get("time_cluster", "").strip() or None
    immune_process = request.form.get("immune_process", "").strip() or None

    has_gene   = bool(symbol or geneid)

    if not (has_gene):
        return render_template(
            'tab_2.html',
            enhancers=[],
            error_message=(
              "Please specify either a gene (symbol or gene_id) "
            )
        )

    gene_enhancers = associations_by_symbol(symbol or None, geneid or None, activity_score,
                                           exp_condition, time_cluster, immune_process) if has_gene else []

    return render_template(
        'tab_2.html',
        enhancers=gene_enhancers,
        error_message=""
    )


## Tab 3
@app.route('/activity_class_search', methods=['POST'])
def activity_class_search():
    activity_class = request.form.get("activity_class", "").strip()
    condition = request.form.get("condition", "").strip()
    activity_score_min = request.form.get("activity_score_min", "0").strip()
    time_cluster = request.form.get("time_cluster", "").strip()
    immune_process = request.form.get("immune_process", "").strip()

    try:
        activity_score_min = float(activity_score_min) if activity_score_min else 0
    except ValueError:
        activity_score_min = 0

    enhancers = []
    error_message = ""

    # At least one filter should be applied
    if not any([activity_class, condition, time_cluster, immune_process]):
        error_message = "Please select at least one filter to search"
    else:
        enhancers = search_by_activity_class(
            activity_class=activity_class if activity_class else None,
            condition=condition if condition else None,
            activity_score_min=activity_score_min,
            time_cluster=time_cluster if time_cluster else None,
            immune_process=immune_process if immune_process else None
        )

        if not enhancers:
            error_message = "No enhancers found matching your criteria"

    # Return only the results div for AJAX requests
    return render_template(
        'tab_3.html',
        enhancers=enhancers,
        error_message=error_message
    )


if __name__ == '__main__':
    app.run(debug=True)



# TODO: If the activity score threshold filter has no value, use 0 automatically
