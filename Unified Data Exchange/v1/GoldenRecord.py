import os
import pandas as pd
from rapidfuzz import process, fuzz
import numpy as np

import xlsxwriter

#   !pip install rapidfuzz --trusted-host pypi.org --trusted-host files.pythonhosted.org


current_time = pd.Timestamp.now()


link = r"D:\\00. Git Repository\\ITSD\\Unified Data Exchange"

file1 = "1. CIF-FOS-Zuna Ed"
sheet_name1 = "Export Worksheet"
filepath1 = os.path.join(link, file1 + ".xlsx")
Excel1 = pd.read_excel(filepath1, header=0, sheet_name=sheet_name1) #, usecols="A:D"
#Excel.shape


file2 = "2. CEDAR Participants Databased 2026 4-Ed"
sheet_name2 = "NEW_MASTER MUM 2026_AS OF JUNE"
filepath2 = os.path.join(link, file2 + ".xlsx")
Excel2 = pd.read_excel(filepath2, header=73, usecols="B:AN", sheet_name=sheet_name2)


file3 = "3. EPC-WORKING CLOSING 30 JUNE 2026-Zuna-Ed"
sheet_name3 = "WORKING JUNE 2026"
filepath3 = os.path.join(link, file3 + ".xlsx")
Excel3 = pd.read_excel(filepath3, header=0, sheet_name=sheet_name3) #, usecols="A:D",


file4 = "4. ELSA-Matching Checking"
sheet_name4 = "ELSA"
filepath4 = os.path.join(link, file4 + ".xlsx")
Excel4 = pd.read_excel(filepath4, header=0, sheet_name=sheet_name4) #, usecols="A:D",


file5 = "5. JomXcess-Self-Check-In Central Region (Responses)-Ed"
sheet_name5 = "Form responses 1"
filepath5 = os.path.join(link, file5 + ".xlsx")
Excel5 = pd.read_excel(filepath5, header=0, sheet_name=sheet_name5) #, usecols="A:D",

# from rapidfuzz import fuzz
#  
# score = fuzz.ratio(
# "Muhammad Syahid",
# "Mohamad Syahid"
# )
#  
# print(score)


# Clean text
Excel1_A = Excel1.iloc[np.where(~Excel1["BUSINESS_NAME"].isnull())][["BUSINESS_NAME"]].sort_values(by="BUSINESS_NAME",ascending=True)
Excel2_A = Excel2.iloc[np.where(~Excel2["NAMA_SYARIKAT_YANG_DIDAFTARKAN_(SSM/PBT)"].isnull())][["NAMA_SYARIKAT_YANG_DIDAFTARKAN_(SSM/PBT)"]].sort_values(by="NAMA_SYARIKAT_YANG_DIDAFTARKAN_(SSM/PBT)",ascending=True)
Excel3_A = Excel3.iloc[np.where(~Excel3["PENYEWA"].isnull())][["PENYEWA"]].sort_values(by="PENYEWA",ascending=True)
Excel4_A = Excel4.iloc[np.where(~Excel4["Nama Syarikat"].isnull())][["Nama Syarikat"]].sort_values(by="Nama Syarikat",ascending=True)
Excel5_A = Excel5.iloc[np.where(~Excel5["Nama Syarikat"].isnull())][["Nama Syarikat"]].sort_values(by="Nama Syarikat",ascending=True)

Excel1_A["BUSINESS_NAME"] = Excel1_A["BUSINESS_NAME"].astype(str).str.upper().str.strip()
Excel2_A["NAMA_SYARIKAT_YANG_DIDAFTARKAN_(SSM/PBT)"] = Excel2_A["NAMA_SYARIKAT_YANG_DIDAFTARKAN_(SSM/PBT)"].astype(str).str.upper().str.strip()
Excel3_A["PENYEWA"] = Excel3_A["PENYEWA"].astype(str).str.upper().str.strip()
Excel4_A["Nama Syarikat"] = Excel4_A["Nama Syarikat"].astype(str).str.upper().str.strip()
Excel5_A["Nama Syarikat"] = Excel5_A["Nama Syarikat"].astype(str).str.upper().str.strip()

Excel1_A.drop_duplicates("BUSINESS_NAME", keep="first", inplace=True)
Excel2_A.drop_duplicates("NAMA_SYARIKAT_YANG_DIDAFTARKAN_(SSM/PBT)", keep="first")
Excel3_A.drop_duplicates("PENYEWA", keep="first")
Excel4_A.drop_duplicates("Nama Syarikat", keep="first")
Excel5_A.drop_duplicates("Nama Syarikat", keep="first")

Excel1_A.rename(columns={"BUSINESS_NAME": "DMS"}, inplace=True)
Excel2_A.rename(columns={"NAMA_SYARIKAT_YANG_DIDAFTARKAN_(SSM/PBT)": "CEDAR"}, inplace=True)
Excel3_A.rename(columns={"PENYEWA": "EPC"}, inplace=True)
Excel4_A.rename(columns={"Nama Syarikat": "ELSA"}, inplace=True)
Excel5_A.rename(columns={"Nama Syarikat": "JomXcess"}, inplace=True)

# Excel1_A.DMS.value_counts()

#match = process.extractOne(Excel3_A["PENYEWA"],Excel1_A["BUSINESS_NAME"].tolist(),scorer=fuzz.token_set_ratio)


# Function to get best match
def get_match(name, choices, threshold=90):
    match = process.extractOne(name, choices,  scorer=fuzz.token_set_ratio)

    if match and match[1] >= threshold:
        return pd.Series([match[0], match[1]])
    else:
        return pd.Series([None, None])

# Find best match
#Excel1_A[["Matched_Name", "Fuzz_Ratio"]] = Excel1_A["BUSINESS_NAME"].apply(lambda x: get_match(x, Excel3_A["PENYEWA"].tolist()))
Excel2_A[["Matched_with_DMS", "Fuzz_Ratio"]] = Excel2_A["CEDAR"].apply(lambda x: get_match(x, Excel1_A["DMS"].tolist()))
Excel3_A[["Matched_with_DMS", "Fuzz_Ratio"]] = Excel3_A["EPC"].apply(lambda x: get_match(x, Excel1_A["DMS"].tolist()))
Excel4_A[["Matched_with_DMS", "Fuzz_Ratio"]] = Excel4_A["ELSA"].apply(lambda x: get_match(x, Excel1_A["DMS"].tolist()))
Excel5_A[["Matched_with_DMS", "Fuzz_Ratio"]] = Excel5_A["JomXcess"].apply(lambda x: get_match(x, Excel1_A["DMS"].tolist()))


# Excel1_A.to_excel(os.path.join(link, "Excel1_A.xlsx"), index=False )
# Excel2_A.to_excel(os.path.join(link, "Excel2_A.xlsx"), index=False )
# Excel3_A.to_excel(os.path.join(link, "Excel3_A.xlsx"), index=False )
# Excel4_A.to_excel(os.path.join(link, "Excel4_A.xlsx"), index=False )
# Excel5_A.to_excel(os.path.join(link, "Excel5_A.xlsx"), index=False )

# Excel1_A.to_json("Excel1_A.json", orient="records", indent=4)
# Excel2_A.to_json("Excel2_A.json", orient="records", indent=4)
# Excel3_A.to_json("Excel3_A.json", orient="records", indent=4)
# Excel4_A.to_json("Excel4_A.json", orient="records", indent=4)
# Excel5_A.to_json("Excel5_A.json", orient="records", indent=4)


# | Threshold | Meaning               |
# | --------- | --------------------- |
# | 90-100    | Very strict           |
# | 80-89     | Good balance          |
# | 70-79     | Moderate similarity   |
# | 60-69     | Risk of false matches |
# | <60       | Usually too loose     |

Excel2_A.iloc[]

Combine2_A = Excel1.merge(Excel2_A, left_on="BUSINESS_NAME", right_on="Matched_with_DMS", how="outer", indicator='_CEDAR')