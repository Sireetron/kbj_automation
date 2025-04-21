import pandas as pd
# from cscore.utils import  transform_files
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
from utils import read_file,clean_column_names,all_history,transform_files
sys.path.append(os.path.abspath(''))



def cscore_app() :
    
    # ===history digit 1====
    conn = jaydebeapi.connect(
        os.getenv("ORACLE_JCLASSNAME"),
         os.getenv("ORACLE_URL"),
         [os.getenv("ORACLE_USER"), os.getenv("ORACLE_PASSWORD")],
         os.getenv("ORACLE_JARS"),
        )
    
    cur = conn.cursor() 	

    query = pd.read_sql(f'''
        SELECT * FROM supat.bucket_score  
        ''', conn) 
    # print('query',query)
    data_performance = pd.read_sql(f'''
       WITH contract AS (
        SELECT AS_OF_DATE ,CONTRACT_NO ,NATIONAL_ID ,CONTRACT_DATE ,PRINCIPAL_BAL 
        FROM JFDWH.CONTRACT_INFO_DAILY 
        WHERE AS_OF_DATE = (SELECT MAX(AS_OF_DATE) FROM JFDWH.CONTRACT_INFO_DAILY)-1
        OFFSET 5 ROWS FETCH NEXT 100 ROWS ONLY
        )
        ,
        rawdata AS (
        SELECT c.*,c2.NAME ,c2.SURNAME ,c2.GROSS_INCOME ,c2.DATE_OF_BIRTH ,c2.BUSINESS_TYPE ,c2.OCCUPATION_TYPE,ro.OCCUPATION_NAME  FROM contract c
        LEFT JOIN JFDWH.CUSTOMER c2 ON c2.NATIONAL_ID_NO = c.NATIONAL_ID
        LEFT JOIN REF_OCCUPATION ro ON c2.OCCUPATION_TYPE = ro.ID 
        )
        ,
        data AS (
        SELECT tcc.AS_OF_DATE,tcc.CONTRACT_NO ,tcc.NATIONAL_ID ,tcc.GROSS_INCOME ,
        tcc.OCCUPATION_TYPE ,tcc.OCCUPATION_NAME,
        tcc.CONTRACT_DATE ,floor(MONTHS_BETWEEN(SYSDATE, tcc.CONTRACT_DATE))  AS contract_period,
        FLOOR(MONTHS_BETWEEN(SYSDATE, tcc.DATE_OF_BIRTH) / 12) AS age,
        PRINCIPAL_BAL ,
        CASE WHEN floor(MONTHS_BETWEEN(SYSDATE, tcc.CONTRACT_DATE))  < 7 THEN 6 ELSE 7 END AS MOB,
        CAST(COALESCE(tis.INDEX_SCORE , '1') AS NUMBER) AS digit2income,
            CAST(COALESCE(tas.INDEX_SCORE, '3') AS NUMBER) AS digit2age,
            CAST(COALESCE(tos.INDEX_SCORE, '3') AS NUMBER) AS digit2job
        FROM rawdata tcc 
        LEFT JOIN TEMP_AGE_SCORE tas ON tas.AGE = FLOOR(MONTHS_BETWEEN(SYSDATE, tcc.DATE_OF_BIRTH) / 12) 
        LEFT JOIN TEMP_OCCUPATION_SCORE tos ON tos.OCCUPATION_TYPE  = tcc.OCCUPATION_TYPE
        LEFT JOIN Temp_INCOME_SCORE tis ON tis.INCOME = tcc.GROSS_INCOME
        )
        SELECT t2.*,
        t3.INDEX_SCORE AS TOTAL_DIGIT2
        FROM  data t2
        LEFT JOIN TEMP_DIGIT2_SCORE t3 ON t2.digit2income + t2.digit2age + t2.digit2job = t3.SUMDIGIT  
        ''', conn) 
    # print(data_performance)
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
        data = all_history('./cscore/input/acc_history_monthly/',query,i[0], i[1])
        data = clean_column_names(data)
        data_digit1 = data_digit1.merge(data, on='contract_no', how='left')
        
        
        
    # performane digit2
    # data_performance = pd.read_csv('./cscore/input/performance_peronal_info/performance.csv')
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
