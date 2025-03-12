
import pandas as pd
# from utils import select_min_pay, read_input_file, export_file
# import glob
# import numpy as np
import pandas as pd
# import glob
# import logging
# import win32com.client as win32
# import os
# import jaydebeapi
# from const import QUERY, CONNECT
# import oracledb
# import getpass
# import json


def all_history(query,date,item) :
    data_mnt = pd.read_csv(f'./input/acc_history_monthly/Acc_{date}_0830.csv')
    print(f'./input/history/Acc_{date}_0830.csv')
    data_mnt['Loan No'] = data_mnt['Loan No'].astype(str)
    data_mnt = data_mnt[['Loan No','OverdueCnt_Morning']].merge(query, left_on='OverdueCnt_Morning', right_on='BUCKET', how='left')
    data_mnt = data_mnt.rename(columns={'SCORE_INDEX': f'SCORE_INDEX{item}mnt'})
    return data_mnt[['Loan No',f'SCORE_INDEX{item}mnt']]