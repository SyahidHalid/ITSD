import pandas as pd
import numpy as np
import pyodbc
import xlsxwriter

#  UAT
connection = pyodbc.connect(
   'DRIVER={ODBC Driver 17 for SQL Server};'
   
   #'SERVER=10.32.1.52,1455;'
   'SERVER=10.20.1.4,1455;'

   #'DATABASE=mis_db_prod23022025;'
   'DATABASE=mis_db_prod;'
   
   #'UID=sa;'
   'UID=mis_admin;'
   'PWD=Exim1234;'
   
   'Encrypt=yes;TrustServerCertificate=yes')  # Use if you encounter SSL issues
# amik kat application_master EOD bru dia update col_facilities application master


info_schema = pd.read_sql_query("SELECT TABLE_NAME, COLUMN_NAME, IS_NULLABLE, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'col_facilities_application_master' ORDER BY ORDINAL_POSITION;", connection)


info_facility_exim_account_num = pd.read_sql_query("SELECT TABLE_NAME, COLUMN_NAME,	IS_NULLABLE, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME = 'facility_exim_account_num'	ORDER BY TABLE_NAME;", connection)
