from flask import Flask, render_template, request
import pandas as pd
import os
from flask_wtf import FlaskForm
from wtforms import FileField,SubmitField
from werkzeug.utils import secure_filename
from checker.checker import checker


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'checker/input/assign_input'
# # Ensure folders exist
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")
    
# @app.route('/',methods=('GET','POST'))
@app.route('/sms-checker',methods=('GET','POST'))
def home(): 
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data  # This gets the uploaded file
        if file:  # Ensure the file is valid
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            checker()
                      
            return "File has been uploaded successfully!"
    return render_template('index.html',form=form)


if __name__ == '__main__':
    app.run(debug=True)

