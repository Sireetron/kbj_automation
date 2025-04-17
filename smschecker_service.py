from flask import Flask, render_template, request, send_from_directory
import os
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from checker.checker_app import checker
from flask import session
import glob

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER_SMS'] = 'checker/input/assign_input'
app.config['DOWNLOAD_FOLDER_SMS'] = 'checker/output' 
# app.config['DOWNLOAD_CSCORE'] = 'cscore/output/' 


class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")

table_checker = [
    { "contract_no": "3250800192489", "mobile_no": "0812345678","sms_type":"C4C"},
    { "contract_no": "1819900360011", "mobile_no": "0836654587","sms_type":"H4C"},
]


def sms_checker_service():
    folder_name = 'sms-checker'
    form = UploadFileForm()
    download_filename = []  
    message = f"--------------------------------------------------------------------------------------------"

    if form.validate_on_submit():
        file = form.file.data 
       
        if file:  
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER_SMS'], filename)
            print('filpath',filepath)
            os.remove(filepath)
            file.save(filepath)
            download_filename = filename
            message = "File uploaded and processed successfully. You can now download the CSV file."
           
        
    return render_template('checker.html', form=form, download_filename=f'check{download_filename}', message=message, folder_name=folder_name, table=table_checker)