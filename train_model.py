import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
import joblib

# Load dataset
data = pd.read_csv("dataset/crop_data.csv")

# Convert crop names into numbers
encoder = LabelEncoder()
data["Crop"] = encoder.fit_transform(data["Crop"])

# Features and Target
X = data[["Crop", "Rainfall", "Temperature", "Humidity"]]
y = data["Yield"]

# Train Model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Save Model and Encoder
joblib.dump(model, "crop_model.pkl")
joblib.dump(encoder, "label_encoder.pkl")

print("✅ Model Trained Successfully!")
print("Files Created:")
print("1. crop_model.pkl")
print("2. label_encoder.pkl")