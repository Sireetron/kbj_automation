import pandas as pd
import glob
import numpy as np
import re





def clean_column_names(df):
    df.columns = df.columns.str.lower()  # Convert to lowercase
    df.columns = df.columns.str.replace(r'\.', '', regex=True)
    df.columns = df.columns.str.replace(r' ', '_', regex=True)  # Replace non-alphanumeric characters with underscores
    df.columns = df.columns.str.replace('customer_id_no|customer_no|customer_id|national_id', 'customer_no', regex=True)  # Replace variations with 'customer_no'
    df.columns = df.columns.str.replace(r'loan_no', 'contract_no', regex=True)
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
    
