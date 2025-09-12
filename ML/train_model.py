import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load dataset
data = pd.read_csv("fertilizer_data.csv")

# Features and target
X = data[["Nitrogen", "Potassium", "Phosphorus"]].copy()
y = data["Fertilizer"]

fert_encoder = LabelEncoder()
y = fert_encoder.fit_transform(y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
acc = model.score(X_test, y_test)
print(f"Model Accuracy: {acc:.2f}")

# Save model + encoders
with open("fertilizer_model.pkl", "wb") as f:
    pickle.dump({
        "model": model,
        "fert_encoder": fert_encoder
    }, f)
