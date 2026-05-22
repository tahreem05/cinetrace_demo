"""
CineTrace CSV → MySQL Importer
-------------------------------
Reads every CSV from CSV_DIR and imports it into the matching MySQL table.

Usage:
    python import_csvs_to_mysql.py

Requirements:
    pip install mysql-connector-python
"""

import csv
import os
import sys
from pathlib import Path

# ─── CONFIGURE THESE ──────────────────────────────────────────────────────────
CSV_DIR  = r"D:\CodeWork\CineTrace\CineTrace\data\cinetrace_csvs"

HOST     = "localhost"
PORT     = 3306
USER     = "root"
PASSWORD = "8808"        # ← your MySQL root password here
DATABASE = "cinetrace"
# ──────────────────────────────────────────────────────────────────────────────

# Table import order respects foreign key dependencies (parents before children)
TABLE_ORDER = [
    "Directors",
    "Cinematographers",
    "Genres",
    "Cinematic_Movements",
    "Crew_Members",
    "Users",
    "Films",
    "Film_Genres",
    "Film_Movements",
    "Film_Crew",
    "Influence_Links",
    "Awards",
    "Reviews",
    "Watchlists",
    "Watchlist_Items",
    "Influence_Votes",
]


def connect():
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=HOST, port=PORT, user=USER,
            password=PASSWORD, database=DATABASE
        )
        return conn
    except ImportError:
        print(" mysql-connector-python is not installed.")
        print("   Run:  pip install mysql-connector-python")
        sys.exit(1)
    except Exception as e:
        print(f" Could not connect to MySQL: {e}")
        print("   → Check HOST / USER / PASSWORD at the top of this script.")
        sys.exit(1)


def find_csv(table_name: str) -> Path | None:
    """
    Look for a CSV file matching the table name (case-insensitive).
    Accepts:  Directors.csv  /  directors.csv  /  directors_table.csv  etc.
    """
    csv_dir = Path(CSV_DIR)
    if not csv_dir.exists():
        print(f" CSV_DIR does not exist: {CSV_DIR}")
        sys.exit(1)

    for f in csv_dir.glob("*.csv"):
        if f.stem.lower() == table_name.lower():
            return f
    return None


def import_table(cursor, table_name: str) -> int:
    csv_path = find_csv(table_name)

    if csv_path is None:
        print(f"     Skipped  {table_name:<25} — no matching CSV found in {CSV_DIR}")
        return 0

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        if not columns:
            print(f"     Skipped  {table_name:<25} — CSV has no header row")
            return 0

        rows = []
        for row in reader:
            # Replace empty strings with None so MySQL gets NULL, not ''
            rows.append(tuple(None if v == "" else v for v in row.values()))

    if not rows:
        print(f"    Skipped  {table_name:<25} — CSV is empty")
        return 0

    placeholders = ", ".join(["%s"] * len(columns))
    col_names    = ", ".join(columns)
    sql = (
        f"INSERT IGNORE INTO `{table_name}` ({col_names}) "
        f"VALUES ({placeholders})"
    )

    cursor.executemany(sql, rows)
    return len(rows)


def main():
    print(f" CSV directory : {CSV_DIR}")
    print(f"  Target DB     : {DATABASE} on {HOST}:{PORT}\n")

    conn   = connect()
    cursor = conn.cursor()

    # Disable FK checks so tables can be loaded in any order if needed
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("SET SQL_SAFE_UPDATES = 0")

    total_rows = 0
    for table in TABLE_ORDER:
        try:
            n = import_table(cursor, table)
            if n:
                print(f"    Imported {table:<25} {n} rows")
                total_rows += n
        except Exception as e:
            print(f"    Error on {table}: {e}")
            conn.rollback()
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            cursor.close()
            conn.close()
            sys.exit(1)

    conn.commit()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    print(f"\ Done! {total_rows} total rows imported across {len(TABLE_ORDER)} tables.")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
