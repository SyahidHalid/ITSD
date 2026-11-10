import pandas as pd
import numpy as np

file = r"C:\Users\syahidhalid\Syahid_PC\Analytics - ITD\00. URS & Test Script\List of Project - 2026\Merge - GIT (Active) Unified Data Exchange ()\4. ELSA-Matching Checking.xlsx"
file1 = r"D:\00. Git Repository\ITSD\SME Intelligence Hub\input\CBRS_GOLDEN_RECORD_TEST_100.xlsx"
file2 = r"D:\00. Git Repository\ITSD\SME Intelligence Hub\input\EPC_EXPANDED.xlsx"
file3 = r"D:\00. Git Repository\ITSD\SME Intelligence Hub\input\JOMXCESS_EXPANDED.xlsx"
file4 = r"D:\00. Git Repository\ITSD\SME Intelligence Hub\input\MIS4_EXPANDED.xlsx"

ELSA = pd.read_excel(file, sheet_name="ELSA", header=0) #, index_col=None, usecols="A:K" 
CEDAR = pd.read_excel(file1, header=0) #, index_col=None, usecols="A:K" 
EPC = pd.read_excel(file2, header=0) #, index_col=None, usecols="A:K" 
JOMXCESS = pd.read_excel(file3, header=0) #, index_col=None, usecols="A:K" 
MIS = pd.read_excel(file4, header=0) #, index_col=None, usecols="A:K" 


ELSA_1 = ELSA[["Nama Syarikat"]].drop_duplicates("Nama Syarikat").reset_index(drop=True) #,"Negeri"
# ELSA_1["Negeri"].value_counts()
# ELSA_1.iloc[np.where(ELSA_1['Nama Syarikat'].str.contains('SBP Zufar Enterprise', case=False, na=False))]

print("ELSA shape:", ELSA.shape)
print("ELSA_1 shape:", ELSA_1.shape)

ELSA_1['MAPPING_KEY'] = (
    ELSA_1['Nama Syarikat']
    .str.upper()
    .str.replace('(M)', '', regex=False)
    .str.replace('(JB)', '', regex=False)
    .str.replace('SDN', '', regex=False)
    .str.replace('DN', '', regex=False)
    .str.replace('SENDIRIAN', '', regex=False)
    .str.replace('BHD', '', regex=False)
    .str.replace('BERHAD', '', regex=False)
    .str.replace('ENTERPRISE', '', regex=False)
    #.str.replace('(M)', '', regex=False)
    #.str.replace('(JB)', '', regex=False)
    .str.replace('TRADING', '', regex=False)
    .str.replace('SERVICES', '', regex=False)
    .str.replace('SERVICE', '', regex=False)
    .str.replace('RESOURCES', '', regex=False)
    .str.replace('RESOURCE', '', regex=False)
    .str.replace(r'[^A-Z0-9]', '', regex=True)
    .str.replace(' ', '', regex=True)
    .str.replace('\t', '', regex=True)
    .str.replace('SOLUTIONS', '', regex=True)
    .str.replace('SOLUTION', '', regex=True)
    .str.replace('MANUFACTURING', '', regex=True)
    .str.replace('MANUFACTURINGS', '', regex=True)
)

CEDAR_1 = CEDAR[["NAMA SYARIKAT"]].drop_duplicates("NAMA SYARIKAT").reset_index(drop=True) #,"NEGERI"
# CEDAR_1["NAMA SYARIKAT"].value_counts()
# CEDAR_1.iloc[np.where(CEDAR_1['NAMA SYARIKAT'].str.contains('SBP Zufar Enterprise', case=False, na=False))]

print("CEDAR shape:", CEDAR.shape)
print("CEDAR_1 shape:", CEDAR_1.shape)

CEDAR_1['MAPPING_KEY'] = (
    CEDAR_1['NAMA SYARIKAT']
    .str.upper()
    .str.replace('(M)', '', regex=False)
    .str.replace('(JB)', '', regex=False)
    .str.replace('SDN', '', regex=False)
    .str.replace('DN', '', regex=False)
    .str.replace('SENDIRIAN', '', regex=False)
    .str.replace('BHD', '', regex=False)
    .str.replace('BERHAD', '', regex=False)
    .str.replace('ENTERPRISE', '', regex=False)
    #.str.replace('(M)', '', regex=False)
    #.str.replace('(JB)', '', regex=False)
    .str.replace('TRADING', '', regex=False)
    .str.replace('SERVICES', '', regex=False)
    .str.replace('SERVICE', '', regex=False)
    .str.replace('RESOURCES', '', regex=False)
    .str.replace('RESOURCE', '', regex=False)
    .str.replace(r'[^A-Z0-9]', '', regex=True)
    .str.replace(' ', '', regex=True)
    .str.replace('\t', '', regex=True)
    .str.replace('SOLUTIONS', '', regex=True)
    .str.replace('SOLUTION', '', regex=True)
    .str.replace('MANUFACTURING', '', regex=True)
    .str.replace('MANUFACTURINGS', '', regex=True)
)

EPC_1 = EPC[["PENYEWA"]].drop_duplicates("PENYEWA").reset_index(drop=True) #,"STATE"
# EPC_1["PENYEWA"].value_counts()
# EPC_1.iloc[np.where(EPC_1['PENYEWA'].str.contains('SBP Zufar Enterprise', case=False, na=False))]


print("EPC shape:", EPC.shape)
print("EPC_1 shape:", EPC_1.shape)

EPC_1['MAPPING_KEY'] = (
    EPC_1['PENYEWA']
    .str.upper()
    .str.replace('(M)', '', regex=False)
    .str.replace('(JB)', '', regex=False)
    .str.replace('SDN', '', regex=False)
    .str.replace('DN', '', regex=False)
    .str.replace('SENDIRIAN', '', regex=False)
    .str.replace('BHD', '', regex=False)
    .str.replace('BERHAD', '', regex=False)
    .str.replace('ENTERPRISE', '', regex=False)
    #.str.replace('(M)', '', regex=False)
    #.str.replace('(JB)', '', regex=False)
    .str.replace('TRADING', '', regex=False)
    .str.replace('SERVICES', '', regex=False)
    .str.replace('SERVICE', '', regex=False)
    .str.replace('RESOURCES', '', regex=False)
    .str.replace('RESOURCE', '', regex=False)
    .str.replace(r'[^A-Z0-9]', '', regex=True)
    .str.replace(' ', '', regex=True)
    .str.replace('\t', '', regex=True)
    .str.replace('SOLUTIONS', '', regex=True)
    .str.replace('SOLUTION', '', regex=True)
    .str.replace('MANUFACTURING', '', regex=True)
    .str.replace('MANUFACTURINGS', '', regex=True)
)

JOMXCESS["NEGERI"] = str("JOMXCESS ")+JOMXCESS["Sumber Rujukan"]

JOMXCESS_1 = JOMXCESS[["Nama Syarikat"]].drop_duplicates("Nama Syarikat").reset_index(drop=True) #,"NEGERI"
# JOMXCESS_1["Nama Syarikat"].value_counts()
# JOMXCESS_1.iloc[np.where(JOMXCESS_1['Nama Syarikat'].str.contains('SBP Zufar Enterprise', case=False, na=False))]


print("JOMXCESS shape:", JOMXCESS.shape)
print("JOMXCESS_1 shape:", JOMXCESS_1.shape)

JOMXCESS_1['MAPPING_KEY'] = (
    JOMXCESS_1['Nama Syarikat']
    .str.upper()
    .str.replace('(M)', '', regex=False)
    .str.replace('(JB)', '', regex=False)
    .str.replace('SDN', '', regex=False)
    .str.replace('DN', '', regex=False)
    .str.replace('SENDIRIAN', '', regex=False)
    .str.replace('BHD', '', regex=False)
    .str.replace('BERHAD', '', regex=False)
    .str.replace('ENTERPRISE', '', regex=False)
    #.str.replace('(M)', '', regex=False)
    #.str.replace('(JB)', '', regex=False)
    .str.replace('TRADING', '', regex=False)
    .str.replace('SERVICES', '', regex=False)
    .str.replace('SERVICE', '', regex=False)
    .str.replace('RESOURCES', '', regex=False)
    .str.replace('RESOURCE', '', regex=False)
    .str.replace(r'[^A-Z0-9]', '', regex=True)
    .str.replace(' ', '', regex=True)
    .str.replace('\t', '', regex=True)
    .str.replace('SOLUTIONS', '', regex=True)
    .str.replace('SOLUTION', '', regex=True)
    .str.replace('MANUFACTURING', '', regex=True)
    .str.replace('MANUFACTURINGS', '', regex=True)
)

MIS_1 = MIS[["CUSTOMER NAME"]].drop_duplicates("CUSTOMER NAME").reset_index(drop=True) #,"STATE CODE"
# MIS_1["CUSTOMER NAME"].value_counts()
# MIS_1.iloc[np.where(MIS_1['CUSTOMER NAME'].str.contains('SBP Zufar Enterprise', case=False, na=False))]


print("MIS shape:", MIS.shape)
print("MIS_1 shape:", MIS_1.shape)

MIS_1['MAPPING_KEY'] = (
    MIS_1['CUSTOMER NAME']
    .str.upper()
    .str.replace('(M)', '', regex=False)
    .str.replace('(JB)', '', regex=False)
    .str.replace('SDN', '', regex=False)
    .str.replace('DN', '', regex=False)
    .str.replace('SENDIRIAN', '', regex=False)
    .str.replace('BHD', '', regex=False)
    .str.replace('BERHAD', '', regex=False)
    .str.replace('ENTERPRISE', '', regex=False)
    #.str.replace('(M)', '', regex=False)
    #.str.replace('(JB)', '', regex=False)
    .str.replace('TRADING', '', regex=False)
    .str.replace('SERVICES', '', regex=False)
    .str.replace('SERVICE', '', regex=False)
    .str.replace('RESOURCES', '', regex=False)
    .str.replace('RESOURCE', '', regex=False)
    .str.replace(r'[^A-Z0-9]', '', regex=True)
    .str.replace(' ', '', regex=True)
    .str.replace('\t', '', regex=True)
    .str.replace('SOLUTIONS', '', regex=True)
    .str.replace('SOLUTION', '', regex=True)
    .str.replace('MANUFACTURING', '', regex=True)
    .str.replace('MANUFACTURINGS', '', regex=True)
)

GR1 = ELSA_1.merge(CEDAR_1
                             ,on='MAPPING_KEY'
                             , how='outer'
                             , indicator="CEDAR_FLAG"
                             , suffixes=('_ELSA1', '_CEDAR'))

GR1['Nama Syarikat'] = GR1['Nama Syarikat'].fillna(GR1['NAMA SYARIKAT'])

GR1.drop(columns=['NAMA SYARIKAT'], inplace=True)

print(GR1.CEDAR_FLAG.value_counts())

print(GR1['Nama Syarikat'].value_counts())


GR2 = GR1.merge(EPC_1        , on='MAPPING_KEY'
                             , how='outer'
                             , indicator="EPC_FLAG"
                             , suffixes=('_ELSA2', '_EPC'))

GR2['Nama Syarikat'] = GR2['Nama Syarikat'].fillna(GR2['PENYEWA'])

GR2.drop(columns=['PENYEWA'], inplace=True)

print(GR2.EPC_FLAG.value_counts())

print(GR2['Nama Syarikat'].value_counts())

GR2.iloc[np.where(GR2['Nama Syarikat'].str.contains('IMPIAN TRADING SDN BHD', case=False, na=False))]

GR3 = GR2.merge(JOMXCESS_1   , on='MAPPING_KEY'
                             , how='outer'
                             , indicator="JOMXCESS_FLAG"
                             , suffixes=('', '_JOMXCESS'))

GR3['Nama Syarikat'] = GR3['Nama Syarikat'].fillna(GR3['Nama Syarikat_JOMXCESS'])

GR3.drop(columns=['Nama Syarikat_JOMXCESS'], inplace=True)

print(GR3.JOMXCESS_FLAG.value_counts())



GR4 = GR3.merge(MIS_1        , on='MAPPING_KEY'
                             , how='outer'
                             , indicator="MIS_FLAG"
                             , suffixes=('_ELSA4', '_MIS'))

GR4['Nama Syarikat'] = GR4['Nama Syarikat'].fillna(GR4['CUSTOMER NAME'])

GR4.drop(columns=['CUSTOMER NAME'], inplace=True)

print(GR4.MIS_FLAG.value_counts())


GR4.to_excel(r"GR4.xlsx", index=False, engine="openpyxl")

# SME Unified Record / Golden Record	✅	Strong
# SME 360° profile	🟡	Partially complete
# Multi-source integration	✅ / 🟡	Implemented, but data quality/mapping gaps remain
# Financing lead prioritisation	✅	Strong
# ML-driven lead generation	🟡	Output exists, operationalisation/governance still needed
# Development/training identification	✅	Strong prototype
# BI Dashboard	✅	Prototype exists
# Data provenance/traceability	✅	Strong
# AI conversational assistant	🟡	Prototype only
# Knowledge Hub / RAG	❌	Major missing capability
# Solution matching	🟡 / ❌	Partial
# SME Insight Report	❌	Missing
# Intervention/case tracking	❌	Missing
# Outcome/impact tracking	❌	Missing
# Controlled API consumption	❌	Missing
# Enterprise governance/security layer	❌	Not represented in prototype


ELSA_COLUMNS = pd.DataFrame(ELSA.columns, columns=['COLUMN_NAME'])
ELSA_COLUMNS.iloc[np.where(ELSA_COLUMNS['COLUMN_NAME'].str.contains('geri', case=False, na=False))]



