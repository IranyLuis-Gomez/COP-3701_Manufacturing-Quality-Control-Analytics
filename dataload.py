import csv
import oracledb

# --- CONFIGURATION ---
LIB_DIR = r"C:\oracle_instant_client\instantclient_23_0"

DB_USER = "SYSTEM"
DB_PASS = "******" # Password Blanked out
DB_DSN  = "localhost:1521/XE"

# Initialize Thick Mode
oracledb.init_oracle_client(lib_dir=LIB_DIR)

# Connect to Database
conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
cur = conn.cursor()
print("✅ Connected to Oracle Database")

# ------------------------
# Load function with TO_DATE for datetime columns
# ------------------------
def load(table, file, date_cols=None):
    date_cols = date_cols or []
    with open(file) as f:
        reader = csv.reader(f)
        headers = next(reader)
        placeholders = []
        for i, h in enumerate(headers):
            if h in date_cols:
                # Convert string to DATE in Oracle
                placeholders.append(f"TO_DATE(:{i+1}, 'YYYY-MM-DD HH24:MI:SS')")
            else:
                placeholders.append(f":{i+1}")
        sql = f"INSERT INTO {table} VALUES ({','.join(placeholders)})"

        for row in reader:
            cur.execute(sql, row)

# ------------------------
# Loading all CSV files
# ------------------------
load("ProductionLine", "data/ProductionLine.csv")
load("Product", "data/Product.csv")
load("ProducedItem", "data/ProducedItem.csv", date_cols=["ProductionDateTime"])
load("Inspector", "data/Inspector.csv")
load("Defect", "data/Defect.csv")
load("Measurement", "data/Measurement.csv", date_cols=["MeasureDateTime"])
load("Inspection", "data/Inspection.csv", date_cols=["InspectionDateTime"])
load("ItemDefect", "data/ItemDefect.csv", date_cols=["DefectDateTime"])
load("QualityPrediction", "data/QualityPrediction.csv", date_cols=["PredDateTime"])

conn.commit()
conn.close()
print("✅ All data loaded successfully!")