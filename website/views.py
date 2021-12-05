from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_file
from flask_login import login_required, current_user
from sqlalchemy.sql.expression import false
from werkzeug.utils import secure_filename
from .models import Note
from .models import File
from . import db
import json
from io import BytesIO
import smtplib
from email.mime.text import MIMEText

views = Blueprint('views', __name__)

ALLOWED_Extension = { 'js' }

def allowed_file(filename: str ) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_Extension

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        try:
            if len(note) < 1:
                flash('Note is too short!', category='error')
            else:
                new_note = Note(data=note, user_id=current_user.id)
                db.session.add(new_note)
                db.session.commit()
                flash('Note added!', category='success')
        except Exception:
            flash('Sorry, there was an error', category='error')

    return render_template("home.html", user=current_user)

@views.route('/send-idea', methods=['GET','POST'])
@login_required
def send_mail():
    if request.method =='POST':
        contact_name = request.form.get('contact-name')
        contact_email = request.form.get('contact-email')
        contact_message = request.form.get('contact-message')

        port = 2525
        smtp_server = 'smtp.mailtrap.io'
        login = 'd240b098e3c69d'
        password = '59a4cf6b3e3ee1'

        if contact_name=="" or contact_email=="" or contact_message=="":
            flash('Sorry, one of the fields was empty', category='error')
            return redirect(request.url)

        message = f"<h3>New Idea Submission</h3><ul><li>Customer: {contact_name} </li><li>Email: {contact_email} </li><li>Customer: {contact_message} </li></ul>"
        
        sender_email = contact_email
        receiver_email = "email@example.com"
        msg = MIMEText(message, 'html')
        msg['Subject'] = "New Project Idea"
        msg['Froms'] = sender_email
        msg['To'] = receiver_email

        #send email

        with smtplib.SMTP(smtp_server,port) as server:
            server.login(login, password)
            server.sendmail(sender_email,receiver_email, msg.as_string())


        return render_template("home.html", user=current_user)

    return render_template("home.html", user=current_user)


@views.route('/upload-file', methods=['Get', 'POST'])
@login_required
def code_file():
    if request.method =='POST':
        
        file = request.files.get('file')
        

        if file.filename == '':
            flash('No file was selected', category='error')
            return render_template("home.html", user=current_user)
            
        if allowed_file(file.filename) == false:
            flash('Wrong file type', category='error')
            return redirect(request.url)


        if file and allowed_file(file.filename):
            new_file = File(name=file.filename, data=file.read(), user_id=current_user.id)
            db.session.add(new_file)
            db.session.commit()
            flash('File uploaded successfully!', category='success')
            return render_template("home.html", user=current_user) 

    return render_template("home.html", user=current_user) 



@views.route('/add-files', methods=['GET'])
@login_required
def files():
    items = File().query.filter(user_id = current_user.id).all()
    return render_template("home.html", user = current_user, items = items)




@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/download/<int:id>', methods=['GET'])
def download(id):
    item = File().query.filter_by(id=id).first()
    return send_file(BytesIO(item.data), mimetype='text/javascript', as_attachment = True, attachment_filename=item.name)


@views.route('/delete-file', methods=['POST'])
def delete_file():
    file = json.loads(request.data)
    fileId = file['fileId']
    file = File.query.get(fileId)
    if file:
        if file.user_id == current_user.id:
            db.session.delete(file)
            db.session.commit()

    return jsonify({})

    

