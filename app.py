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

# 1. AI YIELD PREDICTION
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

    # Yield चा निकाल दाखवणे आणि पुढे crop चे नाव पाठवणे
    return render_template("result.html", crop=crop, prediction=round(prediction[0], 2))

# 2. FERTILIZER FORM PAGE
@app.route('/fertilizer', methods=['GET', 'POST'])
def fertilizer():
    crop = request.args.get('crop', '')
    return render_template('fertilizer.html', crop=crop)

# 3. FERTILIZER & WEED RESULT
# ==============================
# FERTILIZER RESULT (ERROR-FREE)
# ==============================
@app.route("/fertilizer_result", methods=["POST"])
def fertilizer_result():
    try:
        crop = request.form.get("crop", "").strip()
        variety = request.form.get("variety", "").strip()
        soil_type = request.form.get("soil_type", "").strip()
        season = request.form.get("season", "").strip()
        irrigation = request.form.get("irrigation", "").strip()
        region = request.form.get("region", "").strip()
        plant_date = request.form.get("plant_date", "").strip()
        
        # Height चेक करणे
        try:
            height = float(request.form.get("height", 0))
        except (ValueError, TypeError):
            height = 0.0

        # तारीख चेक करणे
        days = 0
        if plant_date:
            try:
                today = datetime.today()
                planting = datetime.strptime(plant_date, "%Y-%m-%d")
                days = (today - planting).days
            except ValueError:
                days = 0

        if days < 0:
            days = 0

        # CSV Columns तपासणे
        def match_value(csv_value, user_value):
            csv_val = str(csv_value).strip().lower()
            user_val = str(user_value).strip().lower()
            if csv_val == "any" or not user_val:
                return True
            return csv_val == user_val

        # CSV मधून फिल्टर करणे
        matches = fertilizer_data[
            (fertilizer_data["Crop"].astype(str).str.strip().str.lower() == crop.lower()) &
            (fertilizer_data["Min_Days"] <= days) &
            (fertilizer_data["Max_Days"] >= days)
        ]

        if not matches.empty:
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
        weedicide = str(first_result.get("Weedicide", "None"))
        weed_dose = str(first_result.get("Weed_Dose", "N/A"))

        return render_template(
            "fertilizer_menu.html",
            crop=crop, variety=variety, soil_type=soil_type,
            season=season, irrigation=irrigation, region=region,
            days=days, height=height, recommendations=recommendations,
            weedicide=weedicide, weed_dose=weed_dose, no_recommendation=False
        )

    except Exception as e:
        # जर काही क्रॅश झालेच तर ५०० एरर न दाखवता काय चूक आहे ते स्क्रीनवर दाखवेल
        return f"<h2>Application Error</h2><p>Detail: {str(e)}</p><a href='/fertilizer'>Go Back</a>"

# 4. WEED CONTROL DETAILS PAGE
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
