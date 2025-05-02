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
from utils import read_file,clean_column_names
from datetime import datetime, timedelta,date
import oracledb

from dotenv import load_dotenv
load_dotenv() 


sys.path.append(os.path.abspath(''))

def checker():
    

    try:
        conn_oracle = oracledb.connect(
                        user=os.getenv("ORACLE_USER"),
                        password=os.getenv("ORACLE_PASSWORD"),
                        dsn=os.getenv("DSN"),
                        mode=oracledb.DEFAULT_AUTH
                    )
        cursor = conn_oracle.cursor()
        
        # jaydebeapi.connect(
        #     os.getenv("ORACLE_JCLASSNAME"),
        #     os.getenv("ORACLE_URL"),
        #     [os.getenv("ORACLE_USER"), os.getenv("ORACLE_PASSWORD")],
        #     os.getenv("ORACLE_JARS")
        # )
        sms_type = pd.read_sql("SELECT * FROM SUPAT.REF_SMS_WORDING", conn_oracle)
        # today_str = datetime.today().strftime('%Y-%m-%d')
        # csv_path = f'./checker/input/customer_input/customer_{today_str}.csv'

        # if os.path.exists(csv_path):
        #     print("Loading data from CSV...")
            
        #     customer = pd.read_csv(csv_path, dtype={
        #         'MOBILE_PHONE_NO_VAL': str,
        #         'NATIONAL_ID': str,
        #         'CONTRACT_NO_VAL': str
        #     })
        # else:
        #     print("Querying database...")
        #     customer = pd.read_sql(
        #       '''WITH data_contract AS (
        #             SELECT cid.AS_OF_DATE,
        #                 cid.CONTRACT_NO AS CONTRACT_NO_VAL,
        #                 cid.NATIONAL_ID,
        #                 cid.MONTHLY_INST_AMT AS MONTHLY_INST_AMT_VAL,
        #                 cid.FIRST_DUE_DATE 
        #             FROM jfdwh.CONTRACT_INFO_DAILY cid 
        #             WHERE AS_OF_DATE = (SELECT MAX(AS_OF_DATE) FROM JFDWH.CONTRACT_INFO_DAILY)
        #         )
        #         SELECT dc."AS_OF_DATE",dc."CONTRACT_NO_VAL",dc."NATIONAL_ID",dc."MONTHLY_INST_AMT_VAL",dc."FIRST_DUE_DATE", 
        #             c.MOBILE_PHONE_NO AS MOBILE_PHONE_NO_VAL
        #         FROM data_contract dc
        #         LEFT JOIN JFDWH.CUSTOMER c ON dc.NATIONAL_ID = c.NATIONAL_ID_NO'''
        #     , conn_oracle, dtype={
        #         'MOBILE_PHONE_NO_VAL': str,
        #         'NATIONAL_ID': str,
        #         'CONTRACT_NO_VAL': str
        #     })
        #     os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        #     customer.to_csv(csv_path, index=False)
        #     print('customer',customer)
    except Exception as e:
        print("Error connecting to Oracle:", e)
    finally:
        if 'conn_oracle' in locals():
            cursor.close()
            conn_oracle.close()
    
    
    
    input_folder = "./checker/input/assign_input/"
    files = glob.glob(os.path.join(input_folder, "*.xlsx")) + glob.glob(os.path.join(input_folder, "*.csv"))
    # print('files',files)
    if files:
        file_path = files[0]
        if file_path.endswith(".xlsx"):
            assign = pd.read_excel(file_path,sheet_name='Data', dtype={'mobile_no': str, '4_digit': str})
            # print('assignassignassign',assign)
        elif file_path.endswith(".csv"):
            assign = pd.read_csv(file_path,sheet_name='Data', dtype={'mobile_no': str, '4_digit': str})   
    else:
        print("No file found in the folder.")


    # //////////////////*********************************************/////////////////////************************ #




    # print('sms_type',sms_type)
    sms_type = clean_column_names(sms_type)

    # //////////////////*********************************************/////////////////////************************

    customer_file_name = glob.glob("./checker/input/customer_input/*") 
    customer_file_name = customer_file_name[0].split('\\')[1]
    customer = read_file('./checker/input/customer_input/',customer_file_name)
    customer = clean_column_names(customer)
    
    
    customer = pd.read_csv('./checker/input/customer_input/customer.csv', dtype={
                'MOBILE_PHONE_NO_VAL': str,
                'NATIONAL_ID': str,
                'CONTRACT_NO_VAL': str
            })
    customer.columns = customer.columns.str.lower()  


    # //////////////////*********************************************/////////////////////************************
    
    assign_delay = clean_column_names(assign)
    assign_delay = assign_delay.merge(sms_type,left_on='sms_type',right_on = 'sms_type', how='left')
    assign_delay['contract_no'] = assign_delay['contract_no'].astype(str)
    customer['contract_no_val'] = customer['contract_no_val'].astype(str)
    customer['monthly_inst_amt_val'] = customer['monthly_inst_amt_val'].apply(lambda x: int(x) if pd.notna(x) else pd.NA).astype('Int64')
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
    assign_delay_merge['sms_wording'] =  assign_delay_merge.apply(
        lambda row: row['sms_wording'].replace("{monthly_inst}", str(row['monthly_inst_amt_val']))
        if "{monthly_inst}" in row['sms_wording'] else row['sms_wording'],
        axis=1
    )
    
    today = date.today()
    first_this_month = today.replace(day=1)
    next_month = first_this_month + timedelta(days=32)
    payment_date_due = next_month.replace(day=1)
    # print('payment_date_due',payment_date_due)
    
    assign_delay_merge['sms_wording'] =  assign_delay_merge.apply(
    lambda row: row['sms_wording'].replace("{paymentdatedue}", str(payment_date_due))
    if "{paymentdatedue}" in row['sms_wording'] else row['sms_wording'],
    axis=1
    )
    
    
    # assign_delay_merge['4_digit'] = assign_delay_merge['4_digit'].astype(str)
    # assign_delay_merge['last4digit_val'] = assign_delay_merge['last4digit_val'].astype(str)
    # assign_delay_merge['4digit_check'] = assign_delay_merge.apply(
    #     lambda row: True if row['4_digit'] == row['last4digit_val']  else row['last4digit_val'],
    #     axis=1
    # )
    
    if '4_digit' in assign_delay_merge.columns :
        assign_delay_merge['4_digit'] = assign_delay_merge['4_digit'].astype(str)
        assign_delay_merge['last4digit_val'] = assign_delay_merge['last4digit_val'].astype(str)

        assign_delay_merge['4digit_check'] = assign_delay_merge.apply(
            lambda row: True if row['4_digit'] == row['last4digit_val'] else row['last4digit_val'],
            axis=1
        )
    else:
        print("One or both of the required columns ('4_digit', 'last4digit_val') are missing.")

    
    
    # assign_delay_merge = assign_delay_merge.drop(columns=['last4digit_val'])



    # //////////////////*********************************************/////////////////////************************
    file_current = glob.glob("./checker/input/acc/*") 
    file_current = file_current[0].split('\\')[1]
    ar_file = read_file('./checker/input/acc/',file_current)
    ar_file.columns = ar_file.columns.str.lower()
    # ar_file = pd.read_csv('./checker/input/acc/Acc_20250417_0830.csv')
    ar_file['loan no'] = ar_file['loan no'].astype(str)
    ar_file =ar_file[['loan no','overduesumamt']]
    assign_delay_merge = assign_delay_merge.merge(ar_file,left_on='contract_no',right_on="loan no",how='left').drop(columns=['loan no'])

    # //////////////////*********************************************/////////////////////************************
    
    if 'ar_today' in assign_delay_merge.columns:
        assign_delay_merge['sumamt_check'] = assign_delay_merge.apply(
        lambda row: True if row['ar_today'] == row['overduesumamt']  else row['overduesumamt'],
        axis=1)
    else:
        print(" missing.")
    
    if 'monthly_inst_amt' in assign_delay_merge.columns:
        assign_delay_merge['monthly_inst_amt_val_check'] = assign_delay_merge.apply(
        lambda row: True if row['monthly_inst_amt'] == row['monthly_inst_amt_val']  else row['monthly_inst_amt_val'],
        axis=1)
    else:
        print(" missing.")



    assign_delay_merge['sms_wording'] =assign_delay_merge.apply(
        lambda row: row['sms_wording'].replace("{totalunpaidbalance}", str(row['overduesumamt']))
        if "{totalunpaidbalance}" in row['sms_wording'] else row['sms_wording'],
        axis=1
    )

    assign_delay_merge.to_excel('./checker/output/smscheck.xlsx', index=False)
    # with ExcelWriter('./checker/input/assign_input/Template SMS SF+ non assign 17042025 (BASE).xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    #     assign_delay_merge.to_excel(writer, sheet_name='check', index=False)
    
