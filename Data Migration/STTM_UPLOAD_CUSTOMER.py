from pickle import LIST

import pandas as pd
import numpy as np
import pyodbc
import sys


def connect_to_mssql():
    try:
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=10.20.1.4,1455;'
            'DATABASE=mis_db_prod;'
            'UID=mis_admin;'
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
-

# reportingDate = '2026-08-31'

# BG_Hist = pd.read_sql_query("SELECT * FROM cif_master WHERE positionAsAt = ?", connection, params=(reportingDate,))

cif_master = pd.read_sql_query("SELECT * FROM cif_master", connection)

                            # SOURCE_CODE, 
                            # MAINTENANCE_SEQ_NO
STTM_UPLOAD_CUSTOMER = LIST[['CUSTOMER_NO',
                             'CUSTOMER_TYPE']]


# 
#      
# CUSTOMER_NAME1    
# ADDRESS_LINE1     
# ADDRESS_LINE3     
# ADDRESS_LINE2     
# ADDRESS_LINE4     
# COUNTRY    
# SHORT_NAME 
# NATIONALITY
# LANGUAGE   
# EXPOSURE_COUNTRY  
# LOCAL_BRANCH      
# LIABILITY_NO      
# UNIQUE_ID_NAME    
# UNIQUE_ID_VALUE   
# FROZEN     
# DECEASED   
# WHEREABOUTS_UNKNOWN      
# CUSTOMER_CATEGORY 
# HO_AC_NO   
# FX_CUST_CLEAN_RISK_LIMIT 
# OVERALL_LIMIT     
# FX_CLEAN_RISK_LIMIT      
# CREDIT_RATING     
# REVISION_DATE     
# LIMIT_CCY  
# CAS_CUST   
# CONVERSION_STATUS_FLAG   
# ERR_MSG    
# SEC_CUST_CLEAN_RISK_LIMIT
# SEC_CLEAN_RISK_LIMIT     
# SEC_CUST_PSTL_RISK_LIMIT 
# SEC_PSTL_RISK_LIMIT      
# SWIFT_CODE 
# LIAB_BR    
# LIAB_NODE  
# PAST_DUE_FLAG     
# DEFAULT_MEDIA     
# LOC_CODE   
# SHORT_NAME2
# SSN 
# ACTION_CODE
# UTILITY_PROVIDER  
# UTILITY_PROVIDER_ID      
# RISK_PROFILE      
# DEBTOR_CATEGORY   
# UDF_1      
# UDF_2      
# UDF_3      
# UDF_4      
# UDF_5      
# MAILERS_REQUIRED  
# AML_CUSTOMER_GRP  
# AML_REQUIRED      
# GROUP_CODE 
# EXPOSURE_CATEGORY 
# CUST_CLASSIFICATION      
# CIF_STATUS 
# CIF_STATUS_SINCE  
# INTRODUCER 
# FT_ACCTING_AS_OF  
# CUST_UNADVISED    
# LIAB_UNADVISED    
# TAX_GROUP  
# CONSOL_TAX_CERT_REQD     
# INDIVIDUAL_TAX_CERT_REQD 
# FX_NETTING_CUSTOMER      
# CLS_PARTICIPANT   
# CLS_CCY_ALLOWED   
# RISK_CATEGORY     
# FAX_NUMBER 
# EXT_REF_NO 
# CRM_CUSTOMER      
# ISSUER_CUSTOMER   
# TREASURY_CUSTOMER 
# CHARGE_GROUP      
# FULL_NAME  
# MAKER_ID   
# MAKER_DT_STAMP    
# CHECKER_ID 
# CHECKER_DT_STAMP  
# CUST_CLG_GROUP    
# CHK_DIGIT_VALID_REQD     
# ALG_ID     
# SOURCE_SEQ_NO     
# BRANCH_CODE
# STAFF
# KYC_REF_NO
# KYC_DETAIL
# LC_COLLATERAL_PCT
# AR_AP_TRACKING
# AUTO_CREATE_ACCOUNT
# AUTO_CUST_AC_NO
# TRACK_LIMITS
# TAXID_NO
# WITHHOLDING_TAX
# SPECIAL_CUST
# CRS_TYPE
# TAX_CNTRY
# CIF_CREATION_DATE
# MFI_CUSTOMER
# JOINT_VENTURE
# CRS_TYPE
# TAX_CNTRY


