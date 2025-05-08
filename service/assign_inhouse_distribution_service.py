from flask import Flask, render_template, request, send_from_directory
import os
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from checker.checker_app import checker
from flask import session
import glob
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER_ASSIGN'] = './assign_distribution/input/assign'
app.config['UPLOAD_FOLDER_PORTION'] = './assign_distribution/input/portion'
app.config['UPLOAD_FOLDER_PARAMETER'] = './assign_distribution/input/parameter'
app.config['DOWNLOAD_FOLDER_ASSIGN'] = './assign_distribution/output' 


class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")

def assign_inhouse_distribution_service():
    folder_mapping = {
        'assign': 'UPLOAD_FOLDER_ASSIGN',
        'portion': 'UPLOAD_FOLDER_PORTION',
         'parameter': 'UPLOAD_FOLDER_PARAMETER',
    }
    folder_name = 'assign-inhouse'
    form = UploadFileForm()
    download_filename = []  
    message = f"--------------------------------------------------------------------------------------------"
    
    if 'messages' not in session:
            session['messages'] = []  
            
    if form.validate_on_submit():
        section = request.form.get("submit_section")  # Get which button was pressed
        files = request.files.getlist(f"file_{section}")  # Get files based on section

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

                # download_filename = saved_files[0] if saved_files else None 
           
    file_assign = glob.glob("./assign_distribution/input/assign/*.xlsx")
    file_path =  re.sub(r'\.(csv|xlsx)$', '', file_assign[0].split('\\')[1])   
    return render_template('assign.html', form=form, download_filename=f'assign_inhouse_{file_path}.xlsx', messages=session.get('messages', []), folder_name=folder_name)
