import pandas as pd
import glob
import re

allfile = glob.glob("./input/*") 
rate = pd.read_csv('./rate.csv')
def summary(allfile) :
    
    allcost = pd.DataFrame() 
    for i in allfile :
        filename = i.split('\\')[-1]
        data = pd.read_csv(f'{i}')
        data_hangup = data.loc[data['Status'] == 'hangup']
        data_hangup['date'] = pd.to_datetime(data_hangup['Timestamp']).dt.date
        data_hangup['campaign'] = re.sub(r'\.csv$', '', filename)  
        cost = data_hangup.groupby(['date','campaign']).agg(count=('No.', 'count')).reset_index()
        cost['key'] = 1
        rate['key'] = 1
        cross = pd.merge(cost, rate, on='key').drop('key', axis=1)
        filtered = cross[(cross['count'] > cross['minimum_rate']) & (cross['count'] < cross['maximum_rate'])]
        filtered['total_cost']=filtered['count']*filtered['ratepercall']
        allcost = pd.concat([allcost, filtered], ignore_index=True)
    return allcost

def summary_monthly(allfile):
    allcost = pd.DataFrame()

    for i in allfile:
        data = pd.read_csv(i)
        data_hangup = data[data['Status'] == 'hangup']
        data_hangup['date'] = pd.to_datetime(data_hangup['Timestamp']).dt.strftime('%Y-%m')
        allcost = pd.concat([allcost, data_hangup], ignore_index=True)
    cost = allcost.groupby('date').agg(count=('No.', 'count')).reset_index()
    cost['key'] = 1
    rate['key'] = 1  
    cross = pd.merge(cost, rate, on='key').drop('key', axis=1)
    filtered = cross[(cross['count'] > cross['minimum_rate']) & (cross['count'] < cross['maximum_rate'])]
    filtered['total_cost'] = filtered['count'] * filtered['ratepercall']

    return filtered

monthly = summary_monthly(allfile)
log = summary(allfile)
monthly['remain(call)'] = 40000-monthly['count']
monthly = monthly[['date','minimum_rate','maximum_rate','ratepercall','count','total_cost','remain(call)']]
monthly=monthly.rename(columns={'ratepercall':'rate_per_hangup_call (baht/call)',
                        'count':'number_of_hangup_call (call)','total_cost':'cost (baht)','remain(call)':'remain_call_in_month(call)'})

with pd.ExcelWriter('./output/costivr.xlsx', engine='openpyxl') as writer:
    monthly.to_excel(writer, sheet_name='monthly', index=False)
    log.to_excel(writer, sheet_name='log', index=False)