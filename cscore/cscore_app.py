import pandas as pd
from cscore.utils import  transform_files
import glob
import numpy as np
import pandas as pd
import glob
# import win32com.client as win32
import jaydebeapi
import re
import sys
from datetime import datetime
from dotenv import load_dotenv
load_dotenv() 
import os
sys.path.append(os.path.abspath(''))




def all_history(query,date,item) :
    data_mnt = pd.read_csv(f'./cscore/input/acc_history_monthly/{date}')
    # print(f'./input/history/{date}')
    data_mnt['Loan No'] = data_mnt['Loan No'].astype(str)
    data_mnt = data_mnt[['Loan No','OverdueCnt_Morning']].merge(query, left_on='OverdueCnt_Morning', right_on='BUCKET', how='left')
    data_mnt = data_mnt.rename(columns={'BUCKET_SCORE': f'BUCKET_SCORE{item}mnt'})
    # print(f'{date}',data_mnt[[f'BUCKET_SCORE{item}mnt','Loan No']])
    return data_mnt[['Loan No',f'BUCKET_SCORE{item}mnt']]


def read_file(pathfile,filename):
    if filename:
        if filename.endswith(".xlsx"):
            file = pd.read_excel(f'{pathfile}{filename}')
        elif filename.endswith(".csv"):
            encodings = ["utf-8", "ISO-8859-1", "latin1", "utf-16"]
            for enc in encodings:
                try:
                    file = pd.read_csv(f'{pathfile}{filename}', encoding=enc)
                    # print(f"Successfully read {filename} using {enc} encoding.")
                    return file
                except UnicodeDecodeError:
                    print(f"Encoding error with {enc}, trying another...")
            # file = pd.read_csv(f'{pathfile}{filename}', encoding='ISO-8859-1')
        return file  
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





def cscore_app() :
    
    # ===history digit 1====
    conn = jaydebeapi.connect(
              os.getenv("TIBERO_JCLASSNAME"),
         os.getenv("TIBERO_URL"),
        [os.getenv("TIBEERO_USER"), os.getenv("TIBEERO_PASSWORD")],
         os.getenv("TIBERO_JARS"),
            )
    
    cur = conn.cursor() 	

    query = pd.read_sql(f'''
        SELECT * FROM SIREETRON.bucket_score  
        ''', conn) 
    conn.close()
# =======================ตั้งต้น===================================

    file_current = glob.glob("./cscore/input/acc_current/*") 
    file_current = file_current[0].split('\\')[1]
    data_digit1 = read_file('./cscore/input/acc_current/',file_current)
    data_digit1 = clean_column_names(data_digit1)
    # data_digit1 = pd.read_csv(f'./input/acc_current/{file_current}')
    data_digit1['contract_no'] = data_digit1['contract_no'].astype(str)
    data_digit1 = data_digit1[['contract_no']]

    
    files_history = glob.glob("./cscore/input/acc_history_monthly/*.csv") 
    # print(f'file_history :, {files_history} ?? ')


    processed_files = []  # Store modified file names
    for i in files_history:
        # print()
        file = i.split('\\')[-1] 
        # print(file)
        processed_files.append(file)  
    his = transform_files(processed_files)
    # confirmation = input(f"Are you sure? (y/n) : file_6minth history :, {processed_files} ?? ").strip().lower()

    # if confirmation != "y":
    #     sys.exit()
        
    # his = [ ['Acc_20250301_0830.csv', 'Acc_20250301_0830'],['Acc_20250201_0830.csv', 'Acc_20250201_0830']]
    for i in his[0:]:
        # print(f"Processing date: {i[0]}")
        # print((i[0], i[1]))
        data = all_history(query,i[0], i[1])
        data = clean_column_names(data)
        data_digit1 = data_digit1.merge(data, on='contract_no', how='left')
        
        
        
    # performane digit2
    data_performance = pd.read_csv('./cscore/input/performance_peronal_info/performance.csv')
    data_performance = clean_column_names(data_performance)
    # ==============================================================================================================================

    data_digit1['contract_no'] = data_digit1['contract_no'].astype(str)
    data_performance['contract_no']= data_performance['contract_no'].astype(str)
    data_digit1['avg_digit1'] = data_digit1.loc[:, data_digit1.columns.str.startswith('bucket_score')].apply(pd.to_numeric, errors='coerce').sum(axis=1).fillna(0).astype(int)/6
    data_all_digit = data_performance.merge(data_digit1, left_on='contract_no', right_on='contract_no', how='left')
    # data_all_digit['AVG_DIGIT1'] = data_all_digit.loc[:, data_all_digit.columns.str.startswith('SCORE_INDEX')].apply(pd.to_numeric, errors='coerce').mean(axis=1).fillna(0).astype(int)
    data_all_digit['mob'] = pd.to_numeric(data_all_digit['mob'], errors='coerce').fillna(0).astype(int)



    # TDR digit2
    files_tdr = glob.glob("./cscore/input/tdr/*.*")   
    df_list = []  # Store individual DataFrames
    for file in files_tdr:
        # print(f"Reading {file}...")
        path = glob.glob(f"{file}")[0].split('\\')[-1]
        # print(path)
        df = read_file('./cscore/input/tdr/',path)
        df_list.append(df)
        
        
    data_tdr = pd.concat(df_list, ignore_index=True)
    data_tdr = clean_column_names(data_tdr)
    data_tdr['contract_no'] = data_tdr['contract_no'].astype(str).apply(lambda x: re.sub(r'\D', '', x))
    data_tdr = data_tdr.loc[
        (data_tdr['product'] == 'TL') & 
        (
            data_tdr['project_code_name'].str.contains('ปรับโครงสร้าง', na=False) | 
            data_tdr['project_code_name'].str.contains('TDR', na=False) | 
            data_tdr['project_code_name'].str.contains('DR', na=False)
        )
    ].reset_index(drop=True)[['contract_no','project_code_name']]


    # =======merge=========
    data_cscore = data_all_digit.merge(data_tdr, left_on='contract_no', right_on='contract_no', how='left')
    # =======merge=========


    # Define conditions
    conditions = [
        data_cscore['project_code_name'].notna(),      # A is not null
        data_cscore['mob'] < 7,          # A is less than 7
        data_cscore['avg_digit1'] > 3  ,
        data_cscore['avg_digit1'] > 1,# C is equal to 3
        data_cscore['avg_digit1'] >= 0,
    ]




    # Define corresponding values
    choices = ['H', 'D', 'H','M','L']
    data_cscore['total_digit1']= np.select(conditions, choices, default='Other')
    data_cscore['total_digit2'] = data_cscore['total_digit2'].map({3: 'H', 2: 'M', 1: 'L'})
    data_cscore['final_score'] =data_cscore['total_digit1'].astype(str)+ data_cscore['total_digit2'].astype(str) +'0'+ data_cscore['mob'].astype(str)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_cscore.to_csv(f'./cscore/output_backup/all_csore_createat{timestamp}.csv',index=False)
    
    output_dir = "./cscore/output/"
    for file in glob.glob(os.path.join(output_dir, "*")):
        os.remove(file)
    data_cscore.to_csv(f'./cscore/output/all_csore.csv',index=False)




    # map assign
    file_assign = glob.glob("./cscore/input/assign_data/*.xlsx") 
    if len(file_assign)>=1:
        data_assign = pd.read_excel(file_assign[0])
        data_assign = clean_column_names(data_assign)
        data_assign = data_assign[['contract_no']]
        data_assign['contract_no'] = data_assign['contract_no'].astype(str)
        data_cscore['contract_no'] = data_cscore['contract_no'].astype(str)

        # final redult
        file_path =  re.sub(r'\.(csv|xlsx)$', '', file_assign[0].split('\\')[1])
        cscore_assigned = data_assign.merge(data_cscore,left_on='contract_no',right_on='contract_no',how='left')
        # cscore_assigned = cscore_assigned[['contract_no','final_score']]
        cscore_assigned.to_excel(f'./cscore/output_backup/cscore_assigned_{file_path}_createat{timestamp}.xlsx',index=False)
        cscore_assigned.to_excel(f'./cscore/output/cscore_assigned_{file_path}.xlsx',index=False)
