import pandas as pd
import glob
import re
from datetime import datetime, timedelta




df = pd.read_excel('./input/loan/save_04042568.xlsx')
start = pd.read_excel('./input/start_due/start_due.xlsx')
df = df.merge(start,left_on='loan_no',right_on='Loan No.',how='left')[['loan_no','Overdue days(Morning)']]
csv_files =glob.glob("./input/ar/*.csv")

def transform_files(files):
    files.sort(reverse=True)
    latest_files = files
    return [[file,  re.sub(r'\.csv$', '', file)] for file in latest_files]

def all_history(path,item) :
    data_mnt = pd.read_csv(f'./input/ar/{path}')
    # print(f'./input/history/{date}')
    data_mnt['Loan No'] = data_mnt['Loan No'].astype(str)
    data_mnt = data_mnt[['Loan No','OverdueDays_Morning']]
    data_mnt['OverdueDays_Morning'] = data_mnt['OverdueDays_Morning'].astype('Int64')
    # data_mnt = query.merge(data_mnt, left_on='loan_no', right_on='Loan No', how='left')
    data_mnt = data_mnt.rename(columns={'OverdueDays_Morning': f'OverdueDays{item}mnt'})
    return data_mnt[['Loan No',f'OverdueDays{item}mnt']]

def find_stamp_date(row):
    for i in range(len(date_cols) - 1):
        if row[date_cols[i + 1]] < row[date_cols[i]]:
            return date_cols[i + 1]
    return ""

def subtract_one_day(date_str):
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    new_date_obj = date_obj - timedelta(days=1)
    return new_date_obj.strftime("%Y%m%d")



processed_files = []  # Store modified file names
for i in csv_files:
    # print()
    file = i.split('\\')[-1] 
    # print(file)
    processed_files.append(file)  
his = transform_files(processed_files)

sorted_data = sorted(his, key=lambda x: x[0], reverse=False)

# Print result
# for item in sorted_data:
#     print(item)
    
df['loan_no'] = df['loan_no'].astype(str)


for i in sorted_data[0:]:
    # print(f"Processing date: {i[0]}")
    # print((i[0], i[1]))
    data = all_history(i[0], i[1])
    # data = clean_column_names(data)
    df = df.merge(data, left_on='loan_no',right_on = 'Loan No', how='left')
    df.drop(columns=['Loan No'], inplace=True)
    
date_cols = df.columns[1:] 

df["insertdate"] = df.apply(find_stamp_date, axis=1)
df["insertdate"] = df['insertdate'].apply(lambda x: re.search(r'OverdueDaysAcc_(.*?)_0830mnt', x).group(1) if re.search(r'OverdueDaysAcc_(.*?)_0830mnt', x) else None)
df['insertdate'] = df['insertdate'].apply(subtract_one_day)
df.to_excel('./output/save_mar.xlsx',index=False)