import pandas as pd
import sqlite3
import os

# --- UPDATED PATHS ---
SCHEMA_FILE_PATH = "app/db/schema.sql" # Path relative to project root
DATA_DIR_PATH = "app/data"             # Path relative to project root
# --- END UPDATED PATHS ---

def load_data():
    # Connect to SQLite DB (auto-creates if not exists)
    conn = sqlite3.connect("ecom.db") # Still creates in project root
    cursor = conn.cursor()

    # Execute schema
    if not os.path.exists(SCHEMA_FILE_PATH):
        print(f"❌ Error: Schema file not found at {SCHEMA_FILE_PATH}. Please create it.")
        conn.close()
        return False

    with open(SCHEMA_FILE_PATH, "r") as f:
        cursor.executescript(f.read())
    print("✅ Database schema applied.")

    # Load CSVs
    try:
        df_elig = pd.read_csv(os.path.join(DATA_DIR_PATH, "eligibility.csv"))
        df_ad = pd.read_csv(os.path.join(DATA_DIR_PATH, "ad_sales.csv"))
        df_total = pd.read_csv(os.path.join(DATA_DIR_PATH, "total_sales.csv"))
    except FileNotFoundError as e:
        print(f"❌ Error loading CSVs: {e}. Make sure '{DATA_DIR_PATH}' folder and CSVs exist.")
        conn.close()
        return False

    # --- CRITICAL ADDITION HERE (from previous fixes) ---
    # Ensure 'eligibility_datetime_utc' is properly formatted with leading zeros for hours
    if 'eligibility_datetime_utc' in df_elig.columns:
        df_elig['eligibility_datetime_utc'] = pd.to_datetime(df_elig['eligibility_datetime_utc']).dt.strftime('%Y-%m-%d %H:%M:%S')
        # Also, ensure boolean column is handled if necessary (SQLite treats TRUE/FALSE as 1/0)
        df_elig['eligibility'] = df_elig['eligibility'].astype(int) # Convert True to 1, False to 0
    # --- END CRITICAL ADDITION ---

    # Write to DB
    df_elig.to_sql("product_eligibility", conn, if_exists="append", index=False)
    df_ad.to_sql("ad_sales_metrics", conn, if_exists="append", index=False)
    df_total.to_sql("total_sales_metrics", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()
    print("✅ Data loaded successfully into ecom.db")
    return True

if __name__ == "__main__":
    # Remove existing DB to ensure fresh load and correct formatting
    if os.path.exists("ecom.db"):
        os.remove("ecom.db")
        print("🗑️ Existing 'ecom.db' removed to ensure fresh data load.")
    load_data()