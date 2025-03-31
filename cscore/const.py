class QUERY:
    # query min pay data
    MIN_PAY = f'''
     WITH lastdate AS (
SELECT LOAN_NO, MAX(SETL_DT) AS CURRENT_DUE FROM INSTC.CFNC_INDM_L GROUP BY LOAN_NO
)
SELECT 
        a.LOAN_NO, 
        b.CURRENT_DUE,
        NVL(a.INS_THMM_DMND_PCPL_AMT,0) 
        + NVL(a.INS_THMM_DMND_INT_AMT,0) 
        + NVL(a.INS_THMM_DMND_CRED_USAGE_AMT,0)
        + NVL(a.INS_THMM_CLCF_AMT,0)
        + NVL(a.INS_THMM_VAT_AMT,0)  AS LAST_DUE_AMT 
    FROM INSTC.CFNC_INDM_L  a
    INNER JOIN lastdate b 
        ON a.LOAN_NO = b.LOAN_NO 
        AND a.SETL_DT = b.CURRENT_DUE 
    '''
#connect database
class CONNECT:
    DB = "com.tmax.tibero.jdbc.TbDriver"
    PORT = "jdbc:tibero:thin:@192.169.10.51:18629:DSTFCC"
    # USER = ["natdilok","Kbjparn#3009"] #user p parn
    USER = ["supat", "coll_sp@2025"]
    CNN = "tibero6-jdbc.jar"

