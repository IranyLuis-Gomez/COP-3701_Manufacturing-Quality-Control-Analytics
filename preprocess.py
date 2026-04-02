import pandas as pd
import numpy as np
import os
from faker import Faker

# ------------------------
# Setup
# ------------------------
fake = Faker()
np.random.seed(42)
os.makedirs("data", exist_ok=True)

# ------------------------
# Load Kaggle Mining Data
# ------------------------
df = pd.read_csv("MiningProcess_Flotation_Plant_Database.csv")
df.columns = df.columns.str.strip()
df["date"] = pd.to_datetime(df["date"])

# Limit to 5000 records for example
df = df.sample(n=5000, random_state=42).reset_index(drop=True)

# Ensure numeric columns
for col in ["% Iron Feed", "% Silica Feed", "% Iron Concentrate", "Starch Flow", "Amina Flow", "Ore Pulp Flow"]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# ------------------------
# ProductionLine (Generated)
# ------------------------
production_lines = pd.DataFrame({
    "LineID": range(1, 101),
    "LineName": [f"Flotation Line {i}" for i in range(1, 101)],
    "Location": [f"Mining Plant - Section {i%5}" for i in range(1, 101)]
})
production_lines.to_csv("data/ProductionLine.csv", index=False)

# ------------------------
# Product (Generated)
# ------------------------
products = pd.DataFrame({
    "ProductID": [101],
    "ProductName": ["Iron Ore Concentrate"],
    "Category": ["Mining Output"],
    "StdQualityThreshold": [66.0]
})
products.to_csv("data/Product.csv", index=False)

# ------------------------
# ProducedItem (Derived from Kaggle)
# ------------------------
produced = pd.DataFrame()
produced["ItemID"] = range(1000, 1000 + len(df))
produced["LineID"] = np.random.choice(production_lines["LineID"], len(df))
produced["ProductID"] = 101
produced["ProductionDateTime"] = df["date"]
produced["QualityScore"] = df["% Iron Concentrate"]  # Kaggle
produced["BatchNumber"] = produced["ProductionDateTime"].dt.strftime("BATCH-%m%d")

# Convert to Oracle-friendly format
produced["ProductionDateTime"] = produced["ProductionDateTime"].dt.strftime("%Y-%m-%d %H:%M:%S")
produced.to_csv("data/ProducedItem.csv", index=False)

# ------------------------
# Measurement (Mix Kaggle + Generated)
# ------------------------
measure_cols = ["% Iron Feed", "% Silica Feed", "Starch Flow", "Amina Flow", "Ore Pulp Flow"]

# Define synthetic ranges for flows
flow_ranges = {
    "Starch Flow": (180, 350),
    "Amina Flow": (100, 320),
    "Ore Pulp Flow": (250, 420)
}

df['ItemID'] = produced['ItemID']

# Melt to long format
measurement_df = df.melt(
    id_vars=['ItemID', 'date'],
    value_vars=measure_cols,
    var_name='MeasureType',
    value_name='MeasureValue'
)

# Numeric safety
measurement_df['MeasureValue'] = pd.to_numeric(measurement_df['MeasureValue'], errors='coerce')

# Randomize only flows
measurement_df['MeasureValue'] = measurement_df.apply(
    lambda row: np.random.uniform(*flow_ranges[row.MeasureType])
    if row.MeasureType in flow_ranges else row.MeasureValue,
    axis=1
)

measurement_df['MeasurementNum'] = measurement_df.groupby('ItemID').cumcount() + 1
measurement_df = measurement_df.rename(columns={'date': 'MeasureDateTime'})
measurement_df = measurement_df[["ItemID", "MeasurementNum", "MeasureType", "MeasureValue", "MeasureDateTime"]]

measurement_df['MeasureDateTime'] = pd.to_datetime(measurement_df['MeasureDateTime']).dt.strftime("%Y-%m-%d %H:%M:%S")
measurement_df.to_csv("data/Measurement.csv", index=False)

# ------------------------
# Inspector (Generated)
# ------------------------
inspectors = pd.DataFrame({
    "InspectorID": range(500, 600),
    "FName": [fake.first_name() for _ in range(100)],
    "LName": [fake.last_name() for _ in range(100)],
    "CertificationLvl": np.random.choice(["Junior", "Senior", "Process Engineer", "Metallurgist"], 100)
})
inspectors.to_csv("data/Inspector.csv", index=False)

# ------------------------
# Inspection (Derived)
# ------------------------
# Pivot to wide
measures_wide = measurement_df.pivot(index='ItemID', columns='MeasureType', values='MeasureValue').reset_index()

inspection = pd.DataFrame()
inspection['ItemID'] = measures_wide['ItemID']
inspection['InspectionDateTime'] = produced.set_index('ItemID').loc[inspection['ItemID'], 'ProductionDateTime'].values
inspection['InspectorID'] = np.random.choice(inspectors['InspectorID'], len(inspection))

# Conditions
conditions = {
    'Iron feed below optimal threshold': measures_wide['% Iron Feed'] < 60,
    'Silica feed exceeds acceptable limits': measures_wide['% Silica Feed'] > 10,
    'Amina flow unusually high': measures_wide['Amina Flow'] > 300,
    'Insufficient starch flow detected': measures_wide['Starch Flow'] < 200,
    'Ore pulp flow above safe range': measures_wide['Ore Pulp Flow'] > 400
}

cond_df = pd.DataFrame(conditions)
inspection['Result'] = np.where(cond_df.any(axis=1), 'FAIL', 'PASS')

# Notes vectorized, safe strings
inspection['Notes'] = np.where(
    inspection['Result'] == 'PASS',
    "All parameters within acceptable operating ranges",
    cond_df.apply(lambda row: ", ".join([str(col) for col, val in row.items() if val]), axis=1)
)

inspection['InspectionID'] = 9000 + np.arange(len(inspection))
inspection = inspection[['InspectionID','InspectorID','ItemID','InspectionDateTime','Result','Notes']]

inspection['InspectionDateTime'] = pd.to_datetime(inspection['InspectionDateTime']).dt.strftime("%Y-%m-%d %H:%M:%S")
inspection.to_csv("data/Inspection.csv", index=False)

# ------------------------
# Defect (Generated)
# ------------------------
defects_data = [
    (200, "Low Iron Feed", 3, "Iron feed below optimal level"),
    (201, "High Silica Feed", 4, "Silica feed too high"),
    (202, "Air Flow Instability", 2, "Air flow fluctuations"),
    (203, "High Ore Pulp Flow", 3, "Excessive pulp flow"),
    (204, "Low Starch Flow", 2, "Insufficient starch"),
    (205, "High Amina Flow", 3, "Excess reagent usage")
]
defects = pd.DataFrame(defects_data, columns=["DefectID","DefectName","SeverityLvl","Description"])
defects.to_csv("data/Defect.csv", index=False)

# ------------------------
# ItemDefect (Derived)
# ------------------------
defect_mapping = {
    'Iron feed below optimal threshold': 200,
    'Silica feed exceeds acceptable limits': 201,
    'Amina flow unusually high': 205,
    'Insufficient starch flow detected': 204,
    'Ore pulp flow above safe range': 203
}

# Vectorized assignment
item_defects_rows = [
    (item_id, defect_mapping[cond], produced.loc[produced['ItemID']==item_id, 'ProductionDateTime'].values[0])
    for cond, mask in conditions.items()
    for item_id in measures_wide['ItemID'][mask]
]

item_defect_df = pd.DataFrame(item_defects_rows, columns=['ItemID','DefectID','DefectDateTime'])
item_defect_df = item_defect_df.drop_duplicates()

item_defect_df['DefectDateTime'] = pd.to_datetime(item_defect_df['DefectDateTime']).dt.strftime("%Y-%m-%d %H:%M:%S")
item_defect_df.to_csv("data/ItemDefect.csv", index=False)

# ------------------------
# QualityPrediction (Derived)
# ------------------------
qp = pd.DataFrame()
qp["ItemID"] = produced["ItemID"]
qp["PredQualityScore"] = produced["QualityScore"] + np.random.normal(0, 1, len(produced))
qp["PredDefectProb"] = np.clip(measures_wide['% Silica Feed'] / 10, 0, 1)
qp["PredDateTime"] = produced["ProductionDateTime"]
qp["ConfidenceLvl"] = np.random.uniform(85, 99, len(produced))
qp["ModelVer"] = "RF_Kaggle_v1"

qp["PredDateTime"] = pd.to_datetime(qp["PredDateTime"]).dt.strftime("%Y-%m-%d %H:%M:%S")
qp.to_csv("data/QualityPrediction.csv", index=False)

print("✅ All CSV files generated successfully!")