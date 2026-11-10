# Listing 100% matching
# Listing Fuzzy matching
# Golden Record
# Financing lead
# Training lead

import pandas as pd
import numpy as np

location = r"C:\\Users\\syahidhalid\\Syahid_PC\\Analytics - ITD\\00. URS & Test Script\\List of Project - 2026\\Merge - GIT (Active) Unified Data Exchange ()\\"

DMS = pd.read_excel(location+"1. DMS-SR-321539-Zuna-Ed.xlsx", sheet_name='Export Worksheet', engine="openpyxl", dtype=object)

#   DMS_Account = DMS[['CUSTOMER NAME','ACCOUNT NUMBER']].drop_duplicates().groupby(['CUSTOMER NAME'])[['ACCOUNT NUMBER']].count().reset_index().sort_values(by='ACCOUNT NUMBER', ascending=False)
DMS_Status = DMS[['CUSTOMER NAME','ACCOUNT STATUS']].drop_duplicates().groupby(['CUSTOMER NAME'])[['ACCOUNT STATUS']].count().reset_index().sort_values(by='ACCOUNT STATUS', ascending=False)

print(DMS['ACCOUNT STATUS'].value_counts())
# ACCOUNT STATUS
# SETTLED        94314
# ACTIVE         21499
# RECALL          7442
# HOLD               7
# UNINITIATED        5
print("")


DMS_1 = DMS.iloc[np.where(DMS['ACCOUNT STATUS'] == 'ACTIVE')][['CUSTOMER NAME','ACCOUNT STATUS']].drop_duplicates()


print("Original Size: ", DMS.shape)
print("Customer Size: ", DMS_Status.shape)
print("Active Customer Size: ", DMS_1.shape)
# Original Size:  (123267, 205)
# Customer Size:  (13583, 2)
# Active Customer Size:  (8805, 2)
print("")

DMS_Status['MAPPING_KEY'] = (
    DMS_Status['CUSTOMER NAME']
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


#   DMS_1.to_excel("a.xlsx", index=False, engine="openpyxl")
TEST_DMS = DMS_Status[DMS_Status['CUSTOMER NAME'].str.contains('TEST', case=False, na=False)]
# 	CUSTOMER NAME	ACCOUNT STATUS	MAPPING_KEY
# 26141	INFINITE TESTS SOLUTIONS (M) SDN BHD	ACTIVE	INFINITETESTSSOLUTIONSM
# 65205	QUALITEST ENGINEERING SDN.BHD.	ACTIVE	QUALITESTENGINEERING

ELSA = pd.read_excel(location+"4. ELSA-Matching Checking.xlsx", sheet_name='ELSA', engine="openpyxl", dtype=object)

ELSA_Account = ELSA[['Nama Syarikat','Nombor Pendaftaran Baru']].drop_duplicates().groupby(['Nama Syarikat'])[['Nombor Pendaftaran Baru']].count().reset_index().sort_values(by='Nombor Pendaftaran Baru', ascending=False)
ELSA_Status = ELSA[['Nama Syarikat','Status Syarikat']].drop_duplicates().groupby(['Nama Syarikat'])[['Status Syarikat']].count().reset_index().sort_values(by='Status Syarikat', ascending=False)

print(ELSA['Status Syarikat'].value_counts())
# ACTIVE                            4489
# DORMANT                             70
# NOT AVAILABLE FOR EFILING           52
# CONVERTED TO LLP                     8
# UNDER LIQUIDATION                    3
# LIQUIDATED                           3
# CONVERTED TO LLP AND DISSOLVED       2
print("")

ELSA_1 = ELSA.iloc[np.where(ELSA['Status Syarikat'] == 'ACTIVE')][['Nama Syarikat','Status Syarikat']].drop_duplicates()

print("Original Size: ", ELSA.shape)
print("Customer Size: ", ELSA_Status.shape)
print("Active Customer Size: ", ELSA_1.shape)
# Original Size:  (4627, 129)
# Customer Size:  (4600, 2)
# Active Customer Size:  (4462, 2)
print("")

ELSA_Account['MAPPING_KEY'] = (
    ELSA_Account['Nama Syarikat']
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


#   ELSA_1.to_excel("b.xlsx", index=False, engine="openpyxl")

TEST_ELSA = ELSA_Account[ELSA_Account['Nama Syarikat'].str.contains('TEST', case=False, na=False)]
# 	Nama Syarikat	Status Syarikat	MAPPING_KEY
# 55	test_123	ACTIVE	TEST123
# 299	TEST ELSA	ACTIVE	TESTELSA
# 875	TEST123	ACTIVE	TEST123
# 1119	BUSINESS TEST	ACTIVE	BUSINESSTEST
# 1225	TESTING	ACTIVE	TESTING
# 1229	GAMEKA TEST	ACTIVE	GAMEKATEST
# 1450	MARC TEST	ACTIVE	MARCTEST

# ============================================================
# 1. EXACT MATCH FIRST
# ============================================================

COMBINE1_ABSOLUTE = DMS_Status.merge(ELSA_Account, how='outer', on='MAPPING_KEY', suffixes=('_DMS', '_ELSA'), indicator=True) #

print("Exact matching:")
print(COMBINE1_ABSOLUTE._merge.value_counts())
# _merge
# left_only     8645
# both           168
# right_only       0
print("")

COMBINE1_ABSOLUTE['SOURCE'] = COMBINE1_ABSOLUTE['_merge'].map({
    'left_only': 'MIS',
    'both': 'MIS,ELSA',
    'right_only': 'ELSA'
})

COMBINE1_ABSOLUTE['CUSTOMER NAME'] = (COMBINE1_ABSOLUTE['CUSTOMER NAME'].replace('', pd.NA).fillna(COMBINE1_ABSOLUTE['Nama Syarikat']))

GOLDEN_RECORD = COMBINE1_ABSOLUTE[[ 'CUSTOMER NAME',
                                    #'ACCOUNT STATUS',
                                    'MAPPING_KEY',
                                    #'Nama Syarikat',
                                    #'Nombor Pendaftaran Baru',
                                    'SOURCE']]

print(GOLDEN_RECORD.SOURCE.value_counts())
print("")


# ============================================================
# 2. FUZZY MATCH
# ============================================================


DMS_UNMATCHED = GOLDEN_RECORD[GOLDEN_RECORD['SOURCE'] == 'MIS'].copy()

ELSA_KEYS = (ELSA_Account['MAPPING_KEY']
    .dropna()
    .astype(str)
    .unique()
    .tolist())

from rapidfuzz import process, fuzz

def fuzzy_match(value):

    if pd.isna(value):
        return pd.Series([None, 0])

    result = process.extractOne(
        str(value),
        ELSA_KEYS,
        scorer=fuzz.ratio
    )

    if result is not None and result[1] >= 90:
        return pd.Series([result[0], result[1]])

    return pd.Series([None, result[1] if result else 0])

DMS_UNMATCHED[['FUZZY_MAPPING_KEY', 'FUZZY_SCORE']] = (DMS_UNMATCHED['MAPPING_KEY'].apply(fuzzy_match))

DMS_UNMATCHED['FUZZY_MATCH'] = DMS_UNMATCHED['FUZZY_MAPPING_KEY'].notna()


print(DMS_UNMATCHED['FUZZY_MATCH'].value_counts())
print("")
# Fuzzy matching:
# FUZZY_MATCH
# False    8594
# True       51

DMS_UNMATCHED['MATCH_STATUS'] = DMS_UNMATCHED['FUZZY_MATCH'].map({
    True: 'fuzzy_match',
    False: 'unmatched'})

print(DMS_UNMATCHED['MATCH_STATUS'].value_counts())
print("")
# Fuzzy match status:
# MATCH_STATUS
# unmatched      8594
# fuzzy_match      51

DF_FUZZY = DMS_UNMATCHED[[
        'MAPPING_KEY',
        'FUZZY_MAPPING_KEY',
        'FUZZY_SCORE',
        'MATCH_STATUS'
    ]].sort_values('FUZZY_SCORE', ascending=False)
#   DF_FUZZY.to_excel("c.xlsx", index=False, engine="openpyxl")


# CHECKING CUSTOMER NAME
# DMS_1[DMS_1['CUSTOMER NAME'].str.contains('SURIA COMPONENT', case=False, na=False)]
# ELSA_1[ELSA_1['Nama Syarikat'].str.contains('SURIA COMPONENT', case=False, na=False)]


# ============================================================
# 3. FINANCING LEAD
# ============================================================

GOLDEN_RECORD

# ============================================================
# 3. TRAINING LEAD
# ============================================================

GOLDEN_RECORD


TEST_DMS.to_json("TEST_DMS.json", orient="records", indent=4)
TEST_ELSA.to_json("TEST_ELSA.json", orient="records", indent=4)
GOLDEN_RECORD.to_json("GOLDEN_RECORD.json", orient="records", indent=4)
DF_FUZZY.to_json("DF_FUZZY.json", orient="records", indent=4)


#  0) TEST_DMS (VALIDATION)
#  0) TEST_ELSA (VALIDATION)
#  1) GOLDEN_RECORD
#  2) DF_FUZZY (VALIDATION)
#  3) Financing lead
#  4) Training lead
