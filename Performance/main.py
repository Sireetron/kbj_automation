import pandas as pd
from utils import all_history
import glob
import numpy as np
import pandas as pd
import glob
# import win32com.client as win32
import jaydebeapi
from const import QUERY, CONNECT
import re





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


data_digit1 = pd.read_csv(f'./input/acc_current/Acc_20250301_0830.csv')
data_digit1['Loan No'] = data_digit1['Loan No'].astype(str)
data_digit1 = data_digit1[['Loan No','OverdueDays']]

his = [ ['20250301', '0'],['20250201', '1'],['20250101','2'],['20241201','3'],['20241101','4'],['20241001','5']]
for i in his[0:]:
    print(f"Processing date: {i[0]}")
    print((i[0], i[1]))
    data = all_history(query,i[0], i[1])
    data_digit1 = data_digit1.merge(data, on='Loan No', how='left')
    
    
    
# performane digit2
data_performance = pd.read_csv('./input/performance/performance.csv')
data_digit1['Loan No'] = data_digit1['Loan No'].astype(str)
data_performance['CONTRACT_NO']= data_performance['CONTRACT_NO'].astype(str)
data_all_digit = data_performance.merge(data_digit1, left_on='CONTRACT_NO', right_on='Loan No', how='left')
data_all_digit['AVG_DIGIT1'] = data_all_digit.loc[:, data_all_digit.columns.str.startswith('SCORE_INDEX')].apply(pd.to_numeric, errors='coerce').mean(axis=1).fillna(0).astype(int)
data_all_digit['MOB'] = pd.to_numeric(data_all_digit['MOB'], errors='coerce').fillna(0).astype(int)

# TDH digit2
files = glob.glob("./Input/ar_all/*.*")
df_list = []  # Store individual DataFrames
for file in files:
    print(f"Reading {file}...")
    df = pd.read_csv(file, encoding='cp874', low_memory=False)
    df_list.append(df)
data_tdh = pd.concat(df_list, ignore_index=True)

data_tdh['Loan No'] = data_tdh['Loan No'].astype(str).apply(lambda x: re.sub(r'\D', '', x))
data_tdh = data_tdh.loc[
    (data_tdh['Product'] == 'TL') & 
    (
        data_tdh['Project Code Name'].str.contains('ปรับโครงสร้าง', na=False) | 
        data_tdh['Project Code Name'].str.contains('TDR', na=False) | 
        data_tdh['Project Code Name'].str.contains('DR', na=False)
    )
].reset_index(drop=True)[['Loan No','Project Code Name']]

data_all_digit = data_all_digit.merge(data_tdh, left_on='CONTRACT_NO', right_on='Loan No', how='left')

# Define conditions
conditions = [
    data_all_digit['Project Code Name'].notna(),      # A is not null
    data_all_digit['MOB'] < 7,          # A is less than 7
    data_all_digit['AVG_DIGIT1'] == 3  ,
    data_all_digit['AVG_DIGIT1'] == 2,# C is equal to 3
    data_all_digit['AVG_DIGIT1'] == 1,
    data_all_digit['AVG_DIGIT1'] == 0
]

# Define corresponding values
choices = ['H', 'D', 'H','M','L','L']
data_all_digit['TOTAL_DIGIT1']= np.select(conditions, choices, default='Other')
data_all_digit['TOTAL_DIGIT2'] = data_all_digit['TOTAL_DIGIT2'].map({3: 'H', 2: 'M', 1: 'L'})
data_all_digit['FINAL_SCORE'] =data_all_digit['TOTAL_DIGIT1'].astype(str) + data_all_digit['TOTAL_DIGIT2'].astype(str) +'0'+ data_all_digit['MOB'].astype(str)

print('data_all_digit',data_all_digit)


# map assign
file = glob.glob("./input/assisgn_data/*.xlsx") 
data_assign = pd.read_excel(file[0])
data_assign = data_assign[['Loan No.','Old OA','New OA']]
data_assign['Loan No.'] = data_assign['Loan No.'].astype(str)

# final redult
file_path = file[0].split('\\')[1]
cscore_assigned = data_assign.merge(data_all_digit,left_on='Loan No.',right_on='CONTRACT_NO',how='left')
cscore_assigned.to_csv(f'./output/assign_{file_path}.csv')
print('data_assign',data_assign)