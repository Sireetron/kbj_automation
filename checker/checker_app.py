import os
import pandas as pd
import glob
import pandas as pd
import glob
import numpy as np
import pandas as pd
import glob
import jaydebeapi
import re
from const import QUERY, CONNECT
from datetime import datetime

def clean_column_names(df):
    df.columns = df.columns.str.lower()  
    df.columns = df.columns.str.replace(r'\.', '', regex=True)
    df.columns = df.columns.str.replace(r' ', '_', regex=True)  
    # df.columns = df.columns.str.replace('customer_id_no|customer_no|customer_id|national_id', 'customer_no', regex=True) 
    df.columns = df.columns.str.replace(r'loan_no', 'contract_no', regex=True)
    # df.columns = df.columns.str.replace(r'mobile.*', 'mobile_no', regex=True)
    # df.columns = df.columns.str.replace(r'customer_name/surname\(thai\)', 'customer_name', regex=True)  
    return df

def checker() :
    # Define the input folder
    input_folder = "./checker/input/assign_input/"



    # Get a list of files in the folder (xlsx or csv)
    files = glob.glob(os.path.join(input_folder, "*.xlsx")) + glob.glob(os.path.join(input_folder, "*.csv"))
    # Read only the first file found
    if files:
        file_path = files[0]
        if file_path.endswith(".xlsx"):
            assign = pd.read_excel(file_path,sheet_name='Data', dtype={'mobile_no': str})
            # print('assignassignassign',assign)
        elif file_path.endswith(".csv"):
            assign = pd.read_csv(file_path,sheet_name='Data', dtype={'mobile_no': str})   
    else:
        print("No file found in the folder.")


    # //////////////////*********************************************/////////////////////************************ #



    assign_delay = clean_column_names(assign)
    # print('assign_delay',assign_delay)
    customer = pd.read_csv('./checker/input/customer_input/customerdata.csv', dtype={'MOBILE_PHONE_NO_VAL': str, 
                                                            'CONTRACT_NO_VAL': str})
    customer.columns = customer.columns.str.lower()  
    # print('customer',customer)


    # //////////////////*********************************************/////////////////////************************ #

    # class CONNECT:
    #     DB = "com.tmax.tibero.jdbc.TbDriver"
    #     PORT = "jdbc:tibero:thin:@192.169.10.51:18629:DSTFCC"
    #     # USER = ["natdilok","Kbjparn#3009"]| #user p parn
    #     USER = ["supat", "coll_sp@2025"]
    #     CNN = "tibero6-jdbc.jar"
        
    conn = jaydebeapi.connect(
            CONNECT.DB,
            CONNECT.PORT,
            CONNECT.USER,
            CONNECT.CNN,
            )
    cur = conn.cursor()  

    sms_type = pd.read_sql(f'''
        SELECT * FROM SIREETRON.REF_SMS_WORDING 
        ''', conn) 
    conn.close()

    # //////////////////*********************************************/////////////////////************************ #

    # assign_delay = assign_delay.merge(sms_type,left_on='sms_type',right_on = 'sms_type', how='left')
    # assign_delay['customer_no'] = assign_delay['customer_no'].astype(str)
    assign_delay['contract_no'] = assign_delay['contract_no'].astype(str)
    customer['contract_no_val'] = customer['contract_no_val'].astype(str)
    # customer['national_id'] = customer['national_id'].astype(str) 

    # //////////////////*********************************************/////////////////////************************ #

    
    
    # assign_delay['customer_name'] = assign_delay['customer_name'].str.strip()
    # assign_delay[['name', 'surname']] = assign_delay['customer_name'].str.split(n=1, expand=True)

    # //////////////////*********************************************/////////////////////************************ #


    assign_delay_merge = assign_delay.merge(customer, left_on='contract_no', right_on='contract_no_val', how='left')
    # assign_delay_merge['name_check'] = assign_delay_merge.apply(
    #     lambda row: True if row['name'] == row['name_val'] else row['name_val'],
    #     axis=1
    # )

    # assign_delay_merge['surname_check'] = assign_delay_merge.apply(
    #     lambda row: True if row['surname'] == row['surname_val'] else row['surname_val'],
    #     axis=1
    # )

    assign_delay_merge['mobile_check'] = assign_delay_merge.apply(
        lambda row: True if row['mobile_no'] == row['mobile_phone_no_val'] else row['mobile_phone_no_val'],
        axis=1
    )

    # assign_delay_merge['fullname_check'] = assign_delay_merge.apply(
    #     lambda row: row['customer_name'] if row['name'] == row['name_val'] and row['surname'] == row['surname_val']  else row['name_val'] + ' ' +row['surname_val'] ,
    #     axis=1
    # )



    assign_delay_merge['last4digit_val'] = assign_delay_merge['contract_no'].str[-4:]
    # assign_delay_merge['sms_wording'] = assign_delay_merge.apply(lambda row: row['sms_wording'].replace("{4digit}", str(row['last4digit_val'])), axis=1)

    # //////////////////*********************************************/////////////////////************************ #



    path_file = re.sub(r'\.(csv|xlsx)$', '', glob.glob("./checker/input/assign_input/*")[0].split('\\')[1])
    # path_file = re.sub(r'\.xlsx$', '', path_file)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    output_dir = "./checker/output/"
    for file in glob.glob(os.path.join(output_dir, "*")):
        os.remove(file)
    assign_delay_merge.to_excel(f'./checker/output/check{path_file}.xlsx')
    assign_delay_merge.to_excel(f'./checker/output_backup/check{path_file}_{timestamp}.xlsx')


    # //////////////////*********************************************/////////////////////************************ #


