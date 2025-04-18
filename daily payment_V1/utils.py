
import pandas as pd
import glob
import re
from const import COlS
from datetime import date, datetime
import logging


def read_all_sheets(file_path):
    xls = pd.ExcelFile(file_path, engine="openpyxl")  # Load the Excel file
    all_sheets = []  # List to store individual DataFrames

    for sheet_name in xls.sheet_names:  # Iterate over all sheets
        print(f"Reading sheet: {sheet_name}")  # Debugging statement
        df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)  # Read each sheet as string
        all_sheets.append(df)

    # Combine all DataFrames into one
    if all_sheets:
        final_df = pd.concat(all_sheets, ignore_index=True)
    else:
        final_df = pd.DataFrame()  # Empty DataFrame if no sheets are found
    
    return final_df

def auto_split_payment_data(payment_final, range_size=5):
    # Convert the 'date' column to datetime if it's not already in that format
    payment_final['datechunk'] = pd.to_datetime(payment_final['Receipt date'])
    
    # Get the day of the month from the 'date' column
    payment_final['datechunk'] = payment_final['datechunk'].dt.day
    
    # Get the maximum day value in the data to determine the number of ranges
    max_day = payment_final['datechunk'].max()

    # Create a dictionary to store the splits
    payment_splits = {}

    # Loop through the days in the specified range and create splits
    for start_day in range(1, max_day + 1, range_size):
        end_day = min(start_day + range_size - 1, max_day)
        pay_key = f'pay{(start_day - 1) // range_size + 1}'
        
        # Filter payment data based on the current day range
        payment_splits[pay_key] = payment_final[(payment_final['datechunk'] >= start_day) & 
                                                (payment_final['datechunk'] <= end_day)]

    return payment_splits

def save_payment_splits_to_excel(payment_final, file_name, range_size=5):
    # Split the data dynamically
    payment_splits = auto_split_payment_data(payment_final, range_size)
    # output_dir='./output/'
    # os.makedirs(output_dir, exist_ok=True)
    
    # Save the splits to an Excel file
    with pd.ExcelWriter(f'./output/{file_name}', engine='xlsxwriter') as writer:
        # Loop through the payment splits and save each as a sheet
        for pay_key, pay_data in payment_splits.items():
            print('pay_data',len(pay_data))
            # Save the split data to an Excel sheet with the sheet name based on the pay_key
            pay_data.to_excel(writer, index=False, sheet_name=pay_key, engine='xlsxwriter')