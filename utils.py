import pandas as pd
import glob
import logging
import win32com.client as win32
import os
import jaydebeapi
from datetime import datetime
import re
import numpy as np








def transform_files(files):
    files.sort(reverse=True)
    latest_files = files
    return [[file,  re.sub(r'\.csv$', '', file)] for file in latest_files]




def clean_column_names(df):
    df.columns = df.columns.str.lower()  
    df.columns = df.columns.str.replace(r'\.', '', regex=True)
    df.columns = df.columns.str.replace(r' ', '_', regex=True)  
    df.columns = df.columns.str.replace('customer_id_no|customer_no|customer_id|national_id', 'customer_no', regex=True) 
    df.columns = df.columns.str.replace(r'loan_no', 'contract_no', regex=True)
    df.columns = df.columns.str.replace(r'mobile.*', 'mobile_no', regex=True)
    df.columns = df.columns.str.replace(r'customer_name/surname\(thai\)', 'customer_name', regex=True)  
    return df


def read_file(pathfile,filename):
    if filename:
        if filename.endswith(".xlsx"):
            file = pd.read_excel(f'{pathfile}{filename}')
        elif filename.endswith(".csv"):
            encodings = ["utf-8", "ISO-8859-1", "latin1", "utf-16"]
            for enc in encodings:
                try:
                    file = pd.read_csv(f'{pathfile}{filename}')
                    # print(f"Successfully read {filename} using {enc} encoding.")
                    return file
                except UnicodeDecodeError:
                    print(f"Encoding error with {enc}, trying another...")
            # file = pd.read_csv(f'{pathfile}{filename}', encoding='ISO-8859-1')
        return file  
    # print(assign.head())  # Display first few rows
    else:
        print("No file found in the folder.")
        
        
def all_history(path,query,date,item) :
    # print('start')
    data_mnt = pd.read_csv(f'{path}{date}')
    # print(f'./input/history/{date}')
    # print(data_mnt)
    data_mnt['Loan No'] = data_mnt['Loan No'].astype(str)
    data_mnt = data_mnt[['Loan No','OverdueCnt_Morning']].merge(query, left_on='OverdueCnt_Morning', right_on='BUCKET', how='left')
    data_mnt = data_mnt.rename(columns={'BUCKET_SCORE': f'BUCKET_SCORE{item}mnt'})
    # print(f'{date}',data_mnt[[f'BUCKET_SCORE{item}mnt','Loan No']])
    return data_mnt[['Loan No',f'BUCKET_SCORE{item}mnt']]







def read_all_sheets(file_path):
    xls = pd.ExcelFile(file_path, engine="openpyxl")  # Load the Excel file
    all_sheets = []  # List to store individual DataFrames

    for sheet_name in xls.sheet_names:  # Iterate over all sheets
        print(f"Reading sheet: {sheet_name}")  # Debugging statement
        df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)  # Read each sheet as string
        all_sheets.append(df)

    # Combine all DataFrames into one
    if all_sheets:
        final_df = pd.concat(all_sheets, ignore_index=True)
    else:
        final_df = pd.DataFrame()  # Empty DataFrame if no sheets are found
    
    return final_df

def auto_split_payment_data(payment_final, range_size=5):
    # Convert the 'date' column to datetime if it's not already in that format
    payment_final['datechunk'] = pd.to_datetime(payment_final['Receipt date'])
    
    # Get the day of the month from the 'date' column
    payment_final['datechunk'] = payment_final['datechunk'].dt.day
    
    # Get the maximum day value in the data to determine the number of ranges
    max_day = payment_final['datechunk'].max()

    # Create a dictionary to store the splits
    payment_splits = {}

    # Loop through the days in the specified range and create splits
    for start_day in range(1, max_day + 1, range_size):
        end_day = min(start_day + range_size - 1, max_day)
        pay_key = f'pay{(start_day - 1) // range_size + 1}'
        
        # Filter payment data based on the current day range
        payment_splits[pay_key] = payment_final[(payment_final['datechunk'] >= start_day) & 
                                                (payment_final['datechunk'] <= end_day)]

    return payment_splits

def save_payment_splits_to_excel(payment_final, file_name, range_size=5):
    # Split the data dynamically
    payment_splits = auto_split_payment_data(payment_final, range_size)
    # output_dir='./output/'
    # os.makedirs(output_dir, exist_ok=True)
    
    # Save the splits to an Excel file
    with pd.ExcelWriter(f'./output/{file_name}', engine='xlsxwriter') as writer:
        # Loop through the payment splits and save each as a sheet
        for pay_key, pay_data in payment_splits.items():
            print('pay_data',len(pay_data))
            # Save the split data to an Excel sheet with the sheet name based on the pay_key
            pay_data.to_excel(writer, index=False, sheet_name=pay_key, engine='xlsxwriter')
            


def split_dataframe_by_group(df, group_column, prefix):
    # Get unique values in the specified group column
    unique_values = df[group_column].unique()
    
    # Create a list to store the names of the created DataFrames
    dataframe_names = []
    
    # Create separate dataframes for each unique value in the group column
    for value in unique_values:
        df_name = f"{prefix}_{value}"
        globals()[df_name] = df[df[group_column] == value]
        dataframe_names.append(df_name)
    
    # Print the name of each created dataframe
    for df_name in dataframe_names:
        print(f"Dataframe name: {df_name}")
        # Uncomment the next line to print the dataframe contents
        # print(globals()[df_name], "\n")
    
    # Return the list of DataFrame names
    return dataframe_names



def assign_to_oa(df_toassign,oa_proportion) : 
    # print('df_toassign',len(df_toassign))
    # List to store the concatenated dataframes
    oa_list = split_dataframe_by_group(oa_proportion, 'group', 'oa')
    ar_list = split_dataframe_by_group(df_toassign, 'group', 'ar')
    # print(ar_list)
    dataframes_oa = {name: globals()[name] for name in oa_list}
    dataframes_ar = {name: globals()[name] for name in ar_list}
    combined_dfs = []

    # Iterate through each ar dataframe in dataframes_ar
    for i in dataframes_ar:
        ar_df = dataframes_ar[i]
        # print(i)
        # print(ar_df)

        order = i[-1]  # Extract the last character of the first element for 'order'
        # print('order', order)
        
        df_y = ar_df.loc[ar_df['ever'] == 'Y']  # Filter rows where 'ever' == 'Y'
        df_n = ar_df.loc[ar_df['ever'] == 'N']  # Filter rows where 'ever' == 'N'
        
        size_y = df_y['contract_no'].count()  # Count of 'Y' contracts
        size_n = df_n['contract_no'].count()  # Count of 'N' contracts
        
        # Get the corresponding OA dataframe based on order
        oa = dataframes_oa[f'oa_{order}']
        
        # Assign values randomly based on the OA assignment probabilities
        df_y['assigned'] = np.random.choice(oa['oa'], size=size_y, p=oa['%assign'])
        df_n['assigned'] = np.random.choice(oa['oa'], size=size_n, p=oa['%assign'])
        
        # Combine the 'Y' and 'N' dataframes
        assigned_df = pd.concat([df_y, df_n], ignore_index=True)
        
        # Store the concatenated dataframe in the list
        combined_dfs.append(assigned_df)

    # Concatenate all the combined dataframes into one final dataframe
    final_df = pd.concat(combined_dfs, ignore_index=True)

    # Optionally, assign the final concatenated dataframe to a dynamic variable
    globals()['df_assign_all'] = final_df

    # Print the final dataframe
    # print(final_df)
    return final_df
    