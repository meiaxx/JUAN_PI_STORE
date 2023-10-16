import os
import random
import string
import re
from dotenv import load_dotenv

# buscará un .envarchivo y, si encuentra uno, cargará las variables de entorno del archivo y las hará accesibles
load_dotenv()

# Flask imports
from flask import Flask,render_template,url_for,request,flash,redirect,session,send_from_directory
from flask_mail import Mail,Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from functools import wraps
from datetime import *

app = Flask(__name__)


# random string generator
characters = string.digits + string.ascii_letters + string.punctuation
length = 64

app.config['SECRET_KEY'] = "".join(random.sample(characters, length))

# token security
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Configuration to database
DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = 'password'
DB_NAME = 'juan_pi'

# email config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
  
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
  
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Email Sender
class EmailSender:
    @staticmethod
    def send_reset_password(user,reset_link):
        msg = Message('Restablecer Contraseña',sender='upttinfo@gmail.com',recipients=[user])
        
        msg.html = render_template('reset_password_email.html', user=user, reset_link=reset_link)

        try:
            mail.send(msg)
            return True
        except Exception as e:
            return False

def generate_reset_link(email):
    # Genera un token que expirará en 1 hora (3600 segundos)
    token = serializer.dumps(email, salt='reset-password-salt')
    return token

def validate_reset_token(token):
    try:
        # Verifica y descifra el token
        email = serializer.loads(token, salt='reset-password-salt', max_age=3600)
        return email
    except SignatureExpired:
        # El token ha caducado
        return None
    except BadSignature:
        # El token es inválido
        return None
