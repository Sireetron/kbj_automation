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


def clean_data(data):
    for col in data.columns:
        if data[col].dtype == object:  # Only apply to text columns
            data[col] = (
                data[col]
                .str.lower()
                .str.replace(r'\.', '', regex=True)
                .str.replace(r' ', '_', regex=True)
                .str.strip()
            )
    return data



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


def count_num(field_collector,df) :
    count_ar = len(df)
    total_rows = field_collector['collector'].count()
    base_value = count_ar // total_rows
    remainder = count_ar % total_rows
    field_collector['num_collection'] = base_value
    field_collector.loc[total_rows-remainder:, 'num_collection'] += 1
    return field_collector




def distribute(df,df_oa_proportion) : 
    num_col_list = dict(zip(df_oa_proportion['collector'], df_oa_proportion['num_collection']))

    distribution_limits = num_col_list
    distribution_counts = {key: 0 for key in distribution_limits}
    active_labels = list(distribution_limits.keys(
    ))


    distribut_column = []
    i = 0
    while len(distribut_column) < len(df):
        if not active_labels:
            break  # All quotas filled

        label = active_labels[i % len(active_labels)]

        if distribution_counts[label] < distribution_limits[label]:
            distribut_column.append(label)
            distribution_counts[label] += 1
        else:
            # Remove label from rotation if quota is met
            active_labels.remove(label)
            i -= 1  # stay at the same index next round to not skip a label

        i += 1

    # Fill the DataFrame
    df['distribute'] = distribut_column + [None] * (len(df) - len(distribut_column))
  
    return df

def flatten_distribution_by_principal(df):
    principal_sum_per_collector = df.groupby('distribute')['principal_balance'].sum().to_dict()
    median_principal = np.median(list(principal_sum_per_collector.values()))
    over_collectors = {k: v for k, v in principal_sum_per_collector.items() if v > median_principal}
    under_collectors = {k: v for k, v in principal_sum_per_collector.items() if v < median_principal}
    for over_collector in list(over_collectors.keys()):
        for under_collector in list(under_collectors.keys()):
            over_diff = principal_sum_per_collector[over_collector] - median_principal
            under_diff = median_principal - principal_sum_per_collector[under_collector]
            if over_diff <= 0 or under_diff <= 0:
                continue
            over_accounts = df[df['distribute'] == over_collector].sort_values('principal_balance', ascending=False)
            under_accounts = df[df['distribute'] == under_collector].sort_values('principal_balance')

            for over_idx, over_row in over_accounts.iterrows():
                for under_idx, under_row in under_accounts.iterrows():
                    over_new = (principal_sum_per_collector[over_collector]
                                - over_row['principal_balance']
                                + under_row['principal_balance'])
                    under_new = (principal_sum_per_collector[under_collector]
                                - under_row['principal_balance']
                                + over_row['principal_balance'])

                    if (abs(over_new - median_principal) < abs(principal_sum_per_collector[over_collector] - median_principal)) and \
                       (abs(under_new - median_principal) < abs(principal_sum_per_collector[under_collector] - median_principal)):

                        df.at[over_idx, 'distribute'] = under_collector
                        df.at[under_idx, 'distribute'] = over_collector

                        principal_sum_per_collector[over_collector] = over_new
                        principal_sum_per_collector[under_collector] = under_new
                        break  
                else:
                    continue
                break
    return df


def process_distribution_by_groups(df, group_fields, oa_proportion_collector):
    combined_dfs = []
    unique_combinations = df[group_fields].drop_duplicates()
    for _, combination in unique_combinations.iterrows():
        condition = True
        for field in group_fields:
            condition &= (df[field] == combination[field])
        df_group = df[condition]

        if df_group.empty:
            continue
        df_group = df_group.sort_values(by='principal_balance', ascending=False)
        count_num_oa = count_num(oa_proportion_collector, df_group)
        distributed_df = distribute(df_group, count_num_oa)
        distributed_df = flatten_distribution_by_principal(distributed_df)
        combined_dfs.append(distributed_df)

    if combined_dfs:
        final_df = pd.concat(combined_dfs, ignore_index=True)
    else:
        final_df = pd.DataFrame()  
    return final_df



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
    