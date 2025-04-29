import pandas as pd
import glob
import numpy as np
import re
from utils import read_file,clean_column_names,clean_data

oa_proportion_path = glob.glob("./input/assigned/*")[0].split('\\')[-1] 
oa_proportion = read_file('./input/assigned/',oa_proportion_path)

ar_path = glob.glob("./input/AR/*")[0].split('\\')[-1]  
ar = read_file('./input/AR/',ar_path)

assign_path