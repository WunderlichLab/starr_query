#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify
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


## Get filter options:
def get_filter_options():
    """Fetch unique activity classes, conditions, time clusters, immune processes and broad immune roles from database"""
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Get unique conditions
        cursor.execute(
            "SELECT DISTINCT exp_condition FROM Enhancers WHERE exp_condition IS NOT NULL ORDER BY exp_condition;")
        conditions = [row[0] for row in cursor.fetchall()]

        # Get unique activity classes
        cursor.execute(
            "SELECT DISTINCT activity_class FROM Activity_class_info WHERE activity_class IS NOT NULL ORDER BY activity_class;")
        activity_classes = [row[0] for row in cursor.fetchall()]

        # Get unique accessibility
        cursor.execute(
            "SELECT DISTINCT accessibility FROM Activity_class_info WHERE accessibility IS NOT NULL ORDER BY accessibility;")
        accessibilities = [row[0] for row in cursor.fetchall()]

        # Get unique time clusters
        cursor.execute("SELECT DISTINCT time_cluster FROM Genes WHERE time_cluster IS NOT NULL ORDER BY time_cluster;")
        time_clusters = [row[0] for row in cursor.fetchall()]

        # Get unique immune processes
        cursor.execute(
            "SELECT DISTINCT immune_process FROM Genes WHERE immune_process IS NOT NULL ORDER BY immune_process;")
        immune_processes = [row[0] for row in cursor.fetchall()]

        # Get unique broad immune roles
        cursor.execute(
            "SELECT DISTINCT broad_immune_role FROM Activity_class_info WHERE broad_immune_role IS NOT NULL ORDER BY broad_immune_role;")
        broad_immune_roles = [row[0] for row in cursor.fetchall()]

        # Get unique time_clusters for tab 3
        cursor.execute(
            "SELECT DISTINCT time_cluster FROM Activity_class_info WHERE time_cluster IS NOT NULL ORDER BY time_cluster;")
        time_clusters_tab3 = [row[0] for row in cursor.fetchall()]

        conn.close()
        filters = {
            'conditions': conditions,
            'activity_classes': activity_classes,
            'accessibilities': accessibilities,
            'time_clusters': time_clusters,
            'immune_processes': immune_processes,
            'broad_immune_roles': broad_immune_roles,
            'time_clusters_tab3': time_clusters_tab3
        }

        return filters

    except mariadb.Error as e:
        print(f"Error fetching filter options: {e}")
        return {
            'conditions': [],
            'activity_classes': [],
            'accessibilities': [],
            'time_clusters': [],
            'immune_processes': [],
            'broad_immune_roles': [],
            'time_clusters_tab3': []
        }

## Tab 1
def associations_by_region(chr=None, start=None, end=None, enhancer_name=None, activity_score_min=0, exp_condition=None,
                           time_cluster=None, immune_process=None):
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
                       a.exp_condition  AS exp_condition,
                       a.activity       AS act_score,
                       g.symbol         AS gene_symbol,
                       g.geneid         AS gene_id,
                       g.tpm_ctrl       AS tpm_ctrl,
                       g.tpm_20e        AS tpm_20e,
                       g.tpm_imd        AS tpm_imd,
                       g.immune_process AS immune_process,
                       g.time_cluster   AS time_cluster
                FROM Enhancers e
                         JOIN Associations a ON e.eid = a.eid
                         JOIN Genes g ON a.gid = g.gid
                WHERE a.activity >= %s
                """

        params = [activity_score_min]

        # Check if coordinates are provided
        if chr and start is not None and end is not None:
            query += """ AND e.chromosome = %s
              AND e.start >= %s
              AND e.end <= %s"""
            params.extend([chr, start, end])

        # Check if enhancer name is provided
        elif enhancer_name:
            [chr,region] = enhancer_name.split(':')
            [start, end] = region.split('-')
            query += """ AND e.chromosome = %s
                          AND e.start >= %s
                          AND e.end <= %s"""
            params.extend([chr, start, end])

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
            a.activity AS act_score,
            a.exp_condition AS exp_condition,
            g.symbol AS gene_symbol,
            g.geneid AS gene_id,
            g.tpm_ctrl AS tpm_ctrl,
            g.tpm_imd AS tpm_imd,
            g.tpm_20e AS tpm_20e,
            e.chromosome AS chromosome,
            e.start AS start,
            e.end AS end,
            g.time_cluster AS time_cluster,
            g.immune_process AS immune_process
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
def search_by_activity_class(chr=None, start=None, end=None, enhancer_name=None,
                             activity_class=None, accessibility=None):
    """Search enhancers by genomic region and/or activity class and accessibility"""
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
                SELECT ac.ac_eid         AS enhancer_id,
                       ac.enhancer_name  AS enhancer_name,
                       ac.activity_class AS activity_class,
                       ac.accessibility  AS accessibility,
                       ac.geneid         AS gene_id,
                       ac.gene_symbol    AS gene_symbol
                FROM Activity_class_info AS ac
                WHERE 1 = 1
                """

        params = []

        # Check if coordinates are provided
        if chr and start is not None and end is not None:
            # Parse chromosome and coordinates from enhancer_name to match
            query += """ AND ac.enhancer_name LIKE %s"""
            region_pattern = f"{chr}:%"
            params.append(region_pattern)

        # Check if enhancer name is provided
        elif enhancer_name:
            query += """ AND ac.enhancer_name = %s"""
            params.append(enhancer_name)

        if activity_class:
            query += " AND activity_class = %s"
            params.append(activity_class)

        if accessibility:
            query += " AND accessibility = %s"
            params.append(accessibility)

        query += " ORDER BY enhancer_name, gene_id"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # If coordinates were provided, filter by coordinate range
        if chr and start is not None and end is not None:
            filtered_rows = []
            for row in rows:
                enhancer_name = row[1]  # enhancer_name is at index 1
                if enhancer_name and ':' in enhancer_name:
                    try:
                        parts = enhancer_name.split(':')
                        if len(parts) == 2:
                            coords = parts[1].split('-')
                            if len(coords) == 2:
                                enh_start = int(coords[0])
                                enh_end = int(coords[1])
                                # Check if enhancer overlaps with the query region
                                if not (enh_end < start or enh_start > end):
                                    filtered_rows.append(row)
                    except (ValueError, IndexError):
                        continue
            rows = filtered_rows

        # Remove duplicates while preserving order
        seen = set()
        unique_rows = []
        for row in rows:
            if row not in seen:
                seen.add(row)
                unique_rows.append(row)

        # Convert to dictionaries for template access
        columns = ['enhancer_id', 'enhancer_name', 'activity_class', 'accessibility',
                   'gene_id', 'gene_symbol']

        result_dicts = [dict(zip(columns, row)) for row in unique_rows]

        conn.close()

        return result_dicts

    except mariadb.Error as e:
        print(f"Database error: {e}")
        return []



## Tab 0
@app.route('/')
def index():
    filter_options = get_filter_options()
    return render_template('template.html', filter_options=filter_options, request=request)

## Tab 1
@app.route('/submit_region', methods=['POST'])
def find_gene():
    # Get form data
    chr = request.form.get('chr', '').strip() or None
    start_str = request.form.get('start', '').strip()
    end_str = request.form.get('end', '').strip()
    enhancer_name = request.form.get('enhancer_name', '').strip() or None
    activity_score_min = float(request.form.get("activity_score_min", 0))
    exp_condition = request.form.get("condition", "").strip() or None
    time_cluster = request.form.get("time_cluster", "").strip() or None
    immune_process = request.form.get("immune_process", "").strip() or None

    # Convert start/end to integers if provided
    start = int(start_str) if start_str else None
    end = int(end_str) if end_str else None

    # Validate input: either coordinates OR enhancer name
    has_coordinates = chr and start is not None and end is not None
    has_enhancer_name = enhancer_name is not None

    if not (has_coordinates or has_enhancer_name):
        filter_options = get_filter_options()
        return render_template('tab_1.html',
                             enhancers=[],
                             filter_options=filter_options,
                             error_message="Please provide either coordinates (chromosome, start, end) OR an enhancer name.")

    enhancers = associations_by_region(chr, start, end, enhancer_name, activity_score_min,
                                       exp_condition, time_cluster, immune_process)

    filter_options = get_filter_options()

    return render_template('tab_1.html', enhancers=enhancers, filter_options=filter_options)

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

    filter_options = get_filter_options()

    if not (has_gene):
        return render_template(
            'tab_2.html',
            enhancers=[],
            filter_options=filter_options,
            error_message=(
              "Please specify either a gene (symbol or gene_id) "
            )
        )


    gene_enhancers = associations_by_symbol(symbol or None, geneid or None, activity_score,
                                           exp_condition, time_cluster, immune_process) if has_gene else []

    return render_template(
        'tab_2.html',
        enhancers=gene_enhancers,
        filter_options=filter_options,
        error_message=""
    )


## Tab 3
@app.route('/activity_class_search', methods=['POST'])
def activity_class_search():
    # Get genomic region parameters
    chr = request.form.get('chr', '').strip() or None
    start_str = request.form.get('start', '').strip() or None
    end_str = request.form.get('end', '').strip() or None
    enhancer_name = request.form.get('enhancer_name', '').strip() or None

    # Get activity parameters
    activity_class = request.form.get("activity_class", "").strip() or None
    accessibility = request.form.get("accessibility", "").strip() or None

    # Convert start/end to integers if provided
    start = int(start_str) if start_str else None
    end = int(end_str) if end_str else None

    filter_options = get_filter_options()

    enhancers = []
    error_message = ""

    # Check if at least one search criterion is provided
    has_coordinates = chr and start is not None and end is not None
    has_enhancer_name = enhancer_name is not None
    has_activity_filters = activity_class or accessibility

    if not (has_coordinates or has_enhancer_name or has_activity_filters):
        error_message = "Please provide either genomic coordinates, enhancer name, or select at least one activity filter"
    else:
        enhancers = search_by_activity_class(
            chr=chr,
            start=start,
            end=end,
            enhancer_name=enhancer_name,
            activity_class=activity_class,
            accessibility=accessibility
        )

        if not enhancers:
            error_message = "No enhancers found matching your criteria"

    return render_template(
        'tab_3.html',
        enhancers=enhancers,
        filter_options=filter_options,
        error_message=error_message
    )


@app.route('/autocomplete_gene', methods=['GET'])
def autocomplete_gene():
    """Autocomplete endpoint for gene symbols"""
    query = request.args.get('term', '').strip().lower()

    if len(query) < 2:  # Only search if at least 2 characters
        return jsonify([])

    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Search for gene symbols that start with or contain the query
        sql = """
              SELECT DISTINCT symbol, geneid
              FROM Genes
              WHERE LOWER(symbol) LIKE %s
                 OR LOWER(geneid) LIKE %s
              ORDER BY symbol LIMIT 20 \
              """

        search_pattern = f"%{query}%"
        cursor.execute(sql, (search_pattern, search_pattern))
        results = cursor.fetchall()

        # Format results for autocomplete
        suggestions = []
        for row in results:
            symbol, geneid = row
            if symbol:
                suggestions.append({
                    'label': f"{symbol} ({geneid})",
                    'value': symbol,
                    'geneid': geneid
                })

        conn.close()
        return jsonify(suggestions)

    except mariadb.Error as e:
        print(f"Error in autocomplete: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)



