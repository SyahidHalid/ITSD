import pandas as pd
import numpy as np
import pyodbc
import sys


def connect_to_mssql():
    try:
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=10.32.1.51,1455;'
            'DATABASE=ecis09072026;'
            'UID=sa;'
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



proposal = pd.read_sql_query("SELECT * FROM proposal;", connection)

proposal_status = pd.read_sql_query("SELECT * FROM proposal_status;", connection)

prospect = pd.read_sql_query("SELECT * FROM prospect;", connection)

invoice_split_aging = pd.read_sql_query("SELECT * FROM invoice_split_aging;", connection)

ledger = pd.read_sql_query("SELECT * FROM ledger;", connection)



proposal1 = proposal[['proposal_number',
                      'company_no',
                      'ledger_bal',
                      'last_modified_date',
                      'rm_incharge',
                      'approve_status',
                      'recommend_status',
                      'changes_status',
                      'policy_type']].merge(proposal_status[['proposal_number',
                                                             'status']], how='left', left_on='proposal_number', right_on='proposal_number')
# proposal1._status.value_counts()

proposal3 = proposal1.merge(prospect[['company_no',
                                      'company_name']], how='left', left_on='company_no', right_on='company_no',)
# proposal3.proposal_number.value_counts()
# proposal3.iloc[np.where(proposal3['proposal_number']=='P/DCT/00049/2025')]



ledger1 = ledger[['proposal_number','datetrans','invoice_number','policy_number','debit','credit']].drop_duplicates(subset=['proposal_number'], keep='last')
# ledger1.proposal_number.value_counts()
# ledger1.invoice_number.value_counts()

# ledger1.iloc[np.where(ledger1['invoice_number']=='CN24090003')]

proposal4 = proposal3.merge(ledger1, how='left', left_on='proposal_number', right_on='proposal_number')
# proposal4.proposal_number.value_counts()
# proposal4.iloc[np.where(proposal4['proposal_number']=='P/DCT/00049/2025')]




invoice_split_aging1 = invoice_split_aging.drop_duplicates(subset=['invoice_number'], keep='last')
# invoice_split_aging1.iloc[np.where(invoice_split_aging1['invoice_number']=='DN25070002')]

proposal5 = proposal4.merge(invoice_split_aging1, how='left', left_on='invoice_number', right_on='invoice_number')
# proposal5.proposal_number.value_counts()
# proposal5.iloc[np.where(proposal5['proposal_number']=='P/DCT/00049/2025')]


proposal5.rename(columns={'status': 'param_name',
                          'param_oth':'param_code'}, inplace=True)

proposal5.loc[proposal5.param_code == 'os_fee' ,'os_fee'] = proposal5.ledger_bal
proposal5.loc[proposal5.param_code == 'os_premium' ,'os_premium'] = proposal5.ledger_bal
proposal5.loc[proposal5.param_code == 'os_sstgst' ,'os_sstgst'] = proposal5.ledger_bal
proposal5.loc[proposal5.param_code == 'os_yeancb' ,'os_yeancb'] = proposal5.ledger_bal


proposal6 = proposal5[['proposal_number'
      ,'company_no'
      ,'company_name'
      ,'ledger_bal'
      ,'last_modified_date'
      ,'rm_incharge'
      ,'approve_status'
      ,'recommend_status
      ,'changes_status
      ,'param_name
      ,'param_code
      ,'policy_type
      ,'datetrans
      ,'invoice_number
      ,'debit
      ,'credit
      ,'policy_number
      ,'os_fee
      ,'os_premium
      ,'os_sstgst
      ,'os_yeancb
      ,'statement_date
      ,'aging_current
      ,'aging_30days
      ,'aging_60days
      ,'aging_90days'
      ,'aging_120days'
      ,'aging_credit']]

# with proposal1 as (select a.proposal_number,
#                       a.company_no,
# 					  c.company_name,
#                       a.ledger_bal,
#                       a.last_modified_date,
#                       a.rm_incharge,
#                       a.approve_status,
#                       a.recommend_status,
#                       a.changes_status,
# 					  b.status,
#                       a.policy_type from proposal a
# 					  left join proposal_status b
# 					  ON a.proposal_number = b.proposal_number
# 					  left join prospect c
# 					  ON a.company_no = c.company_no),
# ledger1 as (select ledger_id,
# 					proposal_number,
# 					datetrans,
# 					invoice_number,
# 					policy_number,
# 					row_number() over (partition by proposal_number order by ledger_id desc) as rn 
# 					from ledger),
# ledger2 as (select * from ledger1
# 					where rn=1),
# proposal2 as (select a.proposal_number,
#                       a.company_no,
# 					  a.company_name,
#                       a.ledger_bal,
#                       a.last_modified_date,
#                       a.rm_incharge,
#                       a.approve_status,
#                       a.recommend_status,
#                       a.changes_status,
# 					  a.status,
#                       a.policy_type,
# 					  b.ledger_id,
# 					  b.datetrans,
# 					  b.invoice_number,
# 					  b.policy_number from proposal1 as a
# 							left join ledger2 b
# 							on a.proposal_number = b.proposal_number),
# invoice1 as (select invoice_number,
# 					param_oth,
# 					invoice_amt,
# 					payment_order,
# 					ROW_NUMBER() OVER (ORDER BY invoice_number) AS row_id 
# 					from invoice_split_aging),
# invoice2 as (select *,
# 					row_number() over (partition by invoice_number order by row_id desc) as rn
# 					from invoice1),
# invoice3 as (select * from invoice2
# 					where rn = 1),
# proposal3 as (select a.proposal_number,
#                       a.company_no,
# 					  a.company_name,
#                       a.ledger_bal,
#                       a.last_modified_date,
#                       a.rm_incharge,
#                       a.approve_status,
#                       a.recommend_status,
#                       a.changes_status,
# 					  a.status,
#                       a.policy_type,
# 					  a.ledger_id,
# 					  a.datetrans,
# 					  a.invoice_number,
# 					  a.policy_number,
# 					  b.param_oth,
# 					  b.invoice_amt,
# 					  b.payment_order,
# 					  b.row_id,
# 					  b.rn from proposal2 a
# 							left join invoice3 b
# 							on a.invoice_number = b.invoice_number)
# select * from proposal3 where invoice_number = 'DN25070002'