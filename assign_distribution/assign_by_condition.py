import pandas as pd
import glob
import numpy as np
import re
from utils import read_file,clean_column_names,assign_to_oa,split_dataframe_by_group
pd.set_option('display.float_format', '{:.0f}'.format)




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

# def split_dataframe_by_group(df, group_column, prefix):
#     unique_values = df[group_column].unique()
#     dataframe_names = []
#     for value in unique_values:
#         df_name = f"{prefix}_{value}"
#         globals()[df_name] = df[df[group_column] == value]
#         dataframe_names.append(df_name)
#     return dataframe_names


# def assign_to_oa(df_toassign) : 
#     oa_list = split_dataframe_by_group(oa_proportion, 'group', 'oa')
#     ar_list = split_dataframe_by_group(df_toassign, 'group', 'ar')
#     dataframes_oa = {name: globals()[name] for name in oa_list}
#     dataframes_ar = {name: globals()[name] for name in ar_list}
#     combined_dfs = []
#     for i in dataframes_ar:
#         ar_df = dataframes_ar[i]
#         order = i[-1]  
#         size = ar_df['contract_no'].count() 
#         oa = dataframes_oa[f'oa_{order}']
#         ar_df['assigned'] = np.random.choice(oa['oa'], size=size, p=oa['%assign'])        
#         assigned_df = ar_df
#         combined_dfs.append(assigned_df)
#     final_df = pd.concat(combined_dfs, ignore_index=True)
#     return final_df


# def loopbyassign(dfassign):
#     unique_product = dfassign['product_abbr'].unique()
#     product_list = []

#     for product in unique_product:
#         product_subset = dfassign[dfassign['product_abbr'] == product]
#         assigned_list = []

#         for overdue in product_subset['overdue_months_division_code'].unique():
#             overdue_subset = product_subset[product_subset['overdue_months_division_code'] == overdue]
#             df_y = overdue_subset.query("ever == 'Y'").sort_values(by='principal_balance', ascending=False)
#             df_n = overdue_subset.query("ever == 'N'").sort_values(by='principal_balance', ascending=False)

#             df_assign_y = assign_to_oa(df_y) if not df_y.empty else pd.DataFrame()
#             df_assign_n = assign_to_oa(df_n) if not df_n.empty else pd.DataFrame()

#             assigned_list.append(pd.concat([df_assign_y, df_assign_n], ignore_index=True))

#         if assigned_list:
#             assign_subset = pd.concat(assigned_list, ignore_index=True)
#             product_list.append(assign_subset)

#     return pd.concat(product_list, ignore_index=True) if product_list else pd.DataFrame()





assigned_path  = glob.glob("./input/assigned/*")[0].split('\\')[-1]
oa_proportion = read_file('./input/assigned/',assigned_path)
oa_proportion = clean_column_names(oa_proportion)


ar_path = glob.glob("./input/AR/*")[0].split('\\')[-1] 
ar = read_file('./input/AR/',ar_path)
ar = clean_column_names(ar)


ar['product_val'] =  ar['sales_product_code'].str.extract(r':\s*(.*)').replace(r'\b(RL|ML|TL)\b', 'RL ML TL', regex=True)
map_criteria = oa_proportion[['product','bucket','group','assign_type']].drop_duplicates(subset=['product', 'bucket','group','assign_type'])
ar_merge = ar.merge(map_criteria,left_on='product_val',right_on = 'product', suffixes=('_df1', '_df2'))
ar_merge  = ar_merge[ar_merge.apply(lambda row: row['overdue_months_division_code'] in row['bucket'], axis=1)]




save_old_assign_new = ar_merge[ar_merge['assign_type'] == 'save_old_assign_new'].reset_index(drop=True)
save_old  = save_old_assign_new.loc[ (save_old_assign_new['status_lm'] == 'SAVE')]
save_old['assigned'] = save_old['old_oa']
assign_new =  save_old_assign_new.loc[ ~(save_old_assign_new['status_lm'] == 'SAVE')]
assign_new= assign_to_oa(assign_new,oa_proportion)
save_old_assign_new = pd.concat([save_old.reset_index(drop=True), 
           assign_new.reset_index(drop=True)],  ignore_index=True)


assign_all = ar_merge[ar_merge['assign_type'] == 'assign_all'].reset_index(drop=True)
assign_all= assign_to_oa(assign_all,oa_proportion)


assign_old_assign_new = ar_merge[ar_merge['assign_type'] == 'assign_old_assign_new'].reset_index(drop=True)
assign_old  = assign_old_assign_new.loc[ (assign_old_assign_new['status_lm'] == 'SAVE')]
assign_old= assign_to_oa(assign_old,oa_proportion)
assign_new =  assign_old_assign_new.loc[ ~(assign_old_assign_new['status_lm'] == 'SAVE')]
assign_new= assign_to_oa(assign_new,oa_proportion)
assign_old_assign_new = pd.concat([assign_old.reset_index(drop=True), 
           assign_new.reset_index(drop=True)],  ignore_index=True)


final = pd.concat([save_old_assign_new.reset_index(drop=True), 
           assign_all.reset_index(drop=True), 
           assign_old_assign_new.reset_index(drop=True)], ignore_index=True)


ar_path = glob.glob("./input/AR/*")[0].split('\\')[-1]  
ar = read_file('./input/AR/',ar_path)
ar_path_name = re.sub(r'\.(csv|xlsx)$', '', ar_path)


final.to_csv(f'./output/assign_by_condition_{ar_path_name}.csv')