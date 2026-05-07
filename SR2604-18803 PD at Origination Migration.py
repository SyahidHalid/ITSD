
import pandas as pd
import numpy as np
import pyodbc

#   Timestamp
current_time = pd.Timestamp.now()

#  Read Excel
link = r"C:\\Users\\syahidhalid\\Syahid_PC\Analytics - ITD\\00. URS & Test Script\\List of Project - 2026\\BD (Active) - PD Rating Migration (SR2604-18803)"

file = "Loandatabase_Feb2026 (Rating) (ITSD)"

#sheet_name = "Loandatabase_Feb2026"
sheet_name = "Loandatabase_Feb2026 (UAT)"

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
#  Excel2["AccountNumber"].value_counts()


#  UAT
connection = pyodbc.connect(
   'DRIVER={ODBC Driver 17 for SQL Server};'
   'SERVER=10.32.1.52,1455;'
   'DATABASE=mis_db_prod;'
   'UID=sa;'
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


# LDB_CA = pd.read_sql_query("SELECT * FROM application_master;", connection)
#     LDB_CA['application_id'].value_counts()   primary key
#     LDB_CA['cif_id'].value_counts()


LDB_ACC = pd.read_sql_query("SELECT * FROM col_facilities_application_master;", connection)
#     LDB_ACC['application_id'].value_counts() secondary
#     LDB_ACC['facility_id'].value_counts() primary
#     LDB_ACC['cif_id'].value_counts()
#     LDB_ACC['facility_exim_account_num'].value_counts()


Excel3 = Excel2[["AccountNumber","Rating at Origination","Position as At"]].merge(LDB_ACC[['facility_exim_account_num','acc_rating_origination','application_id']].rename(columns={'facility_exim_account_num':'AccountNumber'}), on='AccountNumber', how='left', indicator=True)
#     Excel2.shape
#     LDB_ACC.shape
#     Excel3.shape
#     Excel3._merge.value_counts()
#     Excel3.application_id.value_counts()
reportingDate = "Position as At"

column_types = []
for col in Excel3.columns:
   # You can choose to map column types based on data types in the DataFrame, for example:
   if Excel3[col].dtype == 'object':  # String data type
         column_types.append(f"{col} VARCHAR(255)")
   elif Excel3[col].dtype == 'int64':  # Integer data type
         column_types.append(f"{col} INT")
   elif Excel3[col].dtype == 'float64':  # Float data type
         column_types.append(f"{col} FLOAT")
   else:
         column_types.append(f"{col} VARCHAR(255)")  # Default type for others

cursor.execute("DROP TABLE IF EXISTS A_MAI_PD_RATING")
connection.commit()

# Generate the CREATE TABLE statement
create_table_query = "CREATE TABLE A_MAI_PD_RATING (" + ', '.join(column_types) + ")"
# Execute the query
cursor.execute(create_table_query)

for row in Excel3.iterrows():
   sql = "INSERT INTO A_MAI_PD_RATING({}) VALUES ({})".format(','.join(Excel3.columns), ','.join(['?']*len(appendfinal1.columns)))
   cursor.execute(sql, tuple(row[1]))
connection.commit()


cursor.execute("""MERGE INTO application_master AS target USING A_MAI_PD_RATING AS source
ON target.application_id = source.application_id
WHEN MATCHED AND target.position_as_at = ? THEN
   UPDATE SET target.acc_credit_loss_laf_ecl = source.LAF_ECL_FC,
      target.acc_credit_loss_laf_ecl_myr = source.LAF_ECL_MYR,
      target.acc_credit_loss_cnc_ecl = source.CnC_ECL_FC,
      target.acc_credit_loss_cnc_ecl_myr = source.CnC_ECL_MYR,
      target.acc_credit_loss_acc_receiv_ecl = source.AR_ECL_FC,
      target.acc_credit_loss_acc_receiv_ecl_myr = source.AR_ECL_MYR;
""", (reportingDate,))
conn.commit() 

cursor.execute("drop table A_MAI_PD_RATING")
conn.commit() 








LDB_Hist = pd.read_sql_query("SELECT * FROM dbase_account_hist WHERE position_as_at = (SELECT MAX(position_as_at) FROM dbase_account_hist);", connection)

# LDB_Hist[['position_as_at']].value_counts()

# LDB_Hist[['facility_exim_account_num']].value_counts()

LDB_Hist1 = LDB_Hist[['facility_exim_account_num','cif_name','acc_status']]

param_system_param = pd.read_sql_query("SELECT * FROM param_system_param;", connection)

LDB_merge = LDB_FTM1.merge(LDB_Hist1)
