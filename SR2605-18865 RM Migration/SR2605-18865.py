
import pandas as pd
import numpy as np
import pyodbc

#   Timestamp
current_time = pd.Timestamp.now()

#  Read Excel
link = r"C:\\Users\\syahidhalid\\Syahid_PC\\Analytics - ITD\\00. URS & Test Script\\List of Project - 2026\\3. Analytics BD (Active) - RM Migration (SR2605-18865)"

file = "RM Portfolio (AR Reminder)"

sheet_name = "Main"
#sheet_name = "Loandatabase_Feb2026 (UAT)"

filepath = os.path.join(link, file + ".xlsx")

Excel = pd.read_excel(filepath,header=0, usecols="A:D", sheet_name=sheet_name)


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

#  dptkn cif_id
LDB_CIF = pd.read_sql_query("SELECT * FROM cif_master;", connection)
#     LDB_CIF['cif_id'].value_counts()   primary key

Excel1 = Excel.rename(columns={"Customer Name":"cif_name"}).sort_values(by="cif_name",
              ascending=True).merge(LDB_CIF[["cif_name",
              "cif_id"]].sort_values(by="cif_name",
                                     ascending=True),
                on="cif_name",
                  how="left",
                    indicator="cif_tagging")

LDB_RM = pd.read_sql_query("SELECT * FROM relationship_manager_master;", connection)
#     LDB_RM['rm_id'].value_counts()   primary key
#     LDB_RM['credit_app_id'].value_counts()

#   Sample 1 RM Name from relationship_manager_master
LDB_PARAM1 = pd.read_sql_query("select * from param_system_param where param_id = 32475;", connection)

#   All RM Name
LDB_PARAM2 = pd.read_sql_query("select * from param_system_param where parent_param_id = 32190;", connection)


LDB_CA = pd.read_sql_query("select * from credit_application_master;", connection)

#   Banking Team Code 
LDB_TEAM = pd.read_sql_query("select * from param_system_param where parent_param_id = 32196;", connection)
