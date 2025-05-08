
from flask import Flask, render_template, request, send_from_directory,send_file, session
import os
# from flask_wtf import FlaskForm
# from wtforms import FileField, SubmitField
# from werkzeug.utils import secure_filename
from checker.checker_app import checker
from checker.checker_app import checker
from service.cscore_service import cscore_service
from service.smschecker_service import sms_checker_service
from service.overduestamp_service import overdue_stamp_service
from service.costivr_service import costivr_service
from service.assign_inhouse_distribution_service import assign_inhouse_distribution_service
import zipfile
import io
from cscore.cscore_app import cscore_app
from overdue_oa.overdue_date_app import overdue_date_app
from costivr.costivr_app import costivr_app
from assign_distribution.assign_inhouse_app import assign_inhouse_app
from assign_distribution.assign_oa_app import assign_oa_app
from service.assign_oa_distribution_service import assign_oa_distribution_service
from threading import Lock

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['DOWNLOAD_FOLDER_SMS'] = 'checker/output'  
app.config['DOWNLOAD_FOLDER_OVERDUESTAMP'] = 'overdue_oa/output'  
app.config['DOWNLOAD_FOLDER_COST_IVR'] = 'costivr/output'  
app.config['DOWNLOAD_FOLDER_ASSIGN_INHOUSE'] = 'assign_distribution/output'  
app.config['DOWNLOAD_FOLDER_ASSIGN_OA'] = 'assign_distribution/output'  



@app.route('/home', methods=['GET', 'POST'])
def home():
     return render_template('home.html')
 
 
@app.route('/sms-checker', methods=['GET', 'POST'])
def upload_smschecker():
     return sms_checker_service()
   

@app.route('/cscore', methods=['GET', 'POST'])
def upload_monthly_cscore():
    return cscore_service()

@app.route('/overdue-stamp', methods=['GET', 'POST'])
def upload_overdue_stamp():
    return overdue_stamp_service()

@app.route('/costivr', methods=['GET', 'POST'])
def upload_costivr():
    return costivr_service()

@app.route('/assign-inhouse', methods=['GET', 'POST'])
def upload_inhouse_assign_distribution():
    return assign_inhouse_distribution_service()

@app.route('/assign-oa', methods=['GET', 'POST'])
def upload_oa_assign_distribution():
    return assign_oa_distribution_service()



@app.route('/download/<folder>/<filename>')
# folder name is path ที่ตั้ง ไว้ใส่เงื่อไขเวลาเรียก api  filemname คือ outputnaame 
def download_file(folder,filename):
    if folder == 'sms-checker':
            checker() 
            download_path = os.path.abspath(app.config['DOWNLOAD_FOLDER_SMS']) 
    elif folder == 'overdue-stamp':
            overdue_date_app() 
            download_path = os.path.abspath(app.config['DOWNLOAD_FOLDER_OVERDUESTAMP']) 
    elif folder == 'costivr':
            costivr_app() 
            download_path = os.path.abspath(app.config['DOWNLOAD_FOLDER_COST_IVR']) 
    elif folder == 'assign-inhouse':
            assign_inhouse_app() 
            download_path = os.path.abspath(app.config['DOWNLOAD_FOLDER_ASSIGN_INHOUSE']) 
    elif folder == 'assign-oa':
            assign_oa_app() 
            download_path = os.path.abspath(app.config['DOWNLOAD_FOLDER_ASSIGN_OA']) 
    else:
        return "Folder not found", 404  
    
    return send_from_directory(download_path, filename, as_attachment=True)



# cscore_lock = Lock()
@app.route('/download/<folder_name>/<path:outputpath>')
def process_and_download_file_cscore(folder_name, outputpath):
    # acquired = cscore_lock.acquire(blocking=False)
    # if not acquired:
    #     return "Another request is processing. Please try again later.", 429

    # try:
    cscore_app()  # Only one thread can call this at a time

    folder_path = f'{outputpath}'
    if not os.path.exists(folder_path):
        return "Folder does not exist", 404

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name=f"{folder_name}.zip", mimetype='application/zip')

    # finally:
    #     cscore_lock.release()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)