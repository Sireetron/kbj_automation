import pandas as pd
import glob
import numpy as np
import re
import sys
import os
from utils import read_file,clean_column_names,clean_data,process_distribution_by_groups
sys.path.append(os.path.abspath(''))

def assign_inhouse_app() :
    print(glob.glob("./assign_distribution/input/portion/*")[0].split('\\')[-1] )
    oa_proportion_path = glob.glob("./assign_distribution/input/portion/*")[0].split('\\')[-1] 
    oa_proportion = read_file('./assign_distribution/input/portion/',oa_proportion_path)
    oa_proportion = clean_column_names(oa_proportion)

    assign_path = glob.glob("./assign_distribution/input/assign/*")[0].split('\\')[-1]  
    assign = read_file('./assign_distribution/input/assign/',assign_path)
    assign = clean_column_names(assign)

    parameter_path = glob.glob("./assign_distribution/input/parameter/*")[0].split('\\')[-1]  
    param = read_file('./assign_distribution/input/parameter/',parameter_path)
    param = clean_column_names(param)
    param = clean_data(param)

    assign = assign.sort_values(by='principal_balance', ascending=False)

    group_fields = list(param['parameter'])
    final_df = process_distribution_by_groups(assign, group_fields, oa_proportion)
    final_df.to_excel('./assign_distribution/output/assign-inhouse-output.xlsx')
    print('final_df',final_df)
