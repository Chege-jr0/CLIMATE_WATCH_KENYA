import pandas as pd
import sqlite3
import os
from transform import transform_all

DATABASE_PATH = "database/climate.db"

def get_connection():
    """Create connection to SQLite database"""
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    print("Connection to database established")
    return conn

def load_temperature(conn, df):
    """Load temperature data"""
    print("Loading temperature data...")
    df["temp_severity"] = df["temp_severity"].astype(str)
    df.to_sql("temperature", conn, if_exists="replace", index=False)
    count = pd.read_sql("SELECT COUNT(*) AS total FROM temperature", conn)
    print(f"Temperature data loaded: {count['total'][0]} records")

def load_rainfall(conn, df):
    """Load rainfall data"""
    print("Loading rainfall data...")
    df.to_sql("rainfall", conn, if_exists="replace", index=False)
    count = pd.read_sql("SELECT COUNT(*) AS total FROM rainfall", conn)
    print(f"Rainfall data loaded: {count['total'][0]} records")

def load_extreme_events(conn, df):
    """Load extreme events data"""
    print("Loading extreme events data...")
    df.to_sql("extreme_events", conn, if_exists="replace", index=False)
    count = pd.read_sql("SELECT COUNT(*) AS total FROM extreme_events", conn)
    print(f"Extreme events data loaded: {count['total'][0]} records")

def load_vulnerability(conn, df):
    """Load vulnerability index data"""
    print("Loading vulnerability index data...")
    df.to_sql("vulnerability_index", conn, if_exists="replace", index=False)
    count = pd.read_sql("SELECT COUNT(*) AS total FROM vulnerability_index", conn)
    print(f"Vulnerability index data loaded: {count['total'][0]} records")

def verify_database(conn):
    """Check all tables and show record counts."""
    print("=" * 45)

    tables = [
        "temperature",
        "rainfall",
        "extreme_events",
        "vulnerability_index"
    ]

    all_good = True
    for table in tables:
        try:
            count = pd.read_sql(
                f"SELECT COUNT(*) AS total FROM {table}", conn
            )
            records = int(count["total"][0])
            status = "✅" if records > 0 else "❌"
            print(f"  {status} {table}: {records} records")
            if records == 0:
                all_good = False
        except Exception as e:
            print(f"   {table}: Error — {e}")
            all_good = False

    print("=" * 45)
    if all_good:
        print("All tables loaded successfully!")
    else:
        print(" Some tables have issues!")    

def load_all():
    print("Starting Climate Watch data load")

    data = transform_all()

    conn = get_connection()

    load_temperature(conn, data["temperature"])
    load_rainfall(conn, data["rainfall"])
    load_extreme_events(conn, data["events"])
    load_vulnerability(conn, data["vulnerability"])

    verify_database(conn)

    conn.close()
    print("Data load complete")

if __name__ == "__main__":
    load_all()    