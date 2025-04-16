class QUERY:
    # query min pay data
    query= f'''
    SELECT * FROM JFDWH.CUSTOMER c 
OFFSET 5 ROWS FETCH NEXT 10 ROWS ONLY; 
    '''
#connect database
class CONNECT:
    DB = "oracle.jdbc.OracleDriver"
    PORT = "jdbc:oracle:thin:@10.1.41.100:1622/JFDWH"
    # USER = ["natdilok","Kbjparn#3009"] #user p parn
    USER = ["supat", "SU#pass005"]
    CNN = "ojdbc11-23.2.0.0.jar"
