# UAT 10.32.1.51 DB ecis09072026
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


proposal = pd.read_sql_query("SELECT * FROM proposal;", connection)

prospect = pd.read_sql_query("SELECT * FROM prospect;", connection)

invoice_split_aging = pd.read_sql_query("SELECT * FROM invoice_split_aging;", connection)

param_system_param = pd.read_sql_query("SELECT * FROM param_system_param;", connection)

ledger = pd.read_sql_query("SELECT * FROM ledger;", connection)

proposal1 = proposal[['proposal_number',
                      'company_no',
                      'ledger_bal',
                      'last_modified_date',
                      'rm_incharge',
                      'approve_status',
                      'recommend_status',
                      'changes_status',
                      'policy_type']].merge(param_system_param[['param_code',
                                                                'param_name']], how='left',
                                                                  left_on='changes_status',
                                                                    right_on='param_code')

proposal2 = proposal1.merge(prospect[['company_no',
                                       'company_name']],
                                         how='left',
                                           left_on='company_no',
                                             right_on='company_no')

proposal3 = proposal2[['proposal_number',
           'company_no',
           'company_name',
           'ledger_bal',
           'last_modified_date',
           'rm_incharge',
           'approve_status',
           'recommend_status',
           'changes_status',
           'param_name',
           'param_code',
           'policy_type']]

# proposal3.proposal_number.value_counts()

invoice_split_aging_pivot = (
    invoice_split_aging
    .pivot_table(
        index=['invoice_number', 'payment_order'],
        columns='param_oth',
        values='invoice_amt',
        aggfunc='sum',
        fill_value=0
    )
    .reset_index()
)

# jdkn param_oth sbgi index
invoice_split_aging_pivot.columns.name = None

invoice_split_aging_pivot.os_fee.fillna(0, inplace=True)
invoice_split_aging_pivot.os_premium.fillna(0, inplace=True)
invoice_split_aging_pivot.os_sstgst.fillna(0, inplace=True)
invoice_split_aging_pivot.os_yeancb.fillna(0, inplace=True)

invoice_split_aging_pivot1 = invoice_split_aging_pivot.groupby(['invoice_number'])[['os_fee','os_premium','os_sstgst','os_yeancb']].sum().reset_index()

# invoice_split_aging_pivot1.invoice_number.value_counts()

# invoice_split_aging_pivot1.iloc[np.where(invoice_split_aging_pivot1['invoice_number'].isin(['IN24120002','IN24110014']))]

ledger1 = ledger.sort_values(by=['proposal_number',
                                 'datetrans'], ascending=[True,False]).drop_duplicates(subset=['proposal_number'], keep='first')

ledger_debit = ledger.groupby(['proposal_number'])[['debit','credit']].sum().reset_index()

ledger2 = ledger1.drop(['debit','credit'],axis=1).merge(ledger_debit, on='proposal_number', how='left')


# ledger1.proposal_number.value_counts()

# ledger_combine.iloc[np.where(ledger_combine['proposal_number'].isin(['P/CPC/00093/2023']))]
# ledger1.iloc[np.where(ledger1['invoice_number'].isin(['IN24120002']))]


combine = proposal3.merge(ledger2, on='proposal_number', how='left').merge(invoice_split_aging_pivot1, on='invoice_number', how='left')

# proposal3.to_excel('aging_report_proposal (proposal3).xlsx', index=False)
# invoice_split_aging_pivot1.to_excel('aging_report_proposal (invoice_split_aging_pivot1).xlsx', index=False)
# ledger1.to_excel('aging_report_proposal (ledger1).xlsx', index=False)
# combine.to_excel('aging_report_proposal (combine new).xlsx', index=False)

combine1 = combine.iloc[np.where(combine['datetrans'].notnull() & combine['policy_number'].isnull())].sort_values(by=['company_name','debit'], ascending=[True,False])

# current_time = pd.Timestamp.now()

# combine1.loc[current_time - combine1.datetrans > pd.Timedelta(days=90), 'aging'] = '0-90 days'


#-----------------------------------------------------------------------------------


# VIEW SQL

# ALTER view [dbo].[view_aging_report_proposal] AS

# WITH proposal1 AS (
#     SELECT
#         p.proposal_number,
#         p.company_no,
#         p.ledger_bal,
#         p.last_modified_date,
#         p.rm_incharge,
#         p.approve_status,
#         p.recommend_status,
#         p.changes_status,
#         p.policy_type,
#         'testing' as param_code,
#         ps.status as param_name
#     FROM proposal p
#     LEFT JOIN proposal_status ps
#         ON p.proposal_number = ps.proposal_number
# ),

# proposal3 AS (
#     SELECT
#         p1.proposal_number,
#         p1.company_no,
#         pr.company_name,
#         p1.ledger_bal,
#         p1.last_modified_date,
#         p1.rm_incharge,
#         p1.approve_status,
#         p1.recommend_status,
#         p1.changes_status,
#         p1.param_name,
#         p1.param_code,
#         p1.policy_type
#     FROM proposal1 p1
#     LEFT JOIN prospect pr
#         ON p1.company_no = pr.company_no
# ),

# invoice_split_aging_pivot AS (
#     SELECT
#         invoice_number,
#         payment_order,

#         SUM(CASE WHEN param_oth = 'os_fee' THEN invoice_amt ELSE 0 END) AS os_fee,
#         SUM(CASE WHEN param_oth = 'os_premium' THEN invoice_amt ELSE 0 END) AS os_premium,
#         SUM(CASE WHEN param_oth = 'os_sstgst' THEN invoice_amt ELSE 0 END) AS os_sstgst,
#         SUM(CASE WHEN param_oth = 'os_yeancb' THEN invoice_amt ELSE 0 END) AS os_yeancb

#     FROM invoice_split_aging
#     GROUP BY
#         invoice_number,
#         payment_order
# ),

# invoice_split_aging_pivot1 AS (
#     SELECT
#         invoice_number,
#         SUM(ISNULL(os_fee, 0)) AS os_fee,
#         SUM(ISNULL(os_premium, 0)) AS os_premium,
#         SUM(ISNULL(os_sstgst, 0)) AS os_sstgst,
#         SUM(ISNULL(os_yeancb, 0)) AS os_yeancb
#     FROM invoice_split_aging_pivot
#     GROUP BY invoice_number
# ),

# ledger_latest AS (
#     SELECT *
#     FROM (
#         SELECT
#             l.*,
#             ROW_NUMBER() OVER (
#                 PARTITION BY l.proposal_number
#                 ORDER BY l.datetrans DESC
#             ) AS rn
#         FROM ledger l
#     ) x
#     WHERE rn = 1
# ),

# ledger_debit AS (
#     SELECT
#         proposal_number,
#         SUM(debit) AS debit,
#         SUM(credit) AS credit
#     FROM ledger
#     GROUP BY proposal_number
# ),

# ledger2 AS (
#     SELECT
#         ll.proposal_number,
#         ll.datetrans,
#         ll.invoice_number,
# 		ll.policy_number,

#         -- include other ledger columns here if needed
#         -- example:
#         -- ll.payment_order,
#         -- ll.description,
#         -- ll.created_date,

#         ld.debit,
#         ld.credit
#     FROM ledger_latest ll
#     LEFT JOIN ledger_debit ld
#         ON ll.proposal_number = ld.proposal_number
# )

# SELECT
#     p3.*,
#     l2.datetrans,
#     l2.invoice_number,
#     l2.debit,
#     l2.credit,
#     l2.policy_number,
#     isa.os_fee,
#     isa.os_premium,
#     isa.os_sstgst,
#     isa.os_yeancb,
# 	EOMONTH(GETDATE(),-1) as statement_date,
# 	case when DATEDIFF(DAY,l2.datetrans,EOMONTH(GETDATE(),-1)) - 30 < 30 then ledger_bal else 0 end as aging_current,
# 	case when DATEDIFF(DAY,l2.datetrans,EOMONTH(GETDATE(),-1)) - 30 >= 30 and DATEDIFF(DAY,l2.datetrans,EOMONTH(GETDATE(),-1)) - 30 < 60 then ledger_bal else 0 end as aging_30days,
# 	case when DATEDIFF(DAY,l2.datetrans,EOMONTH(GETDATE(),-1)) - 30 >= 60 and DATEDIFF(DAY,l2.datetrans,EOMONTH(GETDATE(),-1)) - 30 < 90 then ledger_bal else 0 end as aging_60days,
# 	case when DATEDIFF(DAY,l2.datetrans,EOMONTH(GETDATE(),-1)) - 30 >= 90 and DATEDIFF(DAY,l2.datetrans,EOMONTH(GETDATE(),-1)) - 30 < 120  then ledger_bal else 0 end as aging_90days,
# 	case when DATEDIFF(DAY,l2.datetrans,EOMONTH(GETDATE(),-1)) - 30 >= 120 then ledger_bal else 0 end as aging_120days
# FROM proposal3 p3
# LEFT JOIN ledger2 l2
#     ON p3.proposal_number = l2.proposal_number
# LEFT JOIN invoice_split_aging_pivot1 isa
#     ON l2.invoice_number = isa.invoice_number
# where l2.policy_number is null and l2.datetrans is not null 
# --and p3.proposal_number = 'P/DCT/00022/2026'
# --where p3.proposal_number = 'P/CPC/00093/2023'
# --order by p3.company_name asc, l2.debit desc;
# GO

#-----------------------------------------------------------------------------------


# STORED PROCEDURE SQL

# INSERT INTO view_aging_proposal_history
# SELECT
#     EOMONTH(GETDATE(),-1) AS snapshot_month,
#     *
# FROM view_aging_proposal;


# 1) create view

# As per above

# 2) create table

# SELECT *
# INTO statement_proposal
# FROM dbo.view_aging_report_proposal;

# 3) create stored procedure

# CREATE or alter PROCEDURE dbo.gen_statement_propo
 
# AS
# BEGIN
#     SET NOCOUNT ON;
# 	declare @statement_date date

# 	select @statement_date=max(statement_date) from statement 

#     DELETE FROM dbo.statement_proposal
#     WHERE statement_date = @statement_date;

#     INSERT INTO dbo.statement_proposal
#     (
#           proposal_number
#         , company_no
#         , company_name
#         , ledger_bal
#         , last_modified_date
#         , rm_incharge
#         , approve_status
#         , recommend_status
#         , changes_status
#         , param_name
#         , param_code
#         , policy_type
#         , datetrans
#         , invoice_number
#         , debit
#         , credit
#         , policy_number
#         , os_fee
#         , os_premium
#         , os_sstgst
#         , os_yeancb
#         , statement_date
#         , aging_current
#         , aging_30days
#         , aging_60days
#         , aging_90days
#         , aging_120days
#     )
#     SELECT
#           proposal_number
#         , company_no
#         , company_name
#         , ledger_bal
#         , last_modified_date
#         , rm_incharge
#         , approve_status
#         , recommend_status
#         , changes_status
#         , param_name
#         , param_code
#         , policy_type
#         , datetrans
#         , invoice_number
#         , debit
#         , credit
#         , policy_number
#         , os_fee
#         , os_premium
#         , os_sstgst
#         , os_yeancb
#         , @statement_date
#         , aging_current
#         , aging_30days
#         , aging_60days
#         , aging_90days
#         , aging_120days
#     FROM dbo.view_aging_report_proposal;
# END;


# 4) Jasper

# SELECT *
# FROM statement_proposal
# WHERE 
#  (CONVERT(date, statement_date, 105)  
#  	BETWEEN  (CONVERT(date, $P{date1}, 105) ) AND (CONVERT(date,  $P{date2}, 105)))
#  	AND
#  	 (policy_type LIKE  '%$P!{policy_type}%' OR   $P{policy_type} IS NULL)
#  	AND 
#  	(status LIKE  '%$P!{changes_status}%' OR   $P{changes_status} IS NULL)
#  	AND 
#  	(company_no LIKE  '%$P!{company_no}%' OR  $P{company_no} IS NULL)
# ORDER BY company_no ASC