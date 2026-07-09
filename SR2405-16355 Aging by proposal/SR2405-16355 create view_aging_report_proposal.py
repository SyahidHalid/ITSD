
# import packages

import pandas as pd
import numpy as np
import pyodbc
import sys

#-----------------------------------------------------------------------------------

#  Database connection 

def connect_to_mssql():
    try:
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=10.20.1.27,1455;'
            'DATABASE=ecis;'
            'UID=ecis_admin;'
            'PWD=Exim1234;'
            'Encrypt=yes;TrustServerCertificate=yes'
        )

        print("Connected to MSSQL database successfully.")
        
        return connection

    except Exception as e:
        print(f"Error connecting to MSSQL database: {e}")
        sys.exit(1)

connection = connect_to_mssql()

cursor = connection.cursor()

# #  List of database exist in 10.20.1.27,1455
# cursor.execute("SELECT name FROM sys.databases")

# for row in cursor.fetchall():
#     print(row.name)


# #  Use one of the db in the list
# cursor.execute("USE ecis")


# #  List of table exist in 10.20.1.27,1455
# cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")

# for row in cursor.fetchall():
#     print(row.TABLE_NAME)

#-----------------------------------------------------------------------------------


# policy transaction
# primary statement_id
# secondary company_no
proposal = pd.read_sql_query("SELECT * FROM proposal;", connection)
#   proposal.head(5)
#   proposal.dtypes
#   proposal.proposal_number.value_counts()
#   proposal.iloc[np.where(proposal.policy_number == 'CTS/00006/04/2025')].sort_values(by='date_of_proposal', ascending=False)





