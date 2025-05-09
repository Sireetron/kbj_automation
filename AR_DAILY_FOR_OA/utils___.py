import pandas as pd
import glob
import logging
import win32com.client as win32
import os
import jaydebeapi
from const import QUERY, CONNECT
from datetime import datetime


def select_min_pay():
    conn = jaydebeapi.connect(
        CONNECT.DB,
        CONNECT.PORT,
        CONNECT.USER,
        CONNECT.CNN,
        )
    cur = conn.cursor()  

    min_pay = pd.read_sql(QUERY.MIN_PAY, conn) 
    conn.close()
    return min_pay
# Configure the logging module
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# Create a logger
logger = logging.getLogger(__name__)

# today_date = datetime.now().date()
# AR_date = today_date - timedelta(1)
# AR_date = AR_date.strftime('%Y%m%d')
Acc = glob.glob("./input/Acc_*.csv")
Acc_date = Acc[0].split('_')[1]
 
def read_input_file():
    files = glob.glob("./Input/*.*")
    logger.info('Start Processing...')
    logger.info('Reading input files...')
    for file in files:
        if 'Acc' in file:
            logger.info('Reading AR file...')
            AR = pd.read_csv(file, encoding='cp874', low_memory=False)
            AR = AR.rename(columns={'Loan No': 'LOAN_NO'})
            AR['BaseDate'] = AR['BaseDate'].astype(str)
            AR['LOAN_NO'] = AR['LOAN_NO'].astype(str)
            file_ar = file.replace('.', '_')
            file_lst = file_ar.split('_')
            ar_time = file_lst[3]
        elif 'GPD' in file:
            logger.info('Reading GPD SPD file...')
            GPD_SPD = pd.read_excel(file, engine='openpyxl', dtype={'LOAN_NO': str})
            GPD_SPD = GPD_SPD.rename(columns={'STATUS': 'GPD/SPD'})
        elif 'Map' in file:
            logger.info('Reading Map Owner file...')
            Owner = pd.read_excel(file, engine='openpyxl', dtype={'Loan No.': str})
            Owner = Owner.rename(columns={'Loan No.': 'LOAN_NO', 'Owner': 'OA'})
            Owner = Owner[['LOAN_NO', 'OA', 'Due']]
        else:
            pass
    print("finish inputfile")
    return AR, ar_time, GPD_SPD, Owner

def set_excel_file_password(excel_file_path, password):
    # Create an Excel application object
    excel_app = win32.Dispatch("Excel.Application")

    # Convert to absolute path
    excel_file_path = os.path.abspath(excel_file_path)

    # Open the Excel file
    wb = excel_app.Workbooks.Open(excel_file_path)

    # Set a password for the entire workbook
    wb.Password = password

    # Save and close the workbook
    wb.Save()
    wb.Close()
    
def export_file(AR, AR_TIME):
    print('==============start===================')
    AR_SF = AR[AR['Product Code'].str.contains('SF', na=False)].reset_index(drop=True)
    AR_ALL = AR[~AR['Product Code'].str.contains('SF', na=False)]
    # split_point = len(AR_SF) //2  # Splitting roughly in half
    # AR_SF1 = AR_SF.iloc[:split_point]
    # AR_SF2 = AR_SF.iloc[split_point:]
    # print('==============finishspritfile===================')
    # AR_SF_ASSIGN = AR_SF[~AR_SF['OA'].isna()]
    # logger.info('Exportting AR and AR_SF..')
    # with pd.ExcelWriter(f'./Output/AR_TOTAL/AR {Acc_date} Time {AR_TIME}.xlsx', engine='xlsxwriter') as writer:
    #     AR_ALL.to_excel(writer, index=False, sheet_name='AR_ALL', engine='xlsxwriter')
    #     AR_SF1.to_excel(writer, index=False, sheet_name='AR_SF1', engine='xlsxwriter') 
    #     AR_SF2.to_excel(writer, index=False, sheet_name='AR_SF2', engine='xlsxwriter')
    #     AR_SF_ASSIGN.to_excel(writer, index=False, sheet_name='AR_SF_ASSIGN', engine='xlsxwriter')
    
    # Split AR_SF into chunks of 100,000 rows per sheet
    max_rows = 100000
    num_sheets = (len(AR_SF) // max_rows) + (1 if len(AR_SF) % max_rows else 0)

    # Generate split dataframes dynamically
    split_AR_SF = [AR_SF.iloc[i * max_rows: (i + 1) * max_rows] for i in range(num_sheets)]
    print('============== Finish Split File ===================')

    # Filter AR_SF_ASSIGN
    AR_SF_ASSIGN = AR_SF[~AR_SF['OA'].isna()]
    logger.info('Exporting AR and AR_SF..')
    # Ensure output directory exists
    output_dir = './Output/AR_TOTAL'
    os.makedirs(output_dir, exist_ok=True)
    # Create Excel file
    output_file = f'{output_dir}/AR {Acc_date} Time {AR_TIME}.xlsx'
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        AR_ALL.to_excel(writer, index=False, sheet_name='AR_ALL')
        # Write split AR_SF sheets dynamically
        for i, df_chunk in enumerate(split_AR_SF):
            sheet_name = f'AR_SF_{i+1}'
            df_chunk.to_excel(writer, index=False, sheet_name=sheet_name)
        # Write AR_SF_ASSIGN
        AR_SF_ASSIGN.to_excel(writer, index=False, sheet_name='AR_SF_ASSIGN')
    logger.info(f'Excel file saved: {output_file}')
    
    
    
    
    print('==============saveallfile===================')
    AR_OA = AR[~AR['OA'].isna()]
    OA = AR_OA['OA'].unique()
    today = datetime.today()
    month = today.strftime('%b')
    year = today.strftime('%y')
    password = 'Col'+month+year
    # password = input('กรุณาระบุ password: ')
    for owner in OA:
        print('==============startloopfindingowner===================')
        OA_data = AR_OA[AR_OA['OA'] == owner]
        OA_SF = OA_data[OA_data['Product Code'].str.contains('SF', na=False)]
        OA_data = OA_data[~OA_data['Product Code'].str.contains('SF', na=False)]
       
        if OA_SF.shape[0] == 0:
            with pd.ExcelWriter(f'./Output/AR_OA/AR {Acc_date} Time {AR_TIME} {owner}.xlsx', engine='xlsxwriter') as writer:
                OA_data.to_excel(writer, index=False, sheet_name='AR_ALL', engine='xlsxwriter')
        else:
            with pd.ExcelWriter(f'./Output/AR_OA/AR {Acc_date} Time {AR_TIME} {owner}.xlsx', engine='xlsxwriter') as writer:
                OA_data.to_excel(writer, index=False, sheet_name='AR_ALL', engine='xlsxwriter')
                OA_SF.to_excel(writer, index=False, sheet_name='AR_SF', engine='xlsxwriter') 
        print('==============finishloop===================')
        path = f'./Output/AR_OA/AR {Acc_date} Time {AR_TIME} {owner}.xlsx'
        set_excel_file_password(path, password)
    logger.info('Exported AR and AR_SF done!!')