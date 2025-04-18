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
app.config['UPLOAD_FOLDER_SMS'] = './checker/input/assign_input'
app.config['UPLOAD_FOLDER_ACC'] = './checker/input/acc'
app.config['DOWNLOAD_FOLDER_SMS'] = './checker/output' 
# app.config['DOWNLOAD_CSCORE'] = 'cscore/output/' 


class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")

table_checker = [
    { "contract_no": "3250800192489", "mobile_no": "0812345678","sms_type":"C4C"},
    { "contract_no": "1819900360011", "mobile_no": "0836654587","sms_type":"H4C"},
]


def sms_checker_service():
    folder_mapping = {
        'assign_input': 'UPLOAD_FOLDER_SMS',
        'acc': 'UPLOAD_FOLDER_ACC',
    }
    folder_name = 'sms-checker'
    form = UploadFileForm()
    download_filename = []  
    message = f"--------------------------------------------------------------------------------------------"
    
    if 'messages' not in session:
            session['messages'] = []  
            
    if form.validate_on_submit():
        section = request.form.get("submit_section")  # Get which button was pressed
        files = request.files.getlist(f"file_{section}")  # Get files based on section
        # print('section',section)
        # print('files',files)
        if section and files:
                upload_folder = app.config.get(folder_mapping.get(section))  # Default folder
                # print('upload_folder',upload_folder)
                for file in glob.glob(os.path.join(upload_folder, "*")):
                    os.remove(file)
                # files_assign = glob.glob('cscore/input/assign_data/*.xlsx') + glob.glob('cscore/input/assign_data/*.csv')
                # for file in files_assign:
                #     os.remove(file)
                    
                    
                saved_files = []
                for file in files:
                    # print('file',file)
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(upload_folder, filename)
                        file.save(filepath)
                        saved_files.append(filename)
                if saved_files:
                    message = f"Files uploaded to {section} successfully: {', '.join(saved_files)}"
                    session['messages'].append(message)  # Append message to session
                else:
                    session['messages'].append(f"No valid files uploaded to {section}.")

                download_filename = saved_files[0] if saved_files else None 
           
        
    return render_template('checker.html', form=form, download_filename=f'smscheck.xlsx', messages=session.get('messages', []), folder_name=folder_name, table=table_checker)
