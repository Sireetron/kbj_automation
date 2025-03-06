Automate Program for Cleansing and formatting Daily Payment data transection


File zila ---> path BND

Rep_xxxxxx_xx.csv file (str all columns)

select columns just
[Loan No	Receipt date	Payment date	Receipt Seq No	Receipt channel	Payment type	 Payment Amt(Total payment Amt) 	Receipt Number	Sales product code	Last processed user No
]

map columns OA and due from assign p กรวด
(ปกติ ไฟล์สำหรับ map owner ก็ทำ manual และเนื่องจากข้อมูลเยอะ และมีการ adjust หรือ assign ใหม่หลายรอบต่อเดือน จึงทำให้เสียเวลา เลยให้โปรแกรมรับไฟล์ต้นฉบับที่จะเอามาใช้ map มาจัดการ โดยหากเป็นการทำฐานไฟล์ payment ในวันที่ 1 ของเดือน ต้องไปนำ ข้อมูลที่ assign เก่าของเดือนก่อนหน้ามารวมด้วย แต่ไฟล์ assign ของเดือนก่อนหน้าจะเป็น total มีทั้ง due 1 และ due 17 ต้องเอาเฉพาะ due ๅ7 ของเดือนเก่า เพราะอาจจะยังมีงานค้างของ due 17 (due 17  เดือนใหม่ยังไม่ถึง)
, original file assign have many cols (around 84 cols) so, read file select only used cols include loan no, OA, Due but when start date of month file payment total must be repaired to new one current month, then must be give data due 17 old month (last month to map too) เผื่อมีงานคงค้างของ OA due 17  

cut off rows of column Receipt Number where duplicate num (cut all if count > 1 keep=False)
# Drop rows where 'Receipt Number' is duplicated
df_unique = df[df.duplicated('number', keep=False) == False]

cut off rows where column Payment Amt(Total payment Amt) have amount <= 0

cut off rows where column Receipt channel have value CIMB

if file date = 1 must be create new file depend on same format cleaned but if date 1 but file time 08.30 it mean data still on MEC previous month concat data to old file last month 
if file date come on 16.00 do it follow same flow nut not concat just rep file only 
file date = 2 data insind = 1 of month so, start new file base of new month.
