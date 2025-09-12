from flask import Flask, request, jsonify
import pickle
import pandas as pd
from flask_cors import CORS
# CORS(app)

# Load model + encoders
with open("fertilizer_model.pkl", "rb") as f:
    saved_data = pickle.load(f)

model = saved_data["model"]
fert_encoder = saved_data["fert_encoder"]

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        print("Incoming Data:", data)  # Debugging

        N = data["N"]        # Map to Nitrogen
        P = data["P"]        # Map to Phosphorus
        K = data["K"]        # Map to Potassium

        X = pd.DataFrame([[N, K, P]],
                         columns=["Nitrogen", "Potassium", "Phosphorus"])

        # Predict
        prediction = model.predict(X)[0]
        fert_name = fert_encoder.inverse_transform([prediction])[0]

        return jsonify({"fertilizer": fert_name}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True)
