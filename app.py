from flask import Flask, render_template, request, send_from_directory,send_file, session
import os
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from checker.checker_app import checker
from cscore_service import cscore
import zipfile
import io
from cscore.cscore_app import cscore_app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER_SMS'] = 'checker/input/assign_input'
app.config['DOWNLOAD_FOLDER_SMS'] = 'checker/output/' 
app.config['DOWNLOAD_CSCORE'] = 'cscore/output/' 


class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")

table_checker = [
    { "contract_no": "3250800192489", "mobile_no": "0000000","sms_type":"C4C"},
    { "contract_no": "1819900360011", "mobile_no": "0000000","sms_type":"H4C"},
]

folder_mapping = {
    'acc_current': 'UPLOAD_ACC_CURRENT',
    'acc_history': 'UPLOAD_ACC_HISTORY',
    'tdr': 'UPLOAD_TDR',
    'assign': 'UPLOAD_ASSIGN',
}
    

@app.route('/sms-checker', methods=['GET', 'POST'])
def smschecker():
    folder_name = 'sms-checker'
    form = UploadFileForm()
    download_filename = []  # Variable to hold download filename
    message = f"---"

    if form.validate_on_submit():
        file = form.file.data  # Get the uploaded file
        if file:  # EnFsure the file is valid
            filename = secure_filename(file.filename)
            # print('filename',filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER_SMS'], filename)
            file.save(filepath)
            checker()  # Run your processing function
            # print('filename',filename)
            
            # download_filename = filename.replace('.xlsx', '.csv')  # Example conversion
            download_filename = filename
            print('download_filename',download_filename)
            # download_filename.append(filename.replace('.xlsx', '.csv'))
            message = "File uploaded and processed successfully. You can now download the CSV file."
           
    return render_template('checker.html', form=form, download_filename=f'check{download_filename}', message=message, folder_name=folder_name, table=table_checker)






@app.route('/multipleupload', methods=['GET', 'POST'])
def upload():
    folder_name = 'cscore'
    form = UploadFileForm()
    download_filename = [] 
    message = f"-----"
    if request.method == 'POST':
        for f in request.files.getlist('file_name'):
            
            f.save(os.path.join(app.config['UPLOAD_FOLDER_SMS'],f.filename))
            message = "File uploaded and processed successfully. You can now download the CSV file."
        return render_template('upload.html', message=message)
    return render_template('upload.html', message='Please choose file')




@app.route('/cscore', methods=['GET', 'POST'])
def monthly_cscore():
    return cscore()  # Call the function and store the result



@app.route('/download/<folder>/<filename>')
def download_file(folder,filename):
    if folder == 'sms-checker':
            download_path = os.path.abspath(app.config['DOWNLOAD_FOLDER_SMS'])  # Default download folder
    else:
        return "Folder not found", 404  # Handle invalid folder name
    
    return send_from_directory(download_path, filename, as_attachment=True)




@app.route('/download/<folder_name>')
def process_and_download_file_cscore(folder_name):
    cscore_app()
    folder_path = f'./cscore/output'
    if not os.path.exists(folder_path):
        return "Folder does not exist", 404

    zip_buffer = io.BytesIO()  # Create an in-memory zip file
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

    zip_buffer.seek(0)  # Reset buffer position
    return send_file(zip_buffer, as_attachment=True, download_name=f"{folder_name}.zip", mimetype='application/zip')



if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)