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
app.config['UPLOAD_ACC_CURRENT'] = './cscore/input/acc_current'
app.config['UPLOAD_ACC_HISTORY'] = './cscore/input/acc_history_monthly' 
app.config['UPLOAD_TDR'] = './cscore/input/tdr' 
app.config['UPLOAD_ASSIGN'] = './cscore/input/assign_data' 


class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")

def cscore_service():
    folder_mapping = {
        'acc_current': 'UPLOAD_ACC_CURRENT',
        'acc_history': 'UPLOAD_ACC_HISTORY',
        'tdr': 'UPLOAD_TDR',
        'assign': 'UPLOAD_ASSIGN',
    }
    
    folder_name = 'cscore'
    form = UploadFileForm()
    download_filename = None
    message = '----'
    
    if 'messages' not in session:
        session['messages'] = []  

    if form.validate_on_submit():
        section = request.form.get("submit_section")  # Get which button was pressed
        files = request.files.getlist(f"file_{section}")  # Get files based on section

        if section and files:
            upload_folder = app.config.get(folder_mapping.get(section))  # Default folder
            # print('upload_folder',upload_folder)
            for file in glob.glob(os.path.join(upload_folder, "*")):
                # print('file',file)
                os.remove(file)
            files_assign = glob.glob('./cscore/input/assign_data/*.xlsx') + glob.glob('cscore/input/assign_data/*.csv')
            for file in files_assign:
                os.remove(file)
                
            saved_files = []
            for file in files:
                # print('file',file)
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    # output_dir = "./cscore/input/"
                    # for file in glob.glob(os.path.join(output_dir, "*")):
                    #     os.remove(file)
                    
                    # print('filename',filename)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    saved_files.append(filename)
            if saved_files:
                message = f"Files uploaded to {section} successfully: {', '.join(saved_files)}"
                session['messages'].append(message)  # Append message to session
            else:
                session['messages'].append(f"No valid files uploaded to {section}.")

            download_filename = saved_files[0] if saved_files else None 
           
                

    return render_template(
        'cscore.html',
        form=form,
        download_filename=download_filename,  # Pass actual filename or None if not set
        messages=session.get('messages', []),  # Pass all status messages from the session
        folder_name=folder_name,  # Pass the folder name for context in the template
        outputpath= './cscore/output'
    )