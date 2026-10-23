import json
import pandas as pd

with open("udx_run_summary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("JSON type:", type(data))

if isinstance(data, dict):
    print("\nJSON structure:")
    
    for key, value in data.items():
        print(f"{key}: {type(value).__name__}", end="")
        
        if isinstance(value, list):
            print(f" | {len(value):,} items")
        elif isinstance(value, dict):
            print(f" | {len(value):,} keys")
        else:
            print(f" | {value}")

elif isinstance(data, list):
    print("Number of records:", len(data))


for key, value in data.items():
    
    if isinstance(value, list):
        try:
            temp_df = pd.DataFrame(value)
            
            print(f"\n--- {key} ---")
            print("Shape:", temp_df.shape)
            print("Columns:", temp_df.columns.tolist())
            display(temp_df.head())
            
        except Exception as e:
            print(f"{key} cannot be converted:", e)

print(data.keys())

for key, value in data.items():
    print(key, type(value))

temp_df