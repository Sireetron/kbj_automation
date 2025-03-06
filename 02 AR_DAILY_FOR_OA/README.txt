Extract AR to OA

1. import file Acc_xxxxxx_xx (AR data which xxxxxx = date, xx = time)
2. import other file which want to mapping data to Acc including
	- GPD_SPD file
	- Map Owner
3. Query Min pay data from SQL use code
	SELECT 
        a.LOAN_NO, 
        b.CURRENT_DUE,
        NVL(a.INS_THMM_DMND_PCPL_AMT,0) 
        + NVL(a.INS_THMM_DMND_INT_AMT,0) 
        + NVL(a.INS_THMM_DMND_CRED_USAGE_AMT,0)
        + NVL(a.INS_THMM_CLCF_AMT,0)
        + NVL(a.INS_THMM_VAT_AMT,0)  AS LAST_DUE_AMT 
    FROM INSTC.CFNC_INDM_L  a
    INNER JOIN (SELECT LOAN_NO, MAX(SETL_DT) AS CURRENT_DUE FROM INSTC.CFNC_INDM_L GROUP BY LOAN_NO) b 
        ON a.LOAN_NO = b.LOAN_NO 
        AND a.SETL_DT = b.CURRENT_DUE

 P.s. Can edit connection info in const.py class CONNECT --> USER Variable

4. Merge data GPD_SPD, Owner (for identify OA and extract file per OA to send to OA)
5.Min Pay Map min pay amount where Product not SF+ or overdue not normal xday wo
5.extract file for each OA for send to OA

(เดิมทีทำ manual ทั้งหมด input ทุกอย่างทำ manual เช่น Min pay ก็ต้องรันโค้ดแล้ว  Export file excel มาทำ manual ต่อ