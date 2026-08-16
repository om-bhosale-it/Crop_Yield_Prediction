import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request
import joblib

# ✅ static_folder='.' आणि static_url_path='' मुळे CSS आणि Images बाहेरूनच लोड होतील
app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')


# ==============================
# LOAD ML MODEL
# ==============================

model = joblib.load("crop_model.pkl")
encoder = joblib.load("label_encoder.pkl")

fertilizer_data = pd.read_csv("fertilizer_data.csv")


# ==============================
# HOME
# ==============================

@app.route("/")
def home():
    return render_template("index.html")


# ==============================
# CROP YIELD PREDICTION
# ==============================

@app.route("/predict", methods=["POST"])
def predict():

    crop = request.form["crop"]
    rainfall = float(request.form["rainfall"])
    temperature = float(request.form["temperature"])
    humidity = float(request.form["humidity"])

    if crop not in encoder.classes_:
        return render_template(
            "index.html",
            error="❌ Invalid Crop Selected."
        )

    crop_encoded = encoder.transform([crop])[0]

    prediction = model.predict(
        [[
            crop_encoded,
            rainfall,
            temperature,
            humidity
        ]]
    )

    return render_template(
        "result.html",
        crop=crop,
        prediction=round(prediction[0], 2)
    )


# ==============================
# FERTILIZER PAGE
# ==============================
@app.route('/fertilizer', methods=['GET', 'POST'])
def fertilizer():
    # ... तुमचा जुना मॅचिंगचा कोड ...
    
    # render_template करताना सर्व variables पाठवणे गरजेचे आहे:
    return render_template(
        'fertilizer_menu.html',
        crop=crop,
        variety=variety,
        days=days,
        height=height,
        recommendations=recommendations,
        weedicide=weedicide,
        weed_dose=weed_dose
    )


# ==============================
# FERTILIZER RESULT
# ==============================

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

    required_columns = [
        "Crop", "Variety", "Soil_Type", "Season",
        "Irrigation", "Region", "Min_Days", "Max_Days",
        "Fertilizer", "Dose", "Weedicide", "Weed_Dose"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in fertilizer_data.columns
    ]

    if missing_columns:
        return (
            "<h2>CSV Column Error</h2>"
            f"<p>Missing columns: {', '.join(missing_columns)}</p>"
        )

    def match_value(csv_value, user_value):
        csv_value = str(csv_value).strip()
        user_value = str(user_value).strip()

        if csv_value.lower() == "any":
            return True

        return csv_value.lower() == user_value.lower()

    matches = fertilizer_data[
        (fertilizer_data["Crop"].astype(str).str.strip().str.lower()
         == crop.strip().lower())
        &
        (fertilizer_data["Min_Days"] <= days)
        &
        (fertilizer_data["Max_Days"] >= days)
    ]

    matches = matches[
        matches["Variety"].apply(lambda x: match_value(x, variety))
        &
        matches["Soil_Type"].apply(lambda x: match_value(x, soil_type))
        &
        matches["Season"].apply(lambda x: match_value(x, season))
        &
        matches["Irrigation"].apply(lambda x: match_value(x, irrigation))
        &
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
    weedicide = first_result["Weedicide"]
    weed_dose = first_result["Weed_Dose"]

    return render_template(
        "fertilizer_menu.html",
        crop=crop, variety=variety, soil_type=soil_type,
        season=season, irrigation=irrigation, region=region,
        days=days, height=height, recommendations=recommendations,
        weedicide=weedicide, weed_dose=weed_dose, no_recommendation=False
    )

@app.route("/fertilizer_dose")
def fertilizer_dose():
    return render_template(
        "fertilizer_dose.html",
        crop=request.args.get("crop"),
        variety=request.args.get("variety"),
        days=request.args.get("days"),
        height=request.args.get("height"),
        fertilizer=request.args.get("fertilizer"),
        dose=request.args.get("dose")
    )


# ==============================
# WEED CONTROL PAGE
# ==============================

@app.route('/weed_control')
def weed_control():
    crop = request.args.get('crop', 'N/A')
    variety = request.args.get('variety', 'N/A')
    days = request.args.get('days', '0')
    height = request.args.get('height', '0')
    weedicide = request.args.get('weedicide', 'None')
    weed_dose = request.args.get('weed_dose', 'N/A')

    return render_template(
        'weed_control.html',
        crop=crop,
        variety=variety,
        days=days,
        height=height,
        weedicide=weedicide,
        weed_dose=weed_dose
    )

# ==============================
# RUN APPLICATION
# ==============================

if __name__ == "__main__":
    app.run(debug=True)
