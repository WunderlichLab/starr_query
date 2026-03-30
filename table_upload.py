import csv
import os
from pathlib import Path

import mariadb
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "processed_data"

ENHANCER_CSV = DATA_DIR / "enhancer.csv"
GENES_CSV = DATA_DIR / "genes.csv"
ASSOCIATIONS_CSV = DATA_DIR / "associations.csv"
TAB3_CSV = DATA_DIR / "tab3_data.csv"

CA_PATH = Path(os.getenv("DB_CA", str(BASE_DIR / "ca.pem")))


def none_if_empty(value):
    if value is None:
        return None
    value = str(value).strip()
    if value in {"", ".", "NA", "N/A", "NULL", "null"}:
        return None
    return value


def to_int(value):
    value = none_if_empty(value)
    if value is None:
        return None
    return int(float(value))


def to_float(value):
    value = none_if_empty(value)
    if value is None:
        return None
    return float(value)


def connect_db():
    return mariadb.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        ssl=True,
        ssl_ca=str(CA_PATH),
    )


def ensure_files_exist():
    required = [
        ENHANCER_CSV,
        GENES_CSV,
        ASSOCIATIONS_CSV,
        TAB3_CSV,
        CA_PATH,
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required files:\n" + "\n".join(missing))


def drop_tables(cur):
    cur.execute("DROP TABLE IF EXISTS Activity_class_info")
    cur.execute("DROP TABLE IF EXISTS Associations")
    cur.execute("DROP TABLE IF EXISTS Genes")
    cur.execute("DROP TABLE IF EXISTS Enhancers")

def insert_in_batches(cur, sql, rows, label, batch_size=200):
    total = len(rows)
    for i in range(0, total, batch_size):
        batch = rows[i:i + batch_size]
        cur.executemany(sql, batch)
        print(f"{label}: inserted {min(i + batch_size, total)}/{total}")

def create_tables(cur):
    cur.execute("""
        CREATE TABLE Enhancers (
            eid INTEGER NOT NULL AUTO_INCREMENT,
            name VARCHAR(30),
            chromosome VARCHAR(2),
            start INTEGER,
            end INTEGER,
            en_length INTEGER,
            exp_condition ENUM('Control','20E','IMD'),
            tf_counts VARCHAR(250),
            tbs INTEGER,
            PRIMARY KEY (eid),
            INDEX location (chromosome, start, end)
        ) ENGINE=InnoDB
    """)

    cur.execute("""
        CREATE TABLE Genes (
            gid INTEGER NOT NULL AUTO_INCREMENT,
            geneid VARCHAR(20),
            chromosome ENUM('3R','3L','2R','2L','X','Y','4'),
            start INTEGER,
            end INTEGER,
            symbol VARCHAR(50),
            immune_process VARCHAR(50),
            time_cluster ENUM('early_C2','mid_C3','late_C1','late_C4'),
            gene_length INTEGER,
            tpm_ctrl DOUBLE,
            tpm_20e DOUBLE,
            tpm_imd DOUBLE,
            PRIMARY KEY (gid),
            INDEX location (chromosome, start, end)
        ) ENGINE=InnoDB
    """)

    cur.execute("""
        CREATE TABLE Associations (
            eid INTEGER NOT NULL,
            gid INTEGER NOT NULL,
            imd_vs_20e DOUBLE,
            20e_vs_ctrl DOUBLE,
            imd_vs_ctrl DOUBLE,
            exp_condition ENUM('Control', '20E', 'IMD'),
            activity DOUBLE,
            accessibility VARCHAR(30),
            PRIMARY KEY (eid, gid, exp_condition),
            FOREIGN KEY (eid) REFERENCES Enhancers (eid)
                ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (gid) REFERENCES Genes (gid)
                ON UPDATE CASCADE ON DELETE CASCADE
        ) ENGINE=InnoDB
    """)

    cur.execute("""
        CREATE TABLE Activity_class_info (
            ac_eid INTEGER NOT NULL AUTO_INCREMENT,
            enhancer_name VARCHAR(30),
            activity_class ENUM(
                'Control',
                '20E',
                'HKSM',
                'Control + 20E',
                'Control + HKSM',
                'HKSM + 20E',
                'Constitutive'
            ),
            accessibility ENUM(
                'Always open',
                'Always closed',
                'HKSM closed',
                'HKSM opened'
            ),
            geneid VARCHAR(30),
            dist_to_enh INTEGER,
            time_cluster VARCHAR(30),
            broad_immune_role VARCHAR(30),
            gene_symbol VARCHAR(30),
            PRIMARY KEY (ac_eid)
        ) ENGINE=InnoDB
    """)

    cur.execute("CREATE INDEX idx_enhancer_name ON Enhancers(name)")
    cur.execute("CREATE INDEX idx_geneid ON Genes(geneid)")


def load_enhancers(cur):
    rows = []

    with open(ENHANCER_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        expected = {
            "Enhancer", "Chromosome", "Start", "End",
            "Length", "Treatment", "TF_counts", "TBS"
        }
        missing = expected - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"enhancer.csv missing columns: {sorted(missing)}")

        for row in reader:
            rows.append((
                none_if_empty(row["Enhancer"]),
                none_if_empty(row["Chromosome"]),
                to_int(row["Start"]),
                to_int(row["End"]),
                to_int(row["Length"]),
                none_if_empty(row["Treatment"]),
                none_if_empty(row["TF_counts"]),
                to_int(row["TBS"]),
            ))

    insert_in_batches(
        cur,
        """
        INSERT INTO Enhancers
        (name, chromosome, start, end, en_length, exp_condition, tf_counts, tbs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows,
        label="Enhancers")

    print(f"Loaded {len(rows)} rows into Enhancers")


def load_genes(cur):
    rows = []

    with open(GENES_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        expected = {
            "GeneID", "Chromosome", "Start", "End", "GeneName",
            "Immune Process", "Time_cluster", "Length",
            "tpm_ctrl", "tpm_20e", "tpm_imd"
        }
        missing = expected - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"genes.csv missing columns: {sorted(missing)}")

        for row in reader:
            rows.append((
                none_if_empty(row["GeneID"]),
                none_if_empty(row["Chromosome"]),
                to_int(row["Start"]),
                to_int(row["End"]),
                none_if_empty(row["GeneName"]),
                none_if_empty(row["Immune Process"]),
                none_if_empty(row["Time_cluster"]),
                to_int(row["Length"]),
                to_float(row["tpm_ctrl"]),
                to_float(row["tpm_20e"]),
                to_float(row["tpm_imd"]),
            ))

    insert_in_batches(
        cur,
        """
        INSERT INTO Genes
        (geneid, chromosome, start, end, symbol, immune_process, time_cluster,
         gene_length, tpm_ctrl, tpm_20e, tpm_imd)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows,
        label="Genes")

    print(f"Loaded {len(rows)} rows into Genes")


def build_lookup(cur, query):
    cur.execute(query)
    lookup = {}
    for row_id, key in cur.fetchall():
        if key is not None and key not in lookup:
            lookup[key] = row_id
    return lookup


def load_associations(cur):
    enhancer_lookup = build_lookup(cur, "SELECT eid, name FROM Enhancers")
    gene_lookup = build_lookup(cur, "SELECT gid, geneid FROM Genes")

    rows = []
    skipped = 0

    with open(ASSOCIATIONS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        expected = {
            "Enhancer", "Gene", "coSTARR LogFC HKSMvs20E",
            "coSTARR LogFC 20EvsControl", "2021 LogFC IMDvsCTRL",
            "Treatment", "new_act_score", "Accessibility"
        }
        missing = expected - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"associations.csv missing columns: {sorted(missing)}")

        for row in reader:
            enhancer_name = none_if_empty(row["Enhancer"])
            geneid = none_if_empty(row["Gene"])

            eid = enhancer_lookup.get(enhancer_name)
            gid = gene_lookup.get(geneid)

            if eid is None or gid is None:
                skipped += 1
                continue

            rows.append((
                eid,
                gid,
                to_float(row["coSTARR LogFC HKSMvs20E"]),
                to_float(row["coSTARR LogFC 20EvsControl"]),
                to_float(row["2021 LogFC IMDvsCTRL"]),
                none_if_empty(row["Treatment"]),
                to_float(row["new_act_score"]),
                none_if_empty(row["Accessibility"]),
            ))

    insert_in_batches(
        cur,
        """
        INSERT INTO Associations
        (eid, gid, imd_vs_20e, 20e_vs_ctrl, imd_vs_ctrl, exp_condition, activity, accessibility)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows,
        label="Associations")

    print(f"Loaded {len(rows)} rows into Associations")
    if skipped:
        print(f"Skipped {skipped} association rows because enhancer or gene was not found")


def load_activity_class_info(cur):
    rows = []

    with open(TAB3_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        expected = {
            "Enhancer", "Activity class", "Accessibility", "Gene",
            "Distance to enhancer", "Time Cluster", "Broad Immune Role"
        }
        missing = expected - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"tab3_data.csv missing columns: {sorted(missing)}")

        for row in reader:
            rows.append((
                none_if_empty(row["Enhancer"]),
                none_if_empty(row["Activity class"]),
                none_if_empty(row["Accessibility"]),
                none_if_empty(row["Gene"]),
                to_int(row["Distance to enhancer"]),
                none_if_empty(row["Time Cluster"]),
                none_if_empty(row["Broad Immune Role"]),
                None,
            ))

    insert_in_batches(
        cur,
        """
        INSERT INTO Activity_class_info
        (enhancer_name, activity_class, accessibility, geneid,
         dist_to_enh, time_cluster, broad_immune_role, gene_symbol)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows,
        label="Activity_class_info")

    print(f"Loaded {len(rows)} rows into Activity_class_info")


def enrich_activity_class_info(cur):
    cur.execute("""
        UPDATE Activity_class_info ac
        INNER JOIN Genes g ON ac.geneid = g.geneid
        SET ac.gene_symbol = g.symbol
    """)
    print("Updated Activity_class_info.gene_symbol from Genes.symbol")


def verify_counts(cur):
    for table in ["Enhancers", "Genes", "Associations", "Activity_class_info"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"{table}: {count}")


def main():
    ensure_files_exist()

    conn = connect_db()
    cur = conn.cursor()

    try:
        print("Dropping old tables...")
        drop_tables(cur)

        print("Creating tables...")
        create_tables(cur)

        print("Loading Enhancers...")
        load_enhancers(cur)

        print("Loading Genes...")
        load_genes(cur)

        print("Loading Associations...")
        load_associations(cur)

        print("Loading Activity_class_info...")
        load_activity_class_info(cur)

        print("Enriching Activity_class_info...")
        enrich_activity_class_info(cur)

        conn.commit()

        print("\nFinal counts:")
        verify_counts(cur)

        print("\nSeed complete.")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()