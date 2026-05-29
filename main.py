from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import string
import random
import qrcode
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class URL(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    original_url = db.Column(
        db.String(500),
        nullable=False
    )

    short_code = db.Column(
        db.String(10),
        unique=True,
        nullable=False
    )

    qr_code = db.Column(
        db.String(200),
        nullable=True
    )

def generate_shorten_url(length=6):
    chars = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(chars) for _ in range(length))    
    return short_url

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':

        original_url = request.form['original_url']
        short_url = generate_shorten_url()
        new_url = URL(
            original_url=original_url,
            short_code=short_url
        )
        db.session.add(new_url)
        db.session.commit()
        full_short_url = request.host_url + short_url
        qrcode_path = generate_qrcode(full_short_url)
        return render_template(
            'index.html',
            short_url=full_short_url,
            qrcode_path=qrcode_path
        )
    return render_template('index.html')

def generate_qrcode(short_url):

    img = qrcode.make(short_url)

    short_code = short_url.split("/")[-1]

    filename = f"static/{short_code}.png"

    img.save(filename)

    return filename

@app.route('/<short_url>')
def redirect_to_original(short_url):
    url_data = URL.query.filter_by(
        short_code=short_url
    ).first()
    if url_data:
        return redirect(url_data.original_url)
    else:
        return 'URL not found', 404

with app.app_context():
    db.create_all()
    app.run()