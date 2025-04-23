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
from datetime import datetime

from dotenv import load_dotenv
load_dotenv() 


sys.path.append(os.path.abspath(''))

def checker():
    
    # try:
    #     conn_tibero = jaydebeapi.connect(
    #         os.getenv("TIBERO_JCLASSNAME"),
    #         os.getenv("TIBERO_URL"),
    #         [os.getenv("TIBERO_USER"), os.getenv("TIBERO_PASSWORD")],
    #         os.getenv("TIBERO_JARS")
    #     )
    #     tibero_test = pd.read_sql("SELECT 1 FROM DUAL", conn_tibero)
    #     print("Tibero Test Query Result:")
    #     print(tibero_test)
    # except Exception as e:
    #     print("Error connecting to Tibero:", e)
    # finally:
    #     if 'conn_tibero' in locals():
    #         conn_tibero.close()
    
    
    
    try:
        conn_oracle = jaydebeapi.connect(
            os.getenv("ORACLE_JCLASSNAME"),
            os.getenv("ORACLE_URL"),
            [os.getenv("ORACLE_USER"), os.getenv("ORACLE_PASSWORD")],
            os.getenv("ORACLE_JARS")
        )
        sms_type = pd.read_sql("SELECT * FROM SUPAT.REF_SMS_WORDING", conn_oracle)
        # print("Oracle SMS Type Query Result:")
        # print(sms_type)
    
        today_str = datetime.today().strftime('%Y-%m-%d')
        print('today_str',today_str)
        csv_path = f'./checker/input/customer_input/customer_{today_str}.csv'

        if os.path.exists(csv_path):
            print("Loading data from CSV...")
            
            customer = pd.read_csv(csv_path, dtype={
                'MOBILE_PHONE_NO_VAL': str,
                'NATIONAL_ID': str,
                'CONTRACT_NO_VAL': str
            })
        else:
            print("Querying database...")
            customer = pd.read_sql(f'''
                WITH data_contract AS (
                    SELECT cid.AS_OF_DATE,
                        cid.CONTRACT_NO AS CONTRACT_NO_VAL,
                        cid.NATIONAL_ID,
                        cid.MONTHLY_INST_AMT,
                        cid.FIRST_DUE_DATE 
                    FROM jfdwh.CONTRACT_INFO_DAILY cid 
                    WHERE AS_OF_DATE = (SELECT MAX(AS_OF_DATE) FROM JFDWH.CONTRACT_INFO_DAILY)
                )
                SELECT dc.*, 
                    c.MOBILE_PHONE_NO AS MOBILE_PHONE_NO_VAL
                FROM data_contract dc
                LEFT JOIN JFDWH.CUSTOMER c ON dc.NATIONAL_ID = c.NATIONAL_ID_NO
            ''', conn_oracle, dtype={
                'MOBILE_PHONE_NO_VAL': str,
                'NATIONAL_ID': str,
                'CONTRACT_NO_VAL': str
            })

            # Save to CSV
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            customer.to_csv(csv_path, index=False)
            # print('customer',customer)
    except Exception as e:
        print("Error connecting to Oracle:", e)
    finally:
        if 'conn_oracle' in locals():
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
    )
    assign_delay_merge = assign_delay_merge.drop(columns=['last4digit_val'])



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



    assign_delay_merge['sms_wording'] =assign_delay_merge.apply(
        lambda row: row['sms_wording'].replace("{totalunpaidbalance}", str(row['overduesumamt']))
        if "{totalunpaidbalance}" in row['sms_wording'] else row['sms_wording'],
        axis=1
    )

    assign_delay_merge.to_excel('./checker/output/smscheck.xlsx', index=False)
    # with ExcelWriter('./checker/input/assign_input/Template SMS SF+ non assign 17042025 (BASE).xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    #     assign_delay_merge.to_excel(writer, sheet_name='check', index=False)
    
