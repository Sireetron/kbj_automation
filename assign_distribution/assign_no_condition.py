import pandas as pd
import glob
import numpy as np
import re
from utils import read_file,clean_column_names
pd.set_option('display.float_format', '{:.0f}'.format)


# for i in glob.glob("./input/assigned/*")  :
assigned_path  = glob.glob("./input/assigned/*")[0].split('\\')[-1] 
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
ar.to_csv(f'./output/assign_no_condition{ar_path_name}.csv')
# print('oa_proportion',oa_proportion)