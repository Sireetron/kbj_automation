class QUERY_SMS:
    # query min pay data
    SMS_WORDING = f'''
     SELECT * FROM SIREETRON.REF_SMS_WORDING 
    '''
#connect database

class QUERY_CUSTOMERINFO:
    query= f'''
     WITH data_contract AS (
        SELECT cid.AS_OF_DATE , cid.CONTRACT_NO AS CONTRACT_NO_val
        , cid.NATIONAL_ID AS NATIONAL_ID  ,cid.MONTHLY_INST_AMT ,cid.FIRST_DUE_DATE 
        FROM jfdwh.CONTRACT_INFO_DAILY cid 
        WHERE AS_OF_DATE =  (SELECT MAX(AS_OF_DATE) FROM JFDWH.CONTRACT_INFO_DAILY) -1
     
        )
        SELECT dc.*,
        c.MOBILE_PHONE_NO AS MOBILE_PHONE_NO_val   FROM JFDWH.data_contract dc
        LEFT JOIN JFDWH.CUSTOMER c ON dc.NATIONAL_ID  =c.NATIONAL_ID_NO
    '''

