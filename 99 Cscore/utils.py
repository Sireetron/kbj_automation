
import pandas as pd
# from utils import select_min_pay, read_input_file, export_file
# import glob
# import numpy as np
import pandas as pd
# import glob
# import logging
# import win32com.client as win32
# import os
# import jaydebeapi
# from const import QUERY, CONNECT
# import oracledb
# import getpass
# import json
import re

def all_history(query,date,item) :
    data_mnt = pd.read_csv(f'./input/acc_history_monthly/{date}')
    # print(f'./input/history/{date}')
    data_mnt['Loan No'] = data_mnt['Loan No'].astype(str)
    data_mnt = data_mnt[['Loan No','OverdueCnt_Morning']].merge(query, left_on='OverdueCnt_Morning', right_on='BUCKET', how='left')
    data_mnt = data_mnt.rename(columns={'BUCKET_SCORE': f'BUCKET_SCORE{item}mnt'})
    return data_mnt[['Loan No',f'BUCKET_SCORE{item}mnt']]

def transform_files(files):
    files.sort(reverse=True)
    latest_files = files
    return [[file,  re.sub(r'\.csv$', '', file)] for file in latest_files]



def read_file(pathfile,filename):
    if filename:
        if filename.endswith(".xlsx"):
            file = pd.read_excel(f'{pathfile}{filename}')
        elif filename.endswith(".csv"):
            encodings = ["utf-8", "ISO-8859-1", "latin1", "utf-16"]
            for enc in encodings:
                try:
                    file = pd.read_csv(f'{pathfile}{filename}', encoding=enc)
                    print(f"Successfully read {filename} using {enc} encoding.")
                    return file
                except UnicodeDecodeError:
                    print(f"Encoding error with {enc}, trying another...")
            # file = pd.read_csv(f'{pathfile}{filename}', encoding='ISO-8859-1')
        # return file  
    # print(assign.head())  # Display first few rows
    else:
        print("No file found in the folder.")
    
def clean_column_names(df):
    df.columns = df.columns.str.lower()  # Convert to lowercase
    df.columns = df.columns.str.replace(r'\.', '', regex=True)
    df.columns = df.columns.str.replace(r' ', '_', regex=True)  # Replace non-alphanumeric characters with underscores
    df.columns = df.columns.str.replace('customer_id_no|customer_no|customer_id|national_id', 'customer_no', regex=True)  # Replace variations with 'customer_no'
    df.columns = df.columns.str.replace(r'loan_no', 'contract_no', regex=True)
    df.columns = df.columns.str.replace(r'mobile.*', 'mobile_no', regex=True)
    df.columns = df.columns.str.replace(r'customer_name/surname\(thai\)', 'customer_name', regex=True)  # Replace 'customer_name/surname(thai)' with 'customer_name'
    return df    