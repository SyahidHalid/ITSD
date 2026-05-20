
import pandas as pd
import numpy as np
import pyodbc

#   Timestamp
current_time = pd.Timestamp.now()

#  Read Excel
link = r"C:\\Users\\syahidhalid\\Syahid_PC\Analytics - ITD\\00. URS & Test Script\\List of Project - 2026\\BD (Active) - PD Rating Migration (SR2604-18803)"

file = "Loandatabase_Feb2026 (Rating) (ITSD)"

sheet_name = "Loandatabase_Feb2026"
#sheet_name = "Loandatabase_Feb2026 (UAT)"

filepath = os.path.join(link, file + ".xlsx")

Excel = pd.read_excel(filepath,header=5, usecols="B:FH", sheet_name=sheet_name)

Excel1 = Excel.iloc[np.where(Excel['Status of Account'].isin(['Active',
                                                              'Active-Overdue',
                                                              'Active-Watchlist',
                                                              'Active-Watchlist-Overdue',
                                                              'Pending Disbursement',
                                                              'Pending Disbursement-Watchlist']))]
#  Excel1['Status of Account'].value_counts()

Excel2 = Excel1[["Exim Account Number/ FA Number",
                 "Customer Name",
                 "Status of Account",
                 "Application Type",
                 "Facility",
                 "Facility Currency",
                 "Amount Approved / Facility Limit (MYR)",
                 "Date Approved at Origination",
                 "Approval Authority",
                 "Rating at Origination",
                 "Internal Credit Rating (PD/PF)",
                 "Relationship Manager (RM)",
                 "Team",
                 "Position as At"]]
#  Excel2['Exim Account Number/ FA Number'].value_counts()

Excel2["AccountNumber"] = Excel2["Exim Account Number/ FA Number"].str.replace("-", "", regex=False)
Excel2["AccountNumber"] = Excel2["AccountNumber"].str.replace(" ", "", regex=False)
Excel2["AccountNumber"] = Excel2["AccountNumber"].str.replace("  ", "", regex=False)
Excel2["AccountNumber"] = Excel2["AccountNumber"].str.replace("   ", "", regex=False)
Excel2["AccountNumber"] = Excel2["AccountNumber"].str.replace("    ", "", regex=False)
#  Excel2["AccountNumber"].value_counts()


#  UAT
connection = pyodbc.connect(
   'DRIVER={ODBC Driver 17 for SQL Server};'
   
   'SERVER=10.32.1.52,1455;'
   #'SERVER=10.20.1.4,1455;'

   'DATABASE=mis_db_prod23022025;'
   #'DATABASE=mis_db_prod_04052026;'
   
   'UID=sa;'
   #'UID=mis_admin;'
   'PWD=Exim1234;'
   
   'Encrypt=yes;TrustServerCertificate=yes')  # Use if you encounter SSL issues
# amik kat application_master EOD bru dia update col_facilities application master

# #  PROD Connect Database
# connection = pyodbc.connect(
#    'DRIVER={ODBC Driver 17 for SQL Server};'
#    'SERVER=10.20.1.4,1455;'
#    'DATABASE=mis_db_prod;'
#    'UID=efms_admin;'
#    'PWD=Exim1234;'
#    'Encrypt=yes;TrustServerCertificate=yes')  # Use if you encounter SSL issues


LDB_CA = pd.read_sql_query("SELECT * FROM application_master;", connection)
#     LDB_CA['application_id'].value_counts()   primary key
#     LDB_CA['cif_id'].value_counts()


LDB_ACC = pd.read_sql_query("SELECT * FROM col_facilities_application_master;", connection)
#     LDB_ACC['application_id'].value_counts() secondary
#     LDB_ACC['facility_id'].value_counts() primary
#     LDB_ACC['cif_id'].value_counts()
#     LDB_ACC['facility_exim_account_num'].value_counts()

LDB_KEY = pd.read_sql_query("SELECT * FROM account_to_application;", connection)
#     LDB_ACC['application_id'].value_counts() secondary
#     LDB_ACC['facility_id'].value_counts() secondary


Excel3 = Excel2.rename(columns={'Rating at Origination':'Rating_at_Origination'}).merge(LDB_ACC[['facility_exim_account_num',
                                                   'acc_rating_origination',
                                                   'facility_id']].rename(columns={'facility_exim_account_num':'AccountNumber'}),
                                                     on='AccountNumber',
                                                       how='left', indicator="Cross_Check_Tag")

# Extract
writer2 = pd.ExcelWriter("UAT_Update_Rating_at_Origination.xlsx",engine='xlsxwriter')

Excel3.to_excel(writer2, sheet_name='UAT_Testing_Result', index = False)

writer2.close()

#     Excel2.shape
#     LDB_ACC.shape
#     Excel3.shape
#     Excel3._merge.value_counts()

#     Excel3.facility_id.value_counts()
#     Excel3.acc_rating_origination.value_counts()

#     Excel3.iloc[np.where(Excel3._merge=="left_only")]
#     Excel3.iloc[np.where(Excel3.application_id.isna())]

Excel4 = Excel3.merge(LDB_KEY[['facility_id',
                               'application_id']],on='facility_id',how='inner', indicator=True)

#     Excel4.head()
#     Excel4.shape
#     Excel3.shape
#     Excel4.application_id.value_counts()
#     Excel4.iloc[np.where(Excel4.application_id==1386)]

# reportingDate = Excel3["Position as At"].iloc[0]


#=======================================================================================================

Excel5 = Excel4.iloc[np.where(~Excel4.Rating_at_Origination.isna())][['application_id','Rating_at_Origination']].drop_duplicates()

#     Excel5.application_id.value_counts()
#     Excel5.iloc[np.where(Excel5.application_id==1386)]
#     Excel5.iloc[np.where(Excel5.Rating_at_Origination.isna())]

column_types = []
for col in Excel5.columns:
   # You can choose to map column types based on data types in the DataFrame, for example:
   if Excel5[col].dtype == 'object':  # String data type
         column_types.append(f"{col} VARCHAR(255)")
   elif Excel5[col].dtype == 'int64':  # Integer data type
         column_types.append(f"{col} INT")
   elif Excel5[col].dtype == 'float64':  # Float data type
         column_types.append(f"{col} FLOAT")
   else:
         column_types.append(f"{col} VARCHAR(255)")  # Default type for others

cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS A_MAI_PD_RATING")
connection.commit()

# Generate the CREATE TABLE statement
create_table_query = "CREATE TABLE A_MAI_PD_RATING (" + ', '.join(column_types) + ")"
# Execute the query
cursor.execute(create_table_query)

for row in Excel5.iterrows():
   sql = "INSERT INTO A_MAI_PD_RATING({}) VALUES ({})".format(','.join(Excel5.columns), ','.join(['?']*len(Excel5.columns)))
   cursor.execute(sql, tuple(row[1]))
connection.commit()


cursor.execute("""MERGE INTO application_master AS target USING A_MAI_PD_RATING AS source
ON target.application_id = source.application_id
WHEN MATCHED THEN
   UPDATE SET target.rating_origination = source.Rating_at_Origination;
""")
connection.commit() 

cursor.execute("drop table A_MAI_PD_RATING")
connection.commit() 

