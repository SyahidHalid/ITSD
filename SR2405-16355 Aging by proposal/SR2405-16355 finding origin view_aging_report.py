
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
a = pd.read_sql_query("SELECT * FROM statement;", connection)
#   a.head(5)
#   a.dtypes
#   a.policy_number.value_counts()
#   a.iloc[np.where(a.policy_number=="CTS/00049/05/2012")].statement_date.value_counts()

# prospect table
# primary prospect_id
b = pd.read_sql_query("SELECT * FROM prospect;", connection)
#   b.head(5)
#   b.dtypes
#   b.company_no.value_counts()
#   b.iloc[np.where(b.company_no=="0000000002")].statement_date.value_counts()

ab = a.merge(b,on='company_no',how='left',indicator='ab')
#   a.shape
#   b.shape
#   ab.shape
#   ab.ab.value_counts()

#-----------------------------------------------------------------------------------

# 1 policy 1 proposal
bb = pd.read_sql_query("SELECT * FROM proposal_latest;", connection)
#   bb.head(5)
#   bb.dtypes
#   bb.proposal_number.value_counts()
#   bb.policy_number.value_counts()

abbb = ab.merge(bb,on='policy_number',how='left',indicator='abbb')
#   ab.shape
#   bb.shape
#   abbb.abbb.value_counts()

#-----------------------------------------------------------------------------------

# primary proposal_id
c = pd.read_sql_query("SELECT * FROM proposal;", connection)
#   c.head(5)
#   c.dtypes
#   c.proposal_number.value_counts()
#   c.iloc[np.where(a.policy_number=="CTS/00049/05/2012")].statement_date.value_counts()

abbbc = abbb.merge(c,on='proposal_number',how='left',indicator='abbbc', suffixes = ("","_abbbc"))
#   abbb.shape
#   abbbc.shape
#   abbbc.abbbc.value_counts()

#-----------------------------------------------------------------------------------

# primary policy
f = pd.read_sql_query("SELECT * FROM policy_status;", connection)
#   f.head(5)
#   f.dtypes
#   f.policy_number.value_counts()

abbbcf = abbbc.merge(f,on='policy_number',how='left',indicator='abbbcf', suffixes = ("","_abbbcf"))
#   abbbc.shape
#   abbbcf.shape
#   abbbcf.abbbcf.value_counts()

#-----------------------------------------------------------------------------------

# buat calculation statement a
gg1 = a[['statement_id',
        'aging_current',
        'aging_30days',
        'aging_60days',
        'aging_90days',
        'aging_120days',
        'total_credit']]

gg1['total'] = (gg1['aging_current'].fillna(0) + 
                gg1['aging_30days'].fillna(0) + 
                gg1['aging_60days'].fillna(0) + 
                gg1['aging_90days'].fillna(0) + 
                gg1['aging_120days'].fillna(0)) + gg1['total_credit'].fillna(0)

gg = gg1[['statement_id',
         'total']]

abbbcfgg = abbbcf.merge(gg,on='statement_id',how='left',indicator='abbbcfgg', suffixes = ("","_abbbcfgg"))
#   abbbcf.shape
#   abbbcfgg.shape
#   abbbcfgg.abbbcfgg.value_counts()

#-----------------------------------------------------------------------------------

os = pd.read_sql_query("SELECT * FROM statement_os_amt;", connection)
#   os.head(5)
#   os.dtypes
#   os.policy_number.value_counts()
#   os.iloc[np.where(os.policy_number=="CTS/00049/05/2012")].statement_date.value_counts()

abbbcfggos = abbbcfgg.merge(os,on=['policy_number',
                                   'statement_date',
                                   'company_no'],how='left',indicator='abbbcfggos', suffixes = ("","_abbbcfggos"))


connection.close()


#   abbbcfggos.shape
#   abbbcfggos.abbbcfggos.value_counts()

#-----------------------------------------------------------------------------------



# a1 = a[['policy_number',
#         'aging_current',
#         'aging_30days',
#         'aging_60days',
#         'aging_90days',
#         'aging_120days',
#         'total_debit',
#         'total_credit',
#         'statement_date']]

# a1['aging_current_f'] = a1['aging_current'].apply(
#     lambda x: f"{x:,.2f}" if x != 0 else "0.00"
# )
# a1['aging_30days_f'] = a1['aging_30days'].apply(
#     lambda x: f"{x:,.2f}" if x != 0 else "0.00"
# )
# a1['aging_60days_f'] = a1['aging_60days'].apply(
#     lambda x: f"{x:,.2f}" if x != 0 else "0.00"
# )
# a1['aging_90days_f'] = a1['aging_90days'].apply(
#     lambda x: f"{x:,.2f}" if x != 0 else "0.00"
# )
# a1['aging_120days_f'] = a1['aging_120days'].apply(
#     lambda x: f"{x:,.2f}" if x != 0 else "0.00"
# )
# a1['total_debit_f'] = a1['total_debit'].apply(
#     lambda x: f"{x:,.2f}" if x != 0 else "0.00"
# )
# a1['total_credit_f'] = a1['total_credit'].apply(
#     lambda x: f"{x:,.2f}" if x != 0 else "0.00"
# )
# a1['statement_date_f'] = a1['statement_date'].apply(
#     lambda x: x.strftime('%d-%m-%Y') if pd.notna(x) else '0.00'
# )
# #   a1.dtypes

# b1 = b[['company_no',
#         'company_name']]


# c1 = c[['policy_type',
#         'proposal_number',
#         'ledger_bal',
#         'rm_incharge']]


# f1 = f[['status']]

# gg = pd.read_sql_query("SELECT * FROM statement;", connection)

# gg1 = gg[[]]

# gg['statement_date_f'] = a1['statement_date'].apply(
#     lambda x: x.strftime('%d-%m-%Y') if pd.notna(x) else '0.00'
# )



#-----------------------------------------------------------------------------------

#   Aging

# begin

# declare @decreturn as decimal(18,2)
# declare @total_credit as decimal(18,2)
# declare @systemdate as date
# set @systemdate=@valdate

# select @decreturn=a.balance_to_date
# from(   select 
#         a.policy_number,a.company_no,a.status,a.ledger_bal ,
#         case when a.ledger_bal <=0  then 0 
#         --when a.balance_to_date <=0  then 0 
#         else a.balance_to_date
#         end as balance_to_date
#         , case when a.balance_to_date < 0 then a.balance_to_date else 0 end total_credit
#         from (
#                 select a.policy_number,a.company_no,a.status,a.ledger_bal,sum(balance_to_date) as balance_to_date 
#                 from(
#                         select a.policy_number,a.company_no,a.balance_to_date,
#                         case when a.total_day>=0 and a.total_day <=30 then 'aging_current' 
#                         when a.total_day>=31 and a.total_day <=60 then 'aging_30days' 
#                         when a.total_day>=61 and a.total_day <=90 then 'aging_60days' 
#                         when a.total_day>=91 and a.total_day <=120 then 'aging_90days' 
#                         when a.total_day < 0  then 'na' 
#                         else 'aging_120days' 
#                         end as status 
#                         ,a.ledger_bal
#                         from
#                         (
#                             select a.*,
#                             datediff(day,a.invoice_date,@systemdate)as total_day,
#                             b.invoice_balance as balance_to_date 
#                             ,c.ledger_bal
#                             from [dbo].[invoice_debitcreditnote] a
#                             left outer join [dbo].[invoice_balance_net] b on a.invoice_number=b.invoice_number
#                             left outer join policy_detail c on a.policy_number=c.policy_number
#                         ) a 
#                             ) a group by a.policy_number,a.company_no,a.status,a.ledger_bal 
#                                 ) a 
#                                     ) a where a.status=@valstatus and a.policy_number=@policy_number and a.company_no=@company_number



# --print @dectreturn
# if @decreturn is null
# set @decreturn=0.00

# return @decreturn

# end



# Recreate

# select 
# a.policy_number,a.company_no,a.status,a.ledger_bal ,
# case when a.ledger_bal <=0  then 0 
# --when a.balance_to_date <=0  then 0 
# else a.balance_to_date
# end as balance_to_date
# , case when a.balance_to_date < 0 then a.balance_to_date else 0 end total_credit
# from (
# select a.policy_number,a.company_no,a.status,a.ledger_bal,sum(balance_to_date) as balance_to_date 
# from(
# select a.policy_number,a.company_no,a.balance_to_date,
# case when a.total_day>=0 and a.total_day <=30 then 'aging_current' 
# when a.total_day>=31 and a.total_day <=60 then 'aging_30days' 
# when a.total_day>=61 and a.total_day <=90 then 'aging_60days' 
# when a.total_day>=91 and a.total_day <=120 then 'aging_90days' 
# when a.total_day < 0  then 'na' 
# else 'aging_120days' 
# end as status 
# ,a.ledger_bal
# from
# (
# SELECT 
# a.*,
# DATEDIFF(DAY, a.invoice_date, GETDATE()) AS total_day,
# b.invoice_balance AS balance_to_date,
# c.ledger_bal
# FROM dbo.invoice_debitcreditnote AS a
# LEFT JOIN dbo.invoice_balance_net AS b 
# ON a.invoice_number = b.invoice_number
# LEFT JOIN dbo.policy_detail AS c 
# ON a.policy_number = c.policy_number
# ) a 
# ) a group by a.policy_number,a.company_no,a.status,a.ledger_bal 
# ) a