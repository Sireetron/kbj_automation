import pandas as pd
import glob
import numpy as np
import re
pd.set_option('display.float_format', '{:.0f}'.format)




def clean_column_names(df):
    df.columns = df.columns.str.lower()  # Convert to lowercase
    df.columns = df.columns.str.replace(r'\.', '', regex=True)
    df.columns = df.columns.str.replace(r' ', '_', regex=True)  # Replace non-alphanumeric characters with underscores
    df.columns = df.columns.str.replace('customer_id_no|customer_no|customer_id|national_id', 'customer_no', regex=True)  # Replace variations with 'customer_no'
    df.columns = df.columns.str.replace(r'loan_no|contract.*', 'contract_no', regex=True)
    df.columns = df.columns.str.replace(r'mobile.*', 'mobile_no', regex=True)
    df.columns = df.columns.str.replace(r'customer_name/surname\(thai\)', 'customer_name', regex=True)  # Replace 'customer_name/surname(thai)' with 'customer_name'
    return df

def read_file(pathfile,filename):
    if filename:
        if filename.endswith(".xlsx"):
            file = pd.read_excel(f'{pathfile}{filename}')
        elif filename.endswith(".csv"):
            file = pd.read_csv(f'{pathfile}{filename}')
        return file  
    # print(assign.head())  # Display first few rows
    else:
        print("No file found in the folder.")



for i in glob.glob("./input/assigned/*")  :
    assigned_path  = i.split('\\')[-1] 
    oa_proportion = read_file('./input/assigned/',assigned_path)
    # oa_proportion = pd.read_csv(f'./input/assigned/{assigned_path}')
    oa_proportion = clean_column_names(oa_proportion)
    
    ar_path = glob.glob("./input/AR/*")[0].split('\\')[-1]  
    ar = read_file('./input/AR/',ar_path)
    ar_path_name = re.sub(r'\.csv$', '', ar_path)  
    # ar = pd.read_csv(f'./input/AR/{ar_path}')
    ar = clean_column_names(ar)

    # loan_count = ar['Loan No'].nunique()
    # loan_balance_sum = ar['Loan Balance'].sum()
    # print(f'loan_count : {loan_count}  , loan_balance_sum : {loan_balance_sum}')
    # oa_proportion['portion_loancount'] =  ((oa_proportion['proportion'] / 100) * loan_count).apply(np.ceil)
    # oa_proportion['portion_loanbalance'] =  ((oa_proportion['proportion'] / 100) * loan_balance_sum).apply(np.ceil)
    
    
    ar['oa_assigned'] = np.random.choice(oa_proportion['oa'],size=ar['contract_no'].count(),   p=oa_proportion['proportion'])
    ar.to_csv(f'./output/oa_distribution_{ar_path_name}.csv')
    # print('oa_proportion',oa_proportion)