class QUERY:
    # query min pay data
    SMS_WORDING = f'''
     SELECT * FROM SIREETRON.REF_SMS_WORDING 
    '''
#connect database
class CONNECT:
    DB = "com.tmax.tibero.jdbc.TbDriver"
    PORT = "jdbc:tibero:thin:@192.169.10.51:18629:DSTFCC"
    # USER = ["natdilok","Kbjparn#3009"] #user p parn
    USER = ["supat", "coll_sp@2025"]
    CNN = "tibero6-jdbc.jar"

