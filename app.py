#!/usr/bin/env python3

from flask import Flask, request, render_template
#request allows the program to retrieve data from the query string

#the next line gives us a convenient way to insert values into strings
from string import Template 
import mariadb

app = Flask(__name__)

def connect_db():
    #connect to database on host
    # Note: Replace the '...' with the actual user and password
    connection = mariadb.connect(
        host = "bioed-new.bu.edu",
        user = "...",
        password = "...",
        database = "Team9",
        port = 4253
    )
    return connection

def get_gene_info(chr, start, end):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # SQL query to get gene information based on chromosome, start, and end positions
        # Note: Replace the '...' with the actual SQL query you want to execute
        query = """
        SELECT ...
        """

        try:
            cursor.execute(query, [chr, start, end])
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

@app.route('/')
def home():
    return render_template('template.html')

@app.route("/Enhancer_Query", methods=["GET"])
def enhancer_query():
    error_message = ""
    chr = request.args.get("chr")
    start = float(request.args.get("stert"))
    end = float(request.args.get("end"))
    
    # Check if the start and end are entered
    if not start or not end:
        error_message = "Please enter both start and end coordinates."

    # If there is an input error, render page with error message only (no table, no summary)
    if error_message:
        return render_template("template.html", 
                               table_html="",
                               error_message=f"<span style='color:red;'>{error_message}</span>",
                               message="",
                               chr=chr,
                               start=start,
                               end=end)

    # No input error: proceed to query the database
    results = get_gene_info(chr, start, end)
    # Summary statement (always output if no input error)
    message = f"There are {len(results)} genes regulated by enhancers in {start}-{end} in the chromosome {chr}."

    if(results):
        #create a table template
        table_template = Template(
        """
        <table border="1">
            <thead>
                <tr>
                    <th>gene</th>
                    <th>control_ave</th>
                    <th>log_fc_imd_vs_ctrl</th>
                    <th>log_fc_hksm_vs_2oe</th>
                    <th>log_fc_20e_vs_control</th>
                    <th>time_cluster</th>
                    <th>immune_process</th>
                    <th>flybase</th>
                </tr>
            </thead>
            <tbody>
                ${table_rows}
            </tbody>
        </table>
        """
        )
        
        #now create the rows
        table_rows = ""
        for row in results:
            table_rows += """
                <tr>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                </tr>
            """ % (row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])
        table_html = table_template.safe_substitute(table_rows=table_rows)
    else:
        # Even if no results, we output the summary message (indicating zero hits)
        table_html = ""

    return render_template("template.html", 
                           table_html=table_html, 
                           error_message="", 
                           message=message,
                           chr=chr,
                           start=start,
                           end=end)

if __name__ == '__main__':
    app.run(debug=True)