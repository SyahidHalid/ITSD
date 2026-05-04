import pandas as pd
import numpy as np
import pyodbc

#   Timestamp
current_time = pd.Timestamp.now()

#  Read Excel
link = r"C:\\Users\\syahidhalid\\Syahid_PC\Analytics - ITD\\00. URS & Test Script\\List of Project - 2026\\BD (Active) - PD Rating Migration (SR2604-18803)"

file = "Loandatabase_Feb2026 (Rating) (ITSD)"

filepath = os.path.join(link, file + ".xlsx")

Excel = pd.read_excel(filepath,header=5, usecols="B:FH")

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

# UAT
connection = pyodbc.connect(
   'DRIVER={ODBC Driver 17 for SQL Server};'
   'SERVER=10.32.1.52,1455;'
   'DATABASE=mis_db_prod;'
   'UID=sa;'
   'PWD=Exim1234;'
   'Encrypt=yes;TrustServerCertificate=yes')  # Use if you encounter SSL issues
# amik kat application_master EOD bru dia update col_facilities application master

#  PROD Connect Database
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
