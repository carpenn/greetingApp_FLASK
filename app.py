import os
from PIL import Image
import secrets
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from predict_breed import classify_dog

UPLOAD_FOLDER = 'static/uploads/'
DEFAULT_IMAGE = 'default.jpg'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_FILE'] = DEFAULT_IMAGE
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'jfif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_picture(form_picture):
  random_hex = secrets.token_hex(8)
  _, f_ext = os.path.splitext(form_picture.filename)
  picture_fn = random_hex + f_ext
  picture_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], picture_fn)

  output_size = (512, 512)
  i = Image.open(form_picture)
  i.thumbnail(output_size)
  i.save(picture_path)

  i, pred_text, labels, values  = classify_dog(picture_path)
  i.save(picture_path)

  return picture_fn, pred_text, labels, values

@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_image():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename):
    #picture_file = save_picture(secure_filename(file.filename))
		picture_file, pred_text, labels, values = save_picture(file)
		filename = picture_file
		#file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#print('upload_image filename: ' + filename)
		flash(pred_text)
		return render_template('upload.html', filename=filename, labels=labels, values=values)
	else:
		flash('Allowed image types are -> png, jpg, jpeg, gif')
		return redirect(request.url)
