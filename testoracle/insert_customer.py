import pandas as pd
import jaydebeapi
import sys
import os
sys.path.append(os.path.abspath(''))
from const import  CONNECT_ORACLE

conn = jaydebeapi.connect(
        CONNECT_ORACLE.jclassname,
        CONNECT_ORACLE.url,
        CONNECT_ORACLE.jars,
        CONNECT_ORACLE.lib,
        )
cur = conn.cursor() 	

customer = pd.read_sql(f'''
    WITH data_contract AS (
SELECT cid.AS_OF_DATE , cid.CONTRACT_NO AS CONTRACT_NO_val
, cid.NATIONAL_ID AS NATIONAL_ID ,cid.CHANNEL ,cid.MONTHLY_INST_AMT ,cid.FIRST_DUE_DATE 
FROM jfdwh.CONTRACT_INFO_DAILY cid 
WHERE AS_OF_DATE =  (SELECT MAX(AS_OF_DATE) FROM JFDWH.CONTRACT_INFO_DAILY) -1
OFFSET 5 ROWS FETCH NEXT 100 ROWS ONLY 
)
SELECT dc.*,c.NAME AS NAME_val, c.SURNAME  AS SURNAME_val , 
c.MOBILE_PHONE_NO AS MOBILE_PHONE_NO_val ,c.RESIDENT_ADDRESS  FROM JFDWH.data_contract dc
LEFT JOIN JFDWH.CUSTOMER c ON dc.NATIONAL_ID  =c.NATIONAL_ID_NO ''', conn,dtype={'MOBILE_PHONE_NO_VAL': str, 
                                                            'NATIONAL_ID': str, 
                                                            'CONTRACT_NO_VAL': str}) 
print('customer',customer)


sms_type = pd.read_sql(f'''
   SELECT * FROM SUPAT.REF_SMS_WORDING ''', conn) 
print('sms_type',sms_type)

conn.close()

