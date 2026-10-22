
import pandas as pd
import joblib

from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "plantfusion_new_data.csv"
MODEL_FILE = BASE_DIR / "plantfusion_anomaly_model.pkl"

FEATURES = [
    "air_temp_c",
    "air_humidity_pct",
    "soil_moisture_pct",
    "light_pct",
    "virtual_ph",
    "virtual_ec",
    "soil_temp_c",
]

# 1. Load sensor data
if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}"
    )

df = pd.read_csv(DATA_FILE)

# 2. Validate required columns
missing_columns = [
    column for column in FEATURES
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns: {missing_columns}"
    )

# 3. Convert sensor columns to numeric values
X = df[FEATURES].apply(
    pd.to_numeric, errors="coerce"
)

# Ignore rows where every sensor value is missing
X = X.dropna(how="all")

if len(X) < 10:
    raise ValueError(
        "At least 10 usable readings are required "
        "for this initial experiment."
    )

# 4. Build an anomaly detection pipeline
model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("detector", IsolationForest(
        n_estimators=100,
        contamination="auto",
        random_state=42
    )),
])

# 5. Train the model
model.fit(X)

# 6. Save the trained model
joblib.dump(model, MODEL_FILE)

# 7. Predict unusual readings in the dataset
predictions = model.predict(X)

results = df.loc[X.index].copy()
results["anomaly_result"] = predictions
results["anomaly_result"] = (
    results["anomaly_result"]
    .map({1: "Normal pattern", -1: "Unusual pattern"})
)

# Save predictions separately
RESULT_FILE = BASE_DIR / "plantfusion_anomaly_results.csv"
results.to_csv(RESULT_FILE, index=False)

print("\n===== PLANTFUSION ML MODEL =====")
print("Training rows:", len(X))
print("Model saved:", MODEL_FILE.name)
print("Predictions saved:", RESULT_FILE.name)

print("\nPrediction summary:")
print(results["anomaly_result"].value_counts())

print("\nLast 5 predictions:")
print(
    results[
        ["timestamp", "anomaly_result"]
    ].tail().to_string(index=False)
)

print(
    "\nNote: These are preliminary anomaly-detection "
    "results, not plant disease predictions."
)
