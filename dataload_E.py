import csv
import oracledb

# --- CONFIGURATION ---
LIB_DIR = r"C:\oracle\instantclient_23_0"

DB_USER = "PERACCINY007_SCHEMA_PW850"
DB_PASS = "DMSE!1CDYT9N64F1rTRG3K75EGRM1I"
DB_DSN  = "db.freesql.com:1521/23ai_34ui2"

# Initialize Thick Mode 
oracledb.init_oracle_client(lib_dir=LIB_DIR)

# Connect to Database
conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
cur = conn.cursor()
print("✅ Connected to Oracle Database")

# ------------------------
# Load function with debugging
# ------------------------


def load(table, file, date_cols=None):
    date_cols = date_cols or []

    with open(file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)

        placeholders = []
        for i, h in enumerate(headers):
            if h in date_cols:
                placeholders.append(f"TO_TIMESTAMP(:{i+1}, 'YYYY-MM-DD HH24:MI:SS')")
            else:
                placeholders.append(f":{i+1}")

        sql = f"INSERT INTO {table} VALUES ({','.join(placeholders)})"

        count = 0

        for i, row in enumerate(reader, start=2):
            try:
                # clean whitespace
                row = [r.strip() if isinstance(r, str) else r for r in row]

                cur.execute(sql, row)
                count += 1

                # progress update so it never "looks frozen"
                if count % 100 == 0:
                    print(f"✅ {table}: {count} rows inserted")

            except Exception as e:
                print(f"\n❌ ERROR in {table} at CSV line {i}")
                print("ROW:", row)
                print("ERROR:", e)
                break

        conn.commit()
        print(f"✅ {table}: inserted {count} rows")

# ------------------------
# Loading all CSV files (correct order)
# ------------------------
load("ProductionLine", "data/ProductionLine.csv")
load("Product", "data/Product.csv")
load("Inspector", "data/Inspector.csv")
load("Defect", "data/Defect.csv")
load("ProducedItem", "data/ProducedItem.csv", ["ProductionDateTime"])
load("Measurement", "data/Measurement.csv", ["MeasureDateTime"])
load("Inspection", "data/Inspection.csv", ["InspectionDateTime"])
load("ItemDefect", "data/ItemDefect.csv", ["DefectDateTime"])
load("QualityPrediction", "data/QualityPrediction.csv", ["PredDateTime"])

cur.close()
conn.close()

print("✅ All data loaded successfully!")