import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request
import joblib

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

# Load Model & CSV
model = joblib.load("crop_model.pkl")
encoder = joblib.load("label_encoder.pkl")
fertilizer_data = pd.read_csv("fertilizer_data.csv")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    crop = request.form["crop"]
    rainfall = float(request.form["rainfall"])
    temperature = float(request.form["temperature"])
    humidity = float(request.form["humidity"])

    if crop not in encoder.classes_:
        return render_template("index.html", error="❌ Invalid Crop Selected.")

    crop_encoded = encoder.transform([crop])[0]
    prediction = model.predict([[crop_encoded, rainfall, temperature, humidity]])

    return render_template("result.html", crop=crop, prediction=round(prediction[0], 2))

@app.route('/fertilizer', methods=['GET', 'POST'])
def fertilizer():
    return render_template('fertilizer.html')

@app.route("/fertilizer_result", methods=["POST"])
def fertilizer_result():
    crop = request.form["crop"]
    variety = request.form["variety"]
    soil_type = request.form["soil_type"]
    season = request.form["season"]
    irrigation = request.form["irrigation"]
    region = request.form["region"]
    plant_date = request.form["plant_date"]
    height = float(request.form["height"])

    today = datetime.today()
    planting = datetime.strptime(plant_date, "%Y-%m-%d")
    days = (today - planting).days

    if days < 0:
        return "Invalid plantation date."

    def match_value(csv_value, user_value):
        csv_val = str(csv_value).strip()
        user_val = str(user_value).strip()
        if csv_val.lower() == "any":
            return True
        return csv_val.lower() == user_val.lower()

    matches = fertilizer_data[
        (fertilizer_data["Crop"].astype(str).str.strip().str.lower() == crop.strip().lower()) &
        (fertilizer_data["Min_Days"] <= days) &
        (fertilizer_data["Max_Days"] >= days)
    ]

    matches = matches[
        matches["Variety"].apply(lambda x: match_value(x, variety)) &
        matches["Soil_Type"].apply(lambda x: match_value(x, soil_type)) &
        matches["Season"].apply(lambda x: match_value(x, season)) &
        matches["Irrigation"].apply(lambda x: match_value(x, irrigation)) &
        matches["Region"].apply(lambda x: match_value(x, region))
    ]

    if matches.empty:
        return render_template(
            "fertilizer_menu.html",
            crop=crop, variety=variety, soil_type=soil_type,
            season=season, irrigation=irrigation, region=region,
            days=days, height=height, recommendations=[],
            weedicide=None, weed_dose=None, no_recommendation=True
        )

    recommendations = matches.to_dict("records")
    first_result = matches.iloc[0]
    weedicide = str(first_result["Weedicide"])
    weed_dose = str(first_result["Weed_Dose"])

    return render_template(
        "fertilizer_menu.html",
        crop=crop, variety=variety, soil_type=soil_type,
        season=season, irrigation=irrigation, region=region,
        days=days, height=height, recommendations=recommendations,
        weedicide=weedicide, weed_dose=weed_dose, no_recommendation=False
    )

@app.route('/weed_control')
def weed_control():
    crop = request.args.get('crop', '')
    variety = request.args.get('variety', '')
    days = request.args.get('days', '')
    height = request.args.get('height', '')
    weedicide = request.args.get('weedicide', '')
    weed_dose = request.args.get('weed_dose', '')

    return render_template(
        'weed_control.html',
        crop=crop,
        variety=variety,
        days=days,
        height=height,
        weedicide=weedicide,
        weed_dose=weed_dose
    )

if __name__ == "__main__":
    app.run(debug=True)
