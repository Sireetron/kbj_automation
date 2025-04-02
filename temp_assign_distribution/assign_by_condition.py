import pandas as pd
import glob
import numpy as np
import re
from utils import read_file,clean_column_names,assign_to_oa
pd.set_option('display.float_format', '{:.0f}'.format)
 

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