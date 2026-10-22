
import pandas as pd
from pathlib import Path

file_path = Path(__file__).parent / "plantfusion_new_data.csv"
df = pd.read_csv(file_path)

print("pH value:", repr(df.loc[0, "virtual_ph"]))
print("EC value:", repr(df.loc[0, "virtual_ec"]))
print("pH data type:", type(df.loc[0, "virtual_ph"]).__name__)
print("EC data type:", type(df.loc[0, "virtual_ec"]).__name__)

print("\nCSV row as a dictionary:")
print(df.iloc[0].to_dict())
