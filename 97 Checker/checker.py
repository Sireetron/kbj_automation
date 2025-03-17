import pandas as pd
# from utils import all_history, transform_files
import glob
import numpy as np
import pandas as pd
import glob
# import win32com.client as win32
import jaydebeapi
# from const import QUERY, CONNECT
import re

assign = pd.read_excel(f"./input/3.Total assign Mar'25 (1).xlsx", dtype={'Mobile No.': str, 
                                                        })
assign_delay = assign.loc[
    (assign['New OA'] == 'Delay calling')
][['Base date','Customer ID No','Principal balance','Customer Name', 'Sales product code','Mobile No.'
        ,'Overdue Months Division Code','Loan No.','Overdue days(Morning)','Status LM','New OA' ]]

assign_delay['Customer Name'] = assign_delay['Customer Name'].str.strip()
assign_delay[['NAME', 'SURNAME']] = assign_delay['Customer Name'].str.split(n=1, expand=True)


customer = pd.read_csv('./input/1stday/customerdata.csv', dtype={'MOBILE_PHONE_NO_VAL': str, 
                                                           'NATIONAL_ID_VAL': str, 
                                                           'CONTRACT_NO_VAL': str})

assign_delay['Customer ID No'] = assign_delay['Customer ID No'].astype(str)
assign_delay['Loan No.'] = assign_delay['Loan No.'].astype(str)
customer['CONTRACT_NO_VAL'] = customer['CONTRACT_NO_VAL'].astype(str)
customer['NATIONAL_ID'] = customer['NATIONAL_ID'].astype(str) 

assign_delay_merge = assign_delay.merge(customer, left_on=['Customer ID No', 'Loan No.'], right_on=['NATIONAL_ID' ,'CONTRACT_NO_VAL'], how='left')
assign_delay_merge['NAME_CHECK'] = assign_delay_merge.apply(
    lambda row: True if row['NAME'] == row['NAME_VAL'] else row['NAME_VAL'],
    axis=1
)
assign_delay_merge['SURNAME_CHECK'] = assign_delay_merge.apply(
    lambda row: True if row['SURNAME'] == row['SURNAME_VAL'] else row['SURNAME_VAL'],
    axis=1
)

assign_delay_merge['MOBILE_CHECK'] = assign_delay_merge.apply(
    lambda row: True if row['Mobile No.'] == row['MOBILE_PHONE_NO_VAL'] else row['MOBILE_PHONE_NO_VAL'],
    axis=1
)

assign_delay_merge['LAST4DIGIT'] = assign_delay_merge['Loan No.'].str[-4:]
assign_delay_merge = assign_delay_merge[['Base date', 'Customer ID No', 'Principal balance', 'Customer Name',
       'Sales product code', 'Mobile No.', 'Overdue Months Division Code',
       'Loan No.', 'Overdue days(Morning)', 'Status LM', 'New OA', 'NAME',
       'SURNAME', 'AS_OF_DATE', 'CHANNEL',
       'MONTHLY_INST_AMT', 'FIRST_DUE_DATE','RESIDENT_ADDRESS', 'NAME_CHECK',
       'SURNAME_CHECK', 'MOBILE_CHECK','LAST4DIGIT']]
path_file = glob.glob("./input/1stday/*assign*.xlsx")[0].split('\\')[1]
path_file = re.sub(r'\.xlsx$', '', path_file)
assign_delay_merge.to_csv(f'./output/1stday/check{path_file}')

