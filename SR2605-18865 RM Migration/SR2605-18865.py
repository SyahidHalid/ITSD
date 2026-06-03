
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
   #'DATABASE=mis_db_prod;'
   
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

Excel1 = Excel.rename(columns={"Customer Name":"cif_name"}).sort_values(by="cif_name", ascending=True).merge(LDB_CIF[["cif_name","cif_id"]].sort_values(by="cif_name",ascending=True),
                on="cif_name",
                  how="left",
                    indicator="cif_tagging")
#   Excel1.cif_tagging.value_counts()
#   Excel1.iloc[np.where(Excel1.cif_tagging=="left_only")]
#   Excel1.cif_id.value_counts()


#   dptkn credit_app_id
LDB_CA = pd.read_sql_query("select * from credit_application_master;", connection)

Excel2 = Excel1.merge(LDB_CA[["cif_id","credit_app_id"]],
                on="cif_id",
                  how="left",
                    indicator="ca_tagging")
#   Excel2.ca_tagging.value_counts()
#   Excel2.iloc[np.where(Excel2.ca_tagging=="left_only")]
#   Excel2.credit_app_id.value_counts()

# Excel1.shape
# Excel2.shape
# Excel2.head()

def NOB(GROUP):
    if (GROUP=="Corporate Banking"):
        return 37476
    elif (GROUP=="SME & Specialized Financing"): 
        return 36651
    elif (GROUP=="Commercial Banking"): 
        return 36905
    elif (GROUP == 'RON'): 
        return 36480
    elif (GROUP == 'EMRO'): 
        return 36467
    elif (GROUP == 'ROS'): 
        return 36255
    else: 
        return ""
Excel2['rm_banking_team'] = Excel2.apply(lambda x: NOB(x['GROUP']), axis=1)
#   Excel2.GROUP.value_counts()
#   Excel2.rm_banking_team.value_counts()
    # SELECT a.rm_team_banking,b.param_name FROM relationship_manager_master a
    # left join param_system_param b on  a.rm_team_banking=b.param_id
    # group by a.rm_team_banking,b.param_name


def NOB1(RM):
    if (RM=="Asyraf")|(RM=="Asyraf / Naser"):
        return 36468
    elif (RM=="Addina"): 
        return 36807
    elif (RM=="Dazman"): 
        return 36479
    # elif (RM == 'Farisha'): 
    #     return 
    elif (RM == 'Fhairoldillah'): 
        return 37466
    elif (RM == 'Helmi'): 
        return 36251
    elif (RM == 'May Ling'): 
        return 36252
    elif (RM == 'Qistina'): 
        return 37099
    elif (RM == 'Shafuan'): 
        return 37474
    elif (RM == 'Mirza'): 
        return 37367
    elif (RM == 'Muiz'): 
        return 36465
    elif (RM == 'Nurin')|(RM=="Nurin / Naser"): 
        return 32485
    elif (RM == 'Irwan'): 
        return 36483
    elif (RM == 'Thanni'): 
        return 36628
    elif (RM == 'Naqhib'): 
        return 37426
    elif (RM == 'Zara')|(RM == 'Farisha'): 
        return 37427
    elif (RM == 'Patrick'): 
        return 37090
    elif (RM == 'Yuzni'): 
        return 36638
    elif (RM == 'Soleha'): 
        return 36813
    else: 
        return ""
Excel2['rm_name'] = Excel2.apply(lambda x: NOB1(x['RM']), axis=1)
#   Excel2.RM.value_counts()
#   Excel2.rm_name.value_counts()
    # SELECT a.rm_name,b.param_name FROM relationship_manager_master a
    # left join param_system_param b on  a.rm_name=b.param_id
    # where b.param_name like '%Addina%'
    # group by a.rm_name,b.param_name


# #   Sample 1 RM Name from relationship_manager_master
# LDB_PARAM1 = pd.read_sql_query("select * from param_system_param where param_id = 32475;", connection)


# #   All RM Name
# LDB_PARAM2 = pd.read_sql_query("select * from param_system_param where parent_param_id = 32190;", connection)


# #   Banking Team Code 
# LDB_TEAM = pd.read_sql_query("select * from param_system_param where parent_param_id = 32196;", connection)


# to update
LDB_RM = pd.read_sql_query("SELECT * FROM relationship_manager_master;", connection)
#     LDB_RM['rm_id'].value_counts()   primary key
#     LDB_RM['credit_app_id'].value_counts()

#   dptkn rm_id
Excel3 = Excel2.merge(LDB_RM[["credit_app_id","rm_id"]],
                on="credit_app_id",
                  how="left",
                    indicator="rm_tagging")
#   Excel3.rm_tagging.value_counts()
#   Excel3.iloc[np.where(Excel3.rm_tagging=="left_only")].credit_app_id.value_counts()
#   Excel3.head()


#   Excel3.rm_id.value_counts()
#   Excel3.rm_name.value_counts()
#   Excel3.rm_banking_team.value_counts()
#   Excel3.credit_app_id.value_counts()
#   Excel3.cif_id.value_counts()


#   PARAM
PARAM = pd.read_sql_query("select * from param_system_param;", connection)

Excel_name = Excel3.merge(PARAM[["param_id","param_name"]].rename(columns={'param_id':'rm_name'}),on="rm_name",how="left",indicator="param_tagging")
#   Excel_name.param_tagging.value_counts()


# Extract
writer2 = pd.ExcelWriter("UAT_Update_RM.xlsx",engine='xlsxwriter')

Excel_name.to_excel(writer2, sheet_name='UAT_Testing_Result', index = False)

writer2.close()


#=======================================================================================================

# Excel5.to_excel("writer5.xlsx", sheet_name='a', index = False)
# Excel3.to_excel("writer3.xlsx", sheet_name='a', index = False)
# Excel3.iloc[np.where(Excel3.rm_name.isna())]

Excel5 = Excel3[["rm_id","rm_banking_team","rm_name"]].fillna(0).drop_duplicates()
# Excel3.shape
# Excel5.shape
# Excel3.rm_id.value_counts()
# Excel5.rm_id.value_counts()

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


cursor.execute("""MERGE INTO relationship_manager_master AS target USING A_MAI_PD_RATING AS source
ON target.rm_id = source.rm_id
WHEN MATCHED THEN
   UPDATE SET target.rm_team_banking = source.rm_banking_team,
               target.rm_name = source.rm_name;
""")
connection.commit() 

cursor.execute("drop table A_MAI_PD_RATING")
connection.commit() 



#=======================================================================================================


    # Planning column inspectionI’m considering using Python to search for specific columns that 
    # could relate to profitability, such as interest income, fees, and expected credit loss, to 
    # clean the data effectively.

    # import pandas as pd, re
    # hdr_df = pd.read_excel(r'D:\00. Git Repository\Power-BI\Product Development Dashboard\(Pure) loanDatabaseReport_28052026_102803.xlsx', sheet_name='Page 1', header=5, engine='openpyxl')
    # cols = list(hdr_df.columns)
    # patterns = ['interest','profit','fee','margin','rate','yield','ftp','cost of fund','ecl','impair','provision','write','recover','penalt','commission','charge','income','expense']
    # matched = {p:[c for c in cols if re.search(p, str(c), re.IGNORECASE)] for p in patterns}
    # {k:len(v) for k,v in matched.items()}


# It seems like I'm preparing to send a Python call to display a list related to financial terms like interest and income.

# import pandas as pd, re
# hdr_df = pd.read_excel(r'D:\00. Git Repository\Power-BI\Product Development Dashboard\(Pure) loanDatabaseReport_28052026_102803.xlsx', sheet_name='Page 1', header=5, engine='openpyxl')
# cols=list(hdr_df.columns)
# def show(p):
#     return [c for c in cols if re.search(p,str(c),re.I)]
# for p in ['interest','profit','margin','rate','ecl','penalt','charge','income','write','impair']:
#     print('\n',p,'\n',*show(p),sep='\n- ')

