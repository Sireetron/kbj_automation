
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
import re

def all_history(query,date,item) :
    data_mnt = pd.read_csv(f'./input/acc_history_monthly/{date}')
    # print(f'./input/history/{date}')
    data_mnt['Loan No'] = data_mnt['Loan No'].astype(str)
    data_mnt = data_mnt[['Loan No','OverdueCnt_Morning']].merge(query, left_on='OverdueCnt_Morning', right_on='BUCKET', how='left')
    data_mnt = data_mnt.rename(columns={'BUCKET_SCORE': f'BUCKET_SCORE{item}mnt'})
    return data_mnt[['Loan No',f'BUCKET_SCORE{item}mnt']]

def transform_files(files):
    files.sort(reverse=True)
    latest_files = files
    return [[file,  re.sub(r'\.csv$', '', file)] for file in latest_files]
