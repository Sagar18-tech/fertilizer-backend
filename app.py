from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import pickle
import pandas as pd

from models import Base, User
from auth import hash_password, check_password, generate_token, verify_token

app = Flask(__name__)
CORS(app)

# Database setup (only for storing users)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///users.db')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Create user table
Base.metadata.create_all(engine)

# Load ML model
with open("ML/fertilizer_model.pkl", "rb") as f:
    saved_data = pickle.load(f)
model = saved_data["model"]
fert_encoder = saved_data["fert_encoder"]

# ---------- ROOT ROUTE ----------
@app.route("/")
def home():
    return jsonify({"message": "Fertilizer Recommendation API is running!"})

# ---------- AUTH ROUTES ----------
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

# ---------- ML MODEL PREDICTION ----------
@app.route('/recommend', methods=['POST']) 
def recommend():
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
