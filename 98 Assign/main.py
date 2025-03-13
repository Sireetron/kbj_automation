import pandas as pd
import glob
import numpy as np

pd.set_option('display.float_format', '{:.0f}'.format)


for i in glob.glob("./input/assigned/*.csv")  :
    assigned_path  = i.split('\\')[-1] 
    oa_proportion = pd.read_csv(f'./input/assigned/{assigned_path}')
    ar_path = glob.glob("./input/AR/*.csv")[0].split('\\')[-1] 
     
    ar = pd.read_csv(f'./input/AR/{ar_path}')

    loan_count = ar['Loan No'].nunique()
    loan_balance_sum = ar['Loan Balance'].sum()
    print(f'loan_count : {loan_count}  , loan_balance_sum : {loan_balance_sum}')


    oa_proportion['portion_loancount'] =  ((oa_proportion['proportion'] / 100) * loan_count).apply(np.ceil)
    oa_proportion['portion_loanbalance'] =  ((oa_proportion['proportion'] / 100) * loan_balance_sum).apply(np.ceil)
    print('oa_proportion',oa_proportion)