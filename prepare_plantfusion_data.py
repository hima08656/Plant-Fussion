
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SOURCE_FILE = BASE_DIR / "plantfusion_mqtt_data.csv"
OUTPUT_FILE = BASE_DIR / "plantfusion_new_data.csv"

# Start collecting only after the new MQTT topic was introduced.
START_TIME = pd.Timestamp("2026-10-22 08:38:00")

if not SOURCE_FILE.exists():
    print("Source CSV not found:", SOURCE_FILE)
    raise SystemExit(1)

df = pd.read_csv(SOURCE_FILE)

if "timestamp" not in df.columns:
    print("CSV does not contain a timestamp column.")
    raise SystemExit(1)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

# Keep readings collected after the new topic was introduced.
clean_df = df[df["timestamp"] >= START_TIME].copy()

# Sort by timestamp and remove exact duplicate records.
clean_df = clean_df.sort_values("timestamp")
clean_df = clean_df.drop_duplicates()

clean_df.to_csv(OUTPUT_FILE, index=False)

print("\n===== PLANTFUSION NEW DATA =====")
print("Rows saved:", len(clean_df))
print("Output file:", OUTPUT_FILE)

if not clean_df.empty:
    print("\nLatest readings:")
    print(clean_df.tail(10).to_string(index=False))
else:
    print(
        "\nNo readings found yet. Keep the Wokwi simulation "
        "and Python subscriber running, then run this script again."
    )
