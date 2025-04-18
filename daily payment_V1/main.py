import pandas as pd
import glob
import re
from const import COlS
from datetime import date, datetime
import logging
from utils import read_all_sheets,save_payment_splits_to_excel

# Configure the logging module
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# Create a logger
logger = logging.getLogger(__name__)

logger.info('Importing file Map Owner...')
Rep_files = glob.glob("./input/*.csv")
Map_path = glob.glob("./input/Map*.xlsx")
Map_owner = pd.read_excel(Map_path[0], engine='openpyxl').astype(str)
Map_owner = Map_owner.drop(columns={'Assign Date'})
Map_owner = Map_owner.rename(columns={'Loan No.': 'Loan No', 'Owner': 'OA', 'Due': 'DUE'})
logger.info('Map Owner impoerted done!!')
file_date = re.findall(r'\d+', Rep_files[0])[0]
file_time = re.findall(r'\d+', Rep_files[0])[1]
logger.info('Importing Rep file...')
Rep = pd.read_csv(Rep_files[0], usecols=COlS.use_cols, encoding='cp874').astype(str)
Rep = Rep.merge(Map_owner, on='Loan No', how='left')
logger.info('Rep file impoerted done!!')
logger.info('Start process cleanning and formatting files...')
print("filetime",file_time)
if file_time != '0830':
    Rep['Payment Amt(Total payment Amt)'] = Rep['Payment Amt(Total payment Amt)'].astype('float64')
    today = datetime.now().date()
    today_str = today.strftime('%Y%m%d')
    file_name = today.strftime('%d%m%Y')
    Rep = Rep[Rep['Receipt date'] == today_str]
    payment_unique = Rep[Rep.duplicated('Receipt Number', keep=False) == False]
    payment_res = payment_unique[payment_unique['Payment Amt(Total payment Amt)'] > 0]
    payment_final = payment_res[~payment_res['Receipt channel'].str.contains('CIMB')]
    payment_final = payment_final.replace('nan', None)
    print("filetime",file_time)
    print("path",f'./output/output_16_30/Payment {file_name} {file_time}.xlsx')
    payment_final.to_excel(f'./output/output_16_30/Payment {file_name} {file_time}.xlsx', engine='xlsxwriter', index=False)
elif file_date[-2:] == '02' and file_time == '0830':
    today = datetime.now().date()
    today_str = today.strftime('%Y%m%d')
    today_month = today.strftime('%Y%b%d')
    month = today_str[4:6]
    full_month = today_month[4:7]
    year = today_str[:4]
    Rep['Payment Amt(Total payment Amt)'] = Rep['Payment Amt(Total payment Amt)'].astype('float64')
    payment_unique = Rep[Rep.duplicated('Receipt Number', keep=False) == False]
    payment_res = payment_unique[payment_unique['Payment Amt(Total payment Amt)'] > 0]
    payment_final = payment_res[~payment_res['Receipt channel'].str.contains('CIMB')]
    payment_final = payment_final.replace('nan', None)
    payment_final.to_excel(f'./output/{month}.All Payment {full_month} {year}.xlsx', engine='xlsxwriter', index=False)
else:
    print("file_date!=02")
    payment_path = glob.glob("./output/*.xlsx")[0]
    print(payment_path)
    #==== ex-record===========#
    # payment = pd.read_excel(payment_path, engine="openpyxl").astype(str)    
    payment = read_all_sheets(payment_path)
    #==== ex-record===========#
    
    
    #==== combine-record===========#
    payment_combine = pd.concat([payment, Rep]).sort_values(by='Receipt date')
    print('quick sum', payment_combine.groupby('Receipt date').size())
    # payment = pd.concat([payment, Rep])
    #==== combine-record===========#
    
    #checkdup======================#
    # print(payment,Rep)
    common_duplicate = Rep[Rep['Receipt Number'].isin(payment['Receipt Number'])]
    print('checkcountduplicate',common_duplicate.groupby('Receipt date').size())
    common_unique =  Rep[~Rep['Receipt Number'].isin(payment['Receipt Number'])]
    print('checkcountunique',common_unique.groupby('Receipt date').size())
    #checkdup======================#


    #==== processing===========#
    # payment_combine['Payment Amt(Total payment Amt)'] = payment_combine['Payment Amt(Total payment Amt)'].astype('float64')
    payment_unique = payment_combine[payment_combine.duplicated('Receipt Number', keep=False) == False]
    payment_res = payment_unique[payment_unique['Payment Amt(Total payment Amt)'].astype('float64') > 0]
    payment_final = payment_res[~payment_res['Receipt channel'].str.contains('CIMB')].replace('nan', None).sort_values(by='Receipt date')
    #==== processing===========#
    
    #==== export===========#
    file_name = payment_path.split('\\')[1]
    save_payment_splits_to_excel(payment_final, file_name,5)
    #==== export===========#
 
 
    # file_name = payment_path.split('\\')[1]
    # if payment_final.shape[0] >1040000:
    #     print("split")
    #     pay1 = payment_final[:1000001]
    #     pay2 = payment_final[1000001:]
    #     logger.info('Exportting payment..')
    #     with pd.ExcelWriter(f'./output/{file_name}', engine='xlsxwriter') as writer:
    #         pay1.to_excel(writer, index=False, sheet_name='payment1', engine='xlsxwriter')
    #         pay2.to_excel(writer, index=False, sheet_name='payment2', engine='xlsxwriter')
    # else:
    #     print("nosplit")
    #     logger.info('Exportting payment..')
    #     payment_final.to_excel(f'./output/{file_name}', engine='xlsxwriter', index=False)
logger.info('Process done, Please check output folder!!!')