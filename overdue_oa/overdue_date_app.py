import pandas as pd
import glob
import re
from datetime import datetime, timedelta
from utils import read_file,transform_files,clean_column_names,all_history



def overdue_date_app():
    
    
    file_current = glob.glob("./overdue_oa/input/loan/*") 
    file_current = file_current[0].split('\\')[1]
    loan = read_file('./overdue_oa/input/loan/',file_current)
    loan = clean_column_names(loan)
    
    # loan = pd.read_excel('./overdue_oa/input/loan/save_04042568.xlsx')
    file_current_start = glob.glob("./overdue_oa/input/start_due/*") 
    file_current_start = file_current_start[0].split('\\')[1]
    start = read_file('./overdue_oa/input/start_due/',file_current_start)
    start = clean_column_names(start)
    # start = pd.read_excel('./overdue_oa/input/start_due/start_due.xlsx')
    
    
    
    df = loan.merge(start,on='contract_no',how='left')[['contract_no','overdue_days(morning)']]
    
    acc =glob.glob("./overdue_oa/input/acc/*.csv")

    def transform_files(files):
        files.sort(reverse=True)
        latest_files = files
        return [[file,  re.sub(r'\.csv$', '', file)] for file in latest_files]

    def all_history(path,item) :
        data_mnt = pd.read_csv(f'./overdue_oa/input/acc/{path}')
        # print(f'./input/history/{date}')
        data_mnt['Loan No'] = data_mnt['Loan No'].astype(str)
        data_mnt = data_mnt[['Loan No','OverdueDays_Morning']]
        data_mnt['OverdueDays_Morning'] = data_mnt['OverdueDays_Morning'].astype('Int64')
        # data_mnt = query.merge(data_mnt, left_on='loan_no', right_on='Loan No', how='left')
        data_mnt = data_mnt.rename(columns={'OverdueDays_Morning': f'OverdueDays{item}mnt'})
        return data_mnt[['Loan No',f'OverdueDays{item}mnt']]

    def find_stamp_date(row):
        for i in range(len(date_cols) - 1):
            val_current = row[date_cols[i]]
            val_next = row[date_cols[i + 1]]

            if pd.isna(val_current) or pd.isna(val_next):
                continue 

            if val_next < val_current:
                return date_cols[i + 1]

        return ""

    def subtract_one_day(date_str):
        date_obj = datetime.strptime(date_str, "%Y%m%d")
        new_date_obj = date_obj - timedelta(days=1)
        return new_date_obj.strftime("%Y%m%d")


    processed_files = []  # Store modified file names
    for i in acc:
        # print()
        file = i.split('\\')[-1] 
        # print(file)
        processed_files.append(file)  
    his = transform_files(processed_files)

    sorted_data = sorted(his, key=lambda x: x[0], reverse=False)

    # Print result
    # for item in sorted_data:
    #     print(item)
        
    df['contract_no'] = df['contract_no'].astype(str)


    for i in sorted_data[0:]:
        # print(f"Processing date: {i[0]}")
        print((i[0], i[1]))
        data = all_history(i[0], i[1])
        # data = clean_column_names(data)
        df = df.merge(data, left_on='contract_no',right_on = 'Loan No', how='left')
        df.drop(columns=['Loan No'], inplace=True)
        
    date_cols = df.columns[1:] 
    # print('df',df)

    df["insertdate"] = df.apply(find_stamp_date, axis=1)
    df["insertdate"] = df['insertdate'].apply(
    lambda x: re.search(r'OverdueDaysAcc_(.*?)_0830mnt', x).group(1) 
    if pd.notna(x) and re.search(r'OverdueDaysAcc_(.*?)_0830mnt', x) 
    else None)
    df['insertdate'] = df['insertdate'].apply(lambda x: subtract_one_day(x) if pd.notna(x) else None)
    df.to_excel('./overdue_oa/output/output.xlsx',index=False)