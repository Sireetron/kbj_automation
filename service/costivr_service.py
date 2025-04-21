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
app.config['UPLOAD_FOLDER_COST_IVR'] = './costivr/input'
 


class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")


def costivr_service():
    folder_mapping = {
        'costivr': 'UPLOAD_FOLDER_COST_IVR',
    }
    folder_name = 'costivr'
    form = UploadFileForm()
    file_list = []

    if 'messages' not in session:
            session['messages'] = [] 
            
             
    upload_folder = app.config.get(folder_mapping.get(folder_name))
    file_list = []
    if upload_folder and os.path.exists(upload_folder):
        file_list = os.listdir(upload_folder)
            
            
    if form.validate_on_submit():
        section = request.form.get("submit_section")  
        files = request.files.getlist(f"file_{section}")  
        if section and files:
                upload_folder = app.config.get(folder_mapping.get(section))  

                    
                    
                saved_files = []
                for file in files:
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        # original_name = secure_filename(file.filename)
                        name_only, file_ext = os.path.splitext(filename)
                        base_name = name_only.split('-')[0].strip()
                        # print('base_name',base_name)
                        # print('file_ext',file_ext)
                        new_filename = f"{base_name}{file_ext}"
                        filepath = os.path.join(upload_folder, new_filename)
                        file.save(filepath)
                        saved_files.append(new_filename)
                        
                        
                if saved_files:
                    message = f"Files uploaded to {section} successfully: {', '.join(saved_files)}"
                    session['messages'].append(message) 
                else:
                    session['messages'].append(f"No valid files uploaded to {section}.")

                
           
        
    return render_template('costivr.html', form=form, download_filename=f'costivr.xlsx', messages=session.get('messages', []), folder_name=folder_name, file_list=file_list)
