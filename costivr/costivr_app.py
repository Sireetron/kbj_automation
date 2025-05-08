import pandas as pd
import glob
import re


def costivr_app():
    allfile = glob.glob("./costivr/input/*") 
    rate = pd.read_csv('./costivr/rate.csv')
    def summary(allfile) :
        
        allcall = pd.DataFrame() 
        for i in allfile :
            filename = i.split('\\')[-1]
            data = pd.read_csv(f'{i}')
            data_hangup = data.loc[data['Status'] == 'hangup'].copy()
            data_hangup['date'] = pd.to_datetime(data_hangup['Timestamp']).dt.date
            data_hangup['campaign'] = re.sub(r'\.csv$', '', filename)
            hangup_summary = data_hangup.groupby(['date', 'campaign']).agg(
                number_of_hangup_calls=('No.', 'count')
            ).reset_index()
            
            ptp_summary = data_hangup[data_hangup['01_result'] == 'ptp'].groupby(['date', 'campaign']).agg(
            ptp_count=('No.', 'count')).reset_index()
            

            # Process all call data
            data['date'] = pd.to_datetime(data['Timestamp']).dt.date
            data['campaign'] = re.sub(r'\.csv$', '', filename)
            total_summary = data.groupby(['date', 'campaign']).agg(
                total_calls=('No.', 'count')
            ).reset_index()

            # Merge both summaries
            merged = pd.merge(hangup_summary, total_summary, on=['date', 'campaign'], how='outer')
            merged['%_hangup_in_total (call)'] = ((merged['number_of_hangup_calls'] / merged['total_calls']) * 100).round(2).astype(str) + '%'
            merged = pd.merge(merged, ptp_summary, on=['date', 'campaign'], how='left')
           
            allcall = pd.concat([allcall, merged], ignore_index=True)
           
        return allcall

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
    log=log.rename(columns={'number_of_hangup_calls':'number_of_hangup_calls (call)',
                            'total_calls':'total_calls (call)','ptp_count':'number_of_ptp (call)'})
    
    log = log.sort_values('date').reset_index(drop=True)
    with pd.ExcelWriter('./costivr/output/costivr.xlsx', engine='openpyxl') as writer:
        monthly.to_excel(writer, sheet_name='monthly', index=False)
        log.to_excel(writer, sheet_name='log', index=False)