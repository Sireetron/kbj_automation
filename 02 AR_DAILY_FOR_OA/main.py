import pandas as pd
from utils import select_min_pay, read_input_file, export_file
import glob
import numpy as np

Acc_check_count = glob.glob("./input/Acc_*.csv")
if len(Acc_check_count) > 1:
        print('File Acc AR have more 1 file please check!!!...')
else:
        MIN_PAY = select_min_pay()
        MIN_PAY = MIN_PAY.drop(columns={'CURRENT_DUE'})
        AR, AR_TIME, GPD_SPD, OWNER = read_input_file()
        AR = AR.merge(OWNER, on='LOAN_NO', how='left')
        AR = AR.merge(GPD_SPD, on='LOAN_NO', how='left')
        AR = AR.merge(MIN_PAY, on='LOAN_NO', how='left')
        not_map = ['NORMAL', 'Normal', 'normal', 'XD', 'Write-Off']
        pattern = '|'.join(not_map)
        AR['LAST_DUE_AMT'] = np.where(AR['Product Code'].str.contains('SF', na=False), None, AR['LAST_DUE_AMT'])
        AR['LAST_DUE_AMT'] = np.where(AR['OverdueCnt'].str.contains(pattern, na=False), None, AR['LAST_DUE_AMT'])
        export_file(AR, AR_TIME)
        print(AR)