import os
import pandas as pd
import glob
import pandas as pd
import glob
import numpy as np
import pandas as pd
import glob
import jaydebeapi
import re
import sys
from pandas import ExcelWriter
sys.path.append(os.path.abspath(''))
from const import  CONNECT_ORACLE



    
    
def clean_column_names(df):
    df.columns = df.columns.str.lower()  
    df.columns = df.columns.str.replace(r'\.', '', regex=True)
    df.columns = df.columns.str.replace(r' ', '_', regex=True)  
    df.columns = df.columns.str.replace('customer_id_no|customer_no|customer_id|national_id', 'customer_no', regex=True) 
    df.columns = df.columns.str.replace(r'loan_no|loan', 'contract_no', regex=True)
    df.columns = df.columns.str.replace(r'mobile.*', 'mobile_no', regex=True)
    df.columns = df.columns.str.replace(r'customer_name/surname\(thai\)', 'customer_name', regex=True)  
    return df

def checker():
    conn = jaydebeapi.connect(
        CONNECT_ORACLE.jclassname,
        CONNECT_ORACLE.url,
        CONNECT_ORACLE.jars,
        CONNECT_ORACLE.lib,
        )
    cur = conn.cursor() 	
    sms_type = pd.read_sql(f'''
    SELECT * FROM SUPAT.REF_SMS_WORDING ''', conn) 


    customer = pd.read_sql(f'''
            WITH data_contract AS (
        SELECT cid.AS_OF_DATE , cid.CONTRACT_NO AS CONTRACT_NO_val
        , cid.NATIONAL_ID AS NATIONAL_ID  ,cid.MONTHLY_INST_AMT ,cid.FIRST_DUE_DATE 
        FROM jfdwh.CONTRACT_INFO_DAILY cid 
        WHERE AS_OF_DATE =  (SELECT MAX(AS_OF_DATE) FROM JFDWH.CONTRACT_INFO_DAILY) -1
         OFFSET 5 ROWS FETCH NEXT 100 ROWS ONLY
        )
        SELECT dc.*,
        c.MOBILE_PHONE_NO AS MOBILE_PHONE_NO_val   FROM JFDWH.data_contract dc
        LEFT JOIN JFDWH.CUSTOMER c ON dc.NATIONAL_ID  =c.NATIONAL_ID_NO ''', conn,dtype={'MOBILE_PHONE_NO_VAL': str, 
                                                                    'NATIONAL_ID': str, 
                                                                    'CONTRACT_NO_VAL': str}) 
    print('customer',customer)
    conn.close()


    
    input_folder = "./checker/input/assign_input/"
    files = glob.glob(os.path.join(input_folder, "*.xlsx")) + glob.glob(os.path.join(input_folder, "*.csv"))
    # print('files',files)
    if files:
        file_path = files[0]
        if file_path.endswith(".xlsx"):
            assign = pd.read_excel(file_path,sheet_name='Data', dtype={'MobileNo': str})
            # print('assignassignassign',assign)
        elif file_path.endswith(".csv"):
            assign = pd.read_csv(file_path,sheet_name='Data', dtype={'MobileNo': str})   
    else:
        print("No file found in the folder.")


    # //////////////////*********************************************/////////////////////************************ #




    # print('sms_type',sms_type)
    sms_type = clean_column_names(sms_type)

    # //////////////////*********************************************/////////////////////************************

    
    customer.columns = customer.columns.str.lower()  


    # //////////////////*********************************************/////////////////////************************
    assign_delay = clean_column_names(assign)
    assign_delay = assign_delay.merge(sms_type,left_on='sms_type',right_on = 'sms_type', how='left')
    assign_delay['contract_no'] = assign_delay['contract_no'].astype(str)
    customer['contract_no_val'] = customer['contract_no_val'].astype(str)
    assign_delay_merge = assign_delay.merge(customer, left_on= 'contract_no', right_on='contract_no_val', how='left')

    # //////////////////*********************************************/////////////////////************************


    assign_delay_merge['mobile_check'] = assign_delay_merge.apply(
        lambda row: True if row['mobile_no'] == row['mobile_phone_no_val'] else row['mobile_phone_no_val'],
        axis=1
    )
    assign_delay_merge['last4digit_val'] = assign_delay_merge['contract_no'].str[-4:]
    assign_delay_merge['sms_wording'] =  assign_delay_merge.apply(
        lambda row: row['sms_wording'].replace("{4digit}", str(row['last4digit_val']))
        if "{4digit}" in row['sms_wording'] else row['sms_wording'],
        axis=1
    )
    assign_delay_merge['4_digit'] = assign_delay_merge['4_digit'].astype(str)
    assign_delay_merge['last4digit_val'] = assign_delay_merge['last4digit_val'].astype(str)
    assign_delay_merge['4digit_check'] = assign_delay_merge.apply(
        lambda row: True if row['4_digit'] == row['last4digit_val']  else row['last4digit_val'],
        axis=1
    ).drop(columns=['last4digit_val'])


    # //////////////////*********************************************/////////////////////************************
    ar_file = pd.read_csv('./checker/input/acc/Acc_20250417_0830.csv')
    ar_file['Loan No'] = ar_file['Loan No'].astype(str)
    ar_file =ar_file[['Loan No','OverdueSumAmt']]
    assign_delay_merge = assign_delay_merge.merge(ar_file,left_on='contract_no',right_on="Loan No",how='left').drop(columns=['Loan No'])

    # //////////////////*********************************************/////////////////////************************



    assign_delay_merge['sms_wording'] =assign_delay_merge.apply(
        lambda row: row['sms_wording'].replace("{totalunpaidbalance}", str(row['OverdueSumAmt']))
        if "{totalunpaidbalance}" in row['sms_wording'] else row['sms_wording'],
        axis=1
    )

    assign_delay_merge.to_excel('./checker/output/smscheck.xlsx')
    # with ExcelWriter('./checker/input/assign_input/Template SMS SF+ non assign 17042025 (BASE).xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    #     assign_delay_merge.to_excel(writer, sheet_name='check', index=False)
    
