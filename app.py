from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
JWT_SECRET = os.environ.get("JWT_SECRET", "fallback-secret")
import pickle
import pandas as pd
from models import Base, User, Recommendation
from auth import hash_password, check_password, generate_token, verify_token

app = Flask(__name__)
CORS(app)

# Database setup
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///fertilizer.db'
)

# Fix SSL root cert issue for CockroachDB on Render
if "cockroachlabs.cloud" in DATABASE_URL and "sslrootcert" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace(
        "sslrootcert=C:\\path\\to\\cc-ca.crt",
        "sslrootcert=system"
    )

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Load ML model
with open("ML/fertilizer_model.pkl", "rb") as f:
    saved_data = pickle.load(f)
model = saved_data["model"]
fert_encoder = saved_data["fert_encoder"]

# Create tables
Base.metadata.create_all(engine)

# Insert sample data if empty
session = Session()
if session.query(Recommendation).count() == 0:
    sample_data = [
        Recommendation(crop='Wheat', n=41, p=0, k=0, fertilizer='Urea'),
        Recommendation(crop='Rice', n=41, p=0, k=0, fertilizer='Urea'),
        Recommendation(crop='Maize', n=41, p=0, k=0, fertilizer='Urea'),
        Recommendation(crop='Sugarcane', n=41, p=0, k=0, fertilizer='Urea'),
        Recommendation(crop='Wheat', n=13, p=0, k=0, fertilizer='DAP'),
        Recommendation(crop='Rice', n=13, p=0, k=0, fertilizer='DAP'),
        Recommendation(crop='Maize', n=13, p=0, k=0, fertilizer='DAP'),
        Recommendation(crop='Sugarcane', n=13, p=0, k=0, fertilizer='DAP'),
    ]
    session.add_all(sample_data)
    session.commit()
session.close()

@app.route('/api/test-db', methods=['GET'])
def test_db():
    try:
        session = Session()
        result = session.execute(text("SELECT NOW() as time")).fetchone()
        session.close()
        return jsonify({'success': True, 'time': str(result[0])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    session = Session()
    if session.query(User).filter_by(username=username).first():
        session.close()
        return jsonify({'error': 'Username already exists'}), 400
    
    hashed = hash_password(password)
    user = User(username=username, password=hashed)
    session.add(user)
    session.commit()
    session.close()
    return jsonify({'message': 'Signup successful'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    
    if not user or not check_password(password, user.password):
        return jsonify({'error': 'Invalid credentials'}), 400
    
    token = generate_token(username)
    return jsonify({'token': token})

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    crop = data.get('crop')
    N = data.get('N')
    P = data.get('P')
    K = data.get('K')
    
    session = Session()
    rec = session.query(Recommendation).filter(
        Recommendation.crop == crop,
        Recommendation.n <= N,
        Recommendation.p <= P,
        Recommendation.k <= K
    ).order_by(Recommendation.id).first()
    session.close()
    
    if rec:
        return jsonify({'fertilizer': rec.fertilizer})
    else:
        return jsonify({'fertilizer': 'No recommendation found for given values'})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        N = data['N']
        P = data['P']
        K = data['K']
        
        X = pd.DataFrame([[N, K, P]], columns=["Nitrogen", "Potassium", "Phosphorus"])
        prediction = model.predict(X)[0]
        fert_name = fert_encoder.inverse_transform([prediction])[0]
        
        return jsonify({'fertilizer': fert_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
