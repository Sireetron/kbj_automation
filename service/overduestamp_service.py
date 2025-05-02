from flask import Flask, render_template, request
import os
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from flask import session
import glob

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER_AR'] = './overdue_oa/input/acc'
app.config['UPLOAD_FOLDER_LOAN_TARGET'] = './overdue_oa/input/loan'
app.config['DOWNLOAD_FOLDER_STARTDUE'] = './overdue_oa/input/start_due' 
 


class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")


def overdue_stamp_service():
    folder_mapping = {
        'ar': 'UPLOAD_FOLDER_AR',
        'loan_target': 'UPLOAD_FOLDER_LOAN_TARGET',
        'startdue':'DOWNLOAD_FOLDER_STARTDUE'
    }
    folder_name = 'overdue-stamp'
    form = UploadFileForm()


    if 'messages' not in session:
            session['messages'] = []  
            
    if form.validate_on_submit():
        section = request.form.get("submit_section")  
        files = request.files.getlist(f"file_{section}")  
        if section and files:
                upload_folder = app.config.get(folder_mapping.get(section))  
                for file in glob.glob(os.path.join(upload_folder, "*")):
                    os.remove(file)

                    
                    
                saved_files = []
                for file in files:
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(upload_folder, filename)
                        file.save(filepath)
                        saved_files.append(filename)
                if saved_files:
                    message = f"Files uploaded to {section} successfully: {', '.join(saved_files)}"
                    session['messages'].append(message) 
                else:
                    session['messages'].append(f"No valid files uploaded to {section}.")

                
           
        
    return render_template('overduestamp.html', form=form, download_filename=f'output.xlsx', messages=session.get('messages', []), folder_name=folder_name)
