from flask import Flask, render_template, request, send_from_directory,send_file, session
import os
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from checker.checker_app import checker
from checker.checker_app import checker
from service.cscore_service import cscore_service
from service.smschecker_service import sms_checker_service
from service.overduestamp_service import overdue_stamp_service
import zipfile
import io
from cscore.cscore_app import cscore_app
from overdue_oa.overdue_date_app import overdue_date_app


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['DOWNLOAD_FOLDER_SMS'] = 'checker/output'  
app.config['DOWNLOAD_FOLDER_OVERDUESTAMP'] = 'overdue_oa/output'  


@app.route('/sms-checker', methods=['GET', 'POST'])
def smschecker():
     return sms_checker_service()
   

@app.route('/cscore', methods=['GET', 'POST'])
def monthly_cscore():
    return cscore_service()

@app.route('/overdue-stamp', methods=['GET', 'POST'])
def overdue_stamp():
    return overdue_stamp_service()





@app.route('/download/<folder>/<filename>')
def download_file(folder,filename):
    if folder == 'sms-checker':
            checker() 
            download_path = os.path.abspath(app.config['DOWNLOAD_FOLDER_SMS'])  # Default download folder
            # print('download_path',download_path)
    elif folder == 'overduestamp':
            overdue_date_app() 
            download_path = os.path.abspath(app.config['DOWNLOAD_FOLDER_OVERDUESTAMP'])  # Default download folder
            # print('download_path',download_path)
        
    else:
        return "Folder not found", 404  # Handle invalid folder name
    
    return send_from_directory(download_path, filename, as_attachment=True)




@app.route('/download/<folder_name>/<path:outputpath>')
def process_and_download_file_cscore(folder_name,outputpath):
    cscore_app()

    folder_path = f'{outputpath}'
    if not os.path.exists(folder_path):
        return "Folder does not exist", 404

    zip_buffer = io.BytesIO()  # Create an in-memory zip file
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

    zip_buffer.seek(0)  
    return send_file(zip_buffer, as_attachment=True, download_name=f"{folder_name}.zip", mimetype='application/zip')



if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)