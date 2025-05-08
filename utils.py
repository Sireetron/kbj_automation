import pandas as pd
import glob
import logging
import win32com.client as win32
import os
import jaydebeapi
from datetime import datetime
import re
import numpy as np






def save_to_split_excel(df,pathsave):
    max_rows_per_sheet = 500000
    total_rows = len(df)
    with pd.ExcelWriter(pathsave, engine='xlsxwriter') as writer:
        for i in range(0, total_rows, max_rows_per_sheet):
            end = min(i + max_rows_per_sheet, total_rows)
            print('end',end)
            sheet_name = f'Sheet_{i // max_rows_per_sheet + 1}'
            df.iloc[i:end].to_excel(writer, sheet_name=sheet_name, index=False)





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

# def flatten_distribution_by_principal(df):
#     principal_sum_per_collector = df.groupby('distribute')['principal_balance'].sum().to_dict()
#     median_principal = np.median(list(principal_sum_per_collector.values()))
    
#     over_collectors = {k: v for k, v in principal_sum_per_collector.items() if v > median_principal}
#     under_collectors = {k: v for k, v in principal_sum_per_collector.items() if v < median_principal}
    
#     if not under_collectors:
#         return df  # Nothing to rebalance
    
#     min_underload = min(under_collectors.values())

#     for over_collector in list(over_collectors.keys()):
#         target = median_principal + min_underload
#         over_accounts = df[df['distribute'] == over_collector].sort_values('principal_balance')

#         for under_collector in list(under_collectors.keys()):
#             under_accounts = df[df['distribute'] == under_collector].sort_values('principal_balance', ascending=False)

#             for over_idx, over_row in over_accounts.iterrows():
#                 for under_idx, under_row in under_accounts.iterrows():
#                     # Simulate swap
#                     over_new = principal_sum_per_collector[over_collector] - over_row['principal_balance'] + under_row['principal_balance']
#                     under_new = principal_sum_per_collector[under_collector] - under_row['principal_balance'] + over_row['principal_balance']

#                     # Check if this brings over_collector closer to target
#                     if abs(over_new - target) < abs(principal_sum_per_collector[over_collector] - target) and \
#                        abs(under_new - median_principal) < abs(principal_sum_per_collector[under_collector] - median_principal):

#                         # Perform swap
#                         df.at[over_idx, 'distribute'] = under_collector
#                         df.at[under_idx, 'distribute'] = over_collector

#                         # Update totals
#                         principal_sum_per_collector[over_collector] = over_new
#                         principal_sum_per_collector[under_collector] = under_new
#                         break  # Swap done
#                 else:
#                     continue
#                 break  # Move to next over_collector

#     return df
def flatten_distribution_by_principal(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Track swapped pairs (pair is sorted lexicographically to handle both directions)
    swapped_pairs = set()

    while True:
        # Step 1: Total principal per team
        principal_sum = df.groupby('distribute')['principal_balance'].sum().to_dict()

        # Step 2: Calculate median
        median_principal = np.average(list(principal_sum.values()))

        # Step 3: Identify overload and underload
        diff_from_median = {team: total - median_principal for team, total in principal_sum.items()}
        overload_teams = {team: diff for team, diff in diff_from_median.items() if diff > 0}
        underload_teams = {team: -diff for team, diff in diff_from_median.items() if diff < 0}

        # Step 4: Check if no more imbalance exists (exit condition)
        if not overload_teams or not underload_teams:
            print("All teams are balanced.")
            break

        # Sort overloaded and underloaded teams
        overload_list = sorted(overload_teams.items(), key=lambda x: -x[1])
        underload_list = sorted(underload_teams.items(), key=lambda x: -x[1])

        swapped = False

        # Step 5: Start pairing overloaded teams with underloaded teams
        for (over_team, over_diff), (under_team, under_diff) in zip(overload_list, underload_list):
            # Check if this pair has been swapped more than twice
            pair_key = tuple(sorted([over_team, under_team]))
            if pair_key in swapped_pairs:
                continue

            over_accounts = df[df['distribute'] == over_team].copy()
            under_accounts = df[df['distribute'] == under_team].copy()

            if under_accounts.empty or over_accounts.empty:
                continue

            # Minimum principal from the underloaded team
            min_under_val = under_accounts['principal_balance'].min()

            # Target for the overloaded account: overloaded difference + minimum underloaded account
            target_val = over_diff + min_under_val

            # Find the account from the overloaded team closest to the target
            over_candidate = over_accounts.iloc[
                (over_accounts['principal_balance'] - target_val).abs().argsort()
            ].head(1)

            # Find the smallest account from the underloaded team
            under_candidate = under_accounts.nsmallest(1, 'principal_balance')

            if not over_candidate.empty and not under_candidate.empty:
                over_idx = over_candidate.index[0]
                under_idx = under_candidate.index[0]

                over_val = df.loc[over_idx, 'principal_balance']
                under_val = df.loc[under_idx, 'principal_balance']

                # Perform the swap: update only the distribute column
                df.at[over_idx, 'distribute'] = under_team
                df.at[under_idx, 'distribute'] = over_team

                # Print the swap details
                # print(f"Swapping accounts:")
                # print(f"  - From {over_team}: {df.loc[over_idx, 'contract_no']} (Principal: {over_val})")
                # print(f"  - To   {under_team}: {df.loc[under_idx, 'contract_no']} (Principal: {under_val})\n")

                swapped = True
                swapped_pairs.add(pair_key)  # Mark this pair as swapped
                break  # After a successful swap, break and recheck

        # If no swap occurred, exit the loop (all teams are now balanced)
        if not swapped:
            print("No more possible swaps. All teams are now balanced.")
            break

    return df

def process_distribution_by_groups_inhouse(df, group_fields, oa_proportion_collector):
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

def count_portion(field_collector, df):
    count_ar = len(df)

    # Step 1: calculate initial (floored) number of collections
    oa_proportion = field_collector.copy()
    raw_counts = oa_proportion['%assign'] * count_ar
    oa_proportion['num_collection'] = np.floor(raw_counts).astype(int)

    # Step 2: calculate remainder
    total_assigned = oa_proportion['num_collection'].sum()
    remainder = count_ar - total_assigned

    # Step 3: add remainder to the row with maximum %assign
    if remainder > 0:
        max_idx = oa_proportion['%assign'].idxmax()
        oa_proportion.loc[max_idx, 'num_collection'] += remainder

    return oa_proportion


def process_distribution_by_groups_oa(df, group_fields, oa_proportion_collector):
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
        count_num_oa = count_portion(oa_proportion_collector, df_group)
        distributed_df = distribute(df_group, count_num_oa)
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
    