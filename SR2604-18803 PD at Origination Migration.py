import pandas as pd
import numpy as np
import pyodbc

#   Timestamp
current_time = pd.Timestamp.now()

connection = pyodbc.connect(
   'DRIVER={ODBC Driver 17 for SQL Server};'
   'SERVER=10.20.1.4,1455;'
   'DATABASE=mis_db_prod;'
   'UID=efms_admin;'
   'PWD=Exim1234;'
   'Encrypt=yes;TrustServerCertificate=yes')  # Use if you encounter SSL issues

LDB_FTM = pd.read_sql_query("SELECT * FROM col_facilities_application_master;", connection)

LDB_FTM1 = LDB_FTM[['facility_exim_account_num','acc_rating_origination']]

# LDB_FTM[['facility_exim_account_num']].value_counts()

LDB_Hist = pd.read_sql_query("SELECT * FROM dbase_account_hist WHERE position_as_at = (SELECT MAX(position_as_at) FROM dbase_account_hist);", connection)

# LDB_Hist[['position_as_at']].value_counts()

# LDB_Hist[['facility_exim_account_num']].value_counts()

LDB_Hist1 = LDB_Hist[['facility_exim_account_num','cif_name','acc_status']]

param_system_param = pd.read_sql_query("SELECT * FROM param_system_param;", connection)

LDB_merge = LDB_FTM1.merge(LDB_Hist1)
