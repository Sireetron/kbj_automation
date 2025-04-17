class QUERY_SMS:
    # query min pay data
    SMS_WORDING = f'''
     SELECT * FROM SIREETRON.REF_SMS_WORDING 
    '''
#connect database
class CONNECT_TIBERO:
    DB = "com.tmax.tibero.jdbc.TbDriver"
    PORT = "jdbc:tibero:thin:@192.169.10.51:18629:DSTFCC"
    # USER = ["natdilok","Kbjparn#3009"] #user p parn
    USER = ["supat", "coll_sp@2025"]
    CNN = "tibero6-jdbc.jar"


class QUERY_CUSTOMERINFO:
    query= f'''
    SELECT * FROM JFDWH.CUSTOMER c 
OFFSET 5 ROWS FETCH NEXT 10 ROWS ONLY; 
    '''


class CONNECT_ORACLE:
    jclassname = "oracle.jdbc.OracleDriver"
    url = "jdbc:oracle:thin:@10.1.41.100:1622/JFDWH"
    # driver_args = ["natdilok","Kbjparn#3009"] #user p parn
    jars = ["supat", "SU#pass005"]
    lib = "ojdbc17.jar"


