import os
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import jwt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key-change-in-production')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), default='student')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.String(50))
    monthly_fee = db.Column(db.Integer, nullable=True)
    admission_fee = db.Column(db.Integer, nullable=True)
    full_payment = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500), default='https://via.placeholder.com/400x250?text=Course')

def generate_token(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            if data['role'] != 'admin':
                return jsonify({'message': 'Admin access required'}), 403
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 409
    new_user = User(name=data['name'], email=data['email'], password=hashed, role='student')
    db.session.add(new_user)
    db.session.commit()
    token = generate_token(new_user)
    return jsonify({'token': token, 'user': {'id': new_user.id, 'name': new_user.name, 'email': new_user.email, 'role': 'student'}})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        token = generate_token(user)
        return jsonify({'token': token, 'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role}})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email'], role='admin').first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        token = generate_token(user)
        return jsonify({'token': token, 'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': 'admin'}})
    return jsonify({'message': 'Invalid admin credentials'}), 401

@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    result = []
    for c in courses:
        result.append({
            'id': c.id,
            'name': c.name,
            'duration': c.duration or '',
            'monthly_fee': c.monthly_fee,
            'admission_fee': c.admission_fee,
            'full_payment': c.full_payment,
            'image_url': c.image_url
        })
    return jsonify(result)

@app.route('/api/admin/courses', methods=['POST'])
@admin_required
def add_course(current_user):
    data = request.get_json()
    course = Course(
        name=data['name'],
        duration=data.get('duration', ''),
        monthly_fee=data.get('monthly_fee'),
        admission_fee=data.get('admission_fee'),
        full_payment=data['full_payment'],
        image_url=data.get('image_url', 'https://via.placeholder.com/400x250?text=Course')
    )
    db.session.add(course)
    db.session.commit()
    return jsonify({'message': 'Course added'}), 201

@app.cli.command("seed-db")
def seed_db():
    if not User.query.filter_by(email='admin@alayya.com').first():
        admin = User(name='Admin', email='admin@alayya.com',
                     password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                     role='admin')
        db.session.add(admin)

    courses = [
        {"name":"Advanced MS Office","duration":"3 Months","monthly_fee":3000,"admission_fee":1000,"full_payment":8000},
        {"name":"Professional Certificate in IT (CIT)","duration":"6 Months","monthly_fee":4000,"admission_fee":1000,"full_payment":22000},
        {"name":"Advanced Diploma in IT (DIT)","duration":"1 Year","monthly_fee":5000,"admission_fee":1000,"full_payment":50000},
        {"name":"Certificate in Digital Graphic Designing","duration":"6 Months","monthly_fee":4000,"admission_fee":1000,"full_payment":22000},
        {"name":"AutoCAD 2D & 3D","duration":"3 Months","monthly_fee":5000,"admission_fee":1000,"full_payment":12000},
        {"name":"Diploma in Computerized Accounting","duration":"6 Months","monthly_fee":4000,"admission_fee":1000,"full_payment":22000},
        {"name":"Data Analytics (Excel & Power BI)","duration":"4 Months","monthly_fee":4000,"admission_fee":1000,"full_payment":15000},
        {"name":"Diploma in Frontend Web Development","duration":"6 Months","monthly_fee":5000,"admission_fee":1000,"full_payment":28000},
        {"name":"Certificate in Video Editing","duration":"2 Months","monthly_fee":7000,"admission_fee":1000,"full_payment":12000},
        {"name":"Certificate in Digital Marketing & SEO","duration":"4 Months","monthly_fee":7000,"admission_fee":1000,"full_payment":25000},
        {"name":"E-Commerce + Freelancing","duration":"2 Months","monthly_fee":None,"admission_fee":None,"full_payment":20000},
        {"name":"Certificate in WordPress Web Development","duration":"2 Months","monthly_fee":None,"admission_fee":None,"full_payment":10000},
        {"name":"Facebook Marketing","duration":"2 Months","monthly_fee":None,"admission_fee":None,"full_payment":10000},
        {"name":"Shopify Drop Shipping","duration":"2 Months","monthly_fee":None,"admission_fee":None,"full_payment":15000},
        {"name":"Cyber Security","duration":"2 Months","monthly_fee":None,"admission_fee":None,"full_payment":10000},
        {"name":"Artificial Intelligence","duration":"2 Months","monthly_fee":None,"admission_fee":None,"full_payment":15000}
    ]

    for c in courses:
        if not Course.query.filter_by(name=c['name']).first():
            db.session.add(Course(**c))
    db.session.commit()
    print("Database seeded!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
