#!/usr/bin/env python3

from flask import Flask, request, render_template
#request allows the program to retrieve data from the query string

#the next line gives us a convenient way to insert values into strings
from string import Template 
# import mariadb

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
    # For testing, return a fixed list of tuples
    # Format: (Gene ID, Gene Name)
    return [
        ("FBgn0000001", "geneA"),
        ("FBgn0000002", "geneB"),
        ("FBgn0000003", "geneC")
    ]

# def get_genes_by_enhancer(chr, start, end):
#     try:
#         conn = connect_db()
#         cursor = conn.cursor()

#         query = """
#         SELECT g.gid, g.name
#         FROM gene g
#         JOIN enhancer_to_gene eg ON g.gid = eg.gid
#         WHERE eg.chr = ?
#           AND eg.start <= ?
#           AND eg.end >= ?
#         """
#         cursor.execute(query, (chr, start, end))
#         result = cursor.fetchall()
#         conn.close()
#         return result
#     except mariadb.Error as e:
#         print(f"DB Error: {e}")
#         return []

#     except mariadb.Error as e:
#         # error handling for connection
#         print(f"Error connecting to the database: {e}")
#         return []

def get_enhancers_by_gene(gene_query):
    # SELECT eg.chr, eg.start, eg.end
    # FROM enhancer_to_gene eg
    # JOIN gene g ON eg.gid = g.gid
    # WHERE g.gid = %s OR g.name LIKE %s
    return [
        ("2L", 1000, 2000),
        ("X", 50000, 51000)
    ]

@app.route('/')
def home():
    return render_template('template.html')

@app.route('/submit_enhancer', methods=['POST'])
def submit():
    chr = request.form['chr']
    start = int(request.form['start'])
    end = int(request.form['end'])
    genes = get_genes_by_enhancer(chr, start, end)
    return render_template('find_gene_results.html', genes=genes)

@app.route('/submit_gene', methods=['POST'])
def submit_gene():
    query = request.form['gene_query']
    enhancers = get_enhancers_by_gene(query)
    return render_template('find_enhancer_results.html', enhancers=enhancers)

if __name__ == '__main__':
    app.run(debug=True)
