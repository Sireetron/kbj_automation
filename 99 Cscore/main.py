import pandas as pd
from utils import all_history, transform_files
import glob
import numpy as np
import pandas as pd
import glob
# import win32com.client as win32
import jaydebeapi
from const import QUERY, CONNECT
import re
import sys

# history digit 1
conn = jaydebeapi.connect(
        CONNECT.DB,
        CONNECT.PORT,
        CONNECT.USER,
        CONNECT.CNN,
        )
cur = conn.cursor()  

query = pd.read_sql(f'''
      SELECT * FROM SIREETRON.bucket_score  
    ''', conn) 
conn.close()


file_current = glob.glob("./input/acc_current/*.csv") 
file_current = file_current[0].split('\\')[1]
# print(f'file_oa_current :, {file_current} ?? ')


data_digit1 = pd.read_csv(f'./input/acc_current/{file_current}')
data_digit1['Loan No'] = data_digit1['Loan No'].astype(str)
data_digit1 = data_digit1[['Loan No']]


files_history = glob.glob("./input/acc_history_monthly/*.csv") 
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
    data_digit1 = data_digit1.merge(data, on='Loan No', how='left')
    
    
    
# performane digit2
data_performance = pd.read_csv('./input/performance/performance.csv')
data_digit1['Loan No'] = data_digit1['Loan No'].astype(str)
data_performance['CONTRACT_NO']= data_performance['CONTRACT_NO'].astype(str)
data_digit1['AVG_DIGIT1'] = data_digit1.loc[:, data_digit1.columns.str.startswith('BUCKET_SCORE')].apply(pd.to_numeric, errors='coerce').sum(axis=1).fillna(0).astype(int)/6
data_all_digit = data_performance.merge(data_digit1, left_on='CONTRACT_NO', right_on='Loan No', how='left')
# data_all_digit['AVG_DIGIT1'] = data_all_digit.loc[:, data_all_digit.columns.str.startswith('SCORE_INDEX')].apply(pd.to_numeric, errors='coerce').mean(axis=1).fillna(0).astype(int)
data_all_digit['MOB'] = pd.to_numeric(data_all_digit['MOB'], errors='coerce').fillna(0).astype(int)



# TDH digit2
files_tdr = glob.glob("./Input/ar_all/*.*")
# confirmation = input(f"Are you sure? (y/n) : file_files_tdr :,  {files_tdr} ?? ").strip().lower()
# if confirmation != "y":
#     sys.exit()


df_list = []  # Store individual DataFrames
for file in files_tdr:
    # print(f"Reading {file}...")
    df = pd.read_csv(file, encoding='cp874', low_memory=False)
    df_list.append(df)
data_tdr = pd.concat(df_list, ignore_index=True)

data_tdr['Loan No'] = data_tdr['Loan No'].astype(str).apply(lambda x: re.sub(r'\D', '', x))
data_tdr = data_tdr.loc[
    (data_tdr['Product'] == 'TL') & 
    (
        data_tdr['Project Code Name'].str.contains('ปรับโครงสร้าง', na=False) | 
        data_tdr['Project Code Name'].str.contains('TDR', na=False) | 
        data_tdr['Project Code Name'].str.contains('DR', na=False)
    )
].reset_index(drop=True)[['Loan No','Project Code Name']]


# =======merge=========
data_cscore = data_all_digit.merge(data_tdr, left_on='CONTRACT_NO', right_on='Loan No', how='left')
# =======merge=========

# print('data_cscore', data_cscore['AVG_DIGIT1'])

# Define conditions
conditions = [
    data_cscore['Project Code Name'].notna(),      # A is not null
    data_cscore['MOB'] < 7,          # A is less than 7
    data_cscore['AVG_DIGIT1'] > 3  ,
    data_cscore['AVG_DIGIT1'] > 1,# C is equal to 3
    data_cscore['AVG_DIGIT1'] >= 0,
]

# Define corresponding values
choices = ['H', 'D', 'H','M','L']
data_cscore['TOTAL_DIGIT1']= np.select(conditions, choices, default='Other')
data_cscore['TOTAL_DIGIT2'] = data_cscore['TOTAL_DIGIT2'].map({3: 'H', 2: 'M', 1: 'L'})
data_cscore['FINAL_SCORE'] =data_cscore['TOTAL_DIGIT1'].astype(str)+ data_cscore['TOTAL_DIGIT2'].astype(str) +'0'+ data_cscore['MOB'].astype(str)





# map assign
file_assign = glob.glob("./input/assign_data/*.xlsx") 
# confirmation = input(f"Are you sure? (y/n) : file_assign :, {file_assign}  ?? ").strip().lower()

# if confirmation != "y":
#     sys.exit()
    
    
data_assign = pd.read_excel(file_assign[0])
data_assign = data_assign[['Loan No.','Old OA','New OA','Overdue Months Division Code']]
data_assign['Loan No.'] = data_assign['Loan No.'].astype(str)



# final redult
file_path = file_assign[0].split('\\')[1]
cscore_assigned = data_assign.merge(data_cscore,left_on='Loan No.',right_on='CONTRACT_NO',how='left')
cscore_assigned.to_csv(f'./output/cscore_assigned_{file_path}.csv')
# print('data_assign',data_assign)