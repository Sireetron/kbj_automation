from flask import Flask, render_template, request, send_from_directory
import os
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from checker.checker import checker


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER_SMS'] = 'checker/input/assign_input'
app.config['DOWNLOAD_FOLDER_SMS'] = 'checker/output/'  # Specify the download folder


class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")

table_checker = [
    {"customer_no": '7240870103414270', "contract_no": "3250800192489", "customer_name": "อดุXX XXX", "mobile_no": "New York"},
    {"customer_no": '7241170104203800', "contract_no": "1819900360011", "customer_name": "บุญXX XXX", "mobile_no ": "San Francisco"},
]


@app.route('/sms-checker', methods=['GET', 'POST'])
def home():
    folder_name = 'sms'
    form = UploadFileForm()
    download_filename = []  # Variable to hold download filename
    message = f"Please upload a valid SMS_CHECKER file || column need to exactly match column name and type  * mobile_no : varchar * loan_no : varchar *customer_no : varchar"

    if form.validate_on_submit():
        file = form.file.data  # Get the uploaded file
        if file:  # EnFsure the file is valid
            filename = secure_filename(file.filename)
            # print('filename',filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER_SMS'], filename)
            file.save(filepath)
            checker()  # Run your processing function
            # print('filename',filename)
            
            download_filename = filename.replace('.xlsx', '.csv')  # Example conversion
            # download_filename.append(filename.replace('.xlsx', '.csv'))
            message = "File uploaded and processed successfully. You can now download the CSV file."
           
    return render_template('index.html', form=form, download_filename=f'check{download_filename}', message=message, folder_name=folder_name, table=table_checker)






@app.route('/upload_file', methods=['GET', 'POST'])
def upload():
    folder_name = 'sms'
    form = UploadFileForm()
    download_filename = [] 
    message = f"Please upload a valid SMS_CHECKER file || column need to exactly match column name and type  * mobile_no : varchar * loan_no : varchar *customer_no : varchar"
    if request.method == 'POST':
        for f in request.files.getlist('file_name'):
            
            f.save(os.path.join(app.config['UPLOAD_FOLDER_SMS'],f.filename))
            message = "File uploaded and processed successfully. You can now download the CSV file."
        return render_template('upload.html', message=message)
    return render_template('upload.html', message='Please choose file')






@app.route('/download/<folder>/<filename>')
def download_file(folder,filename):
    if folder == 'sms':
            download_path = os.path.abspath(app.config['DOWNLOAD_FOLDER_SMS'])  # Default download folder
    elif folder == 'version2':
        download_path = os.path.abspath(app.config['DOWNLOAD_FOLDER_2'])  # Different download folder
    else:
        return "Folder not found", 404  # Handle invalid folder name
    
    return send_from_directory(download_path, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)