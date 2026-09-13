import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from src.predict import (
    predict_aqi_full_report,
    load_model_artifacts,
    FEATURE_COLUMNS
)

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Real-world preset test scenarios
PRESETS = [
    {
        "id": "clean",
        "title": "Clean Coastal / Hill Station",
        "subtitle": "Clear skies, low traffic & coastal breeze",
        "icon": "leaf",
        "tag": "Good (AQI < 50)",
        "tagColor": "#10B981",
        "tagClass": "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
        "dotClass": "bg-emerald-400 shadow-[0_0_6px_#10B981]",
        "values": {
            "PM2.5": 18.0,
            "PM10": 34.0,
            "NO": 4.5,
            "NO2": 12.0,
            "NOx": 14.5,
            "NH3": 6.2,
            "CO": 0.45,
            "SO2": 6.0,
            "O3": 22.0,
            "Benzene": 0.5,
            "Toluene": 1.2
        }
    },
    {
        "id": "satisfactory",
        "title": "Suburban Living Area",
        "subtitle": "Moderate activity with gentle dispersion",
        "icon": "sun",
        "tag": "Satisfactory (51-100)",
        "tagColor": "#84CC16",
        "tagClass": "text-lime-400 bg-lime-500/10 border-lime-500/30",
        "dotClass": "bg-lime-400 shadow-[0_0_6px_#84CC16]",
        "values": {
            "PM2.5": 45.0,
            "PM10": 78.0,
            "NO": 10.0,
            "NO2": 24.0,
            "NOx": 30.0,
            "NH3": 14.0,
            "CO": 0.8,
            "SO2": 11.0,
            "O3": 30.0,
            "Benzene": 1.5,
            "Toluene": 3.0
        }
    },
    {
        "id": "moderate",
        "title": "Typical Urban Daytime",
        "subtitle": "City traffic with mixed residential & commerce",
        "icon": "city",
        "tag": "Moderate (101-200)",
        "tagColor": "#F59E0B",
        "tagClass": "text-amber-400 bg-amber-500/10 border-amber-500/30",
        "dotClass": "bg-amber-400 shadow-[0_0_6px_#F59E0B]",
        "activeClass": "border-amber-500/80 bg-amber-500/10 text-white shadow-[0_0_15px_rgba(245,158,11,0.15)]",
        "values": {
            "PM2.5": 85.0,
            "PM10": 135.0,
            "NO": 18.0,
            "NO2": 38.0,
            "NOx": 48.0,
            "NH3": 22.0,
            "CO": 1.4,
            "SO2": 16.0,
            "O3": 42.0,
            "Benzene": 2.8,
            "Toluene": 5.8
        }
    },
    {
        "id": "poor",
        "title": "Heavy Congestion / Industrial",
        "subtitle": "Highway junctions, dense diesel emissions",
        "icon": "truck",
        "tag": "Poor (201-300)",
        "tagColor": "#F97316",
        "tagClass": "text-orange-400 bg-orange-500/10 border-orange-500/30",
        "dotClass": "bg-orange-400 shadow-[0_0_6px_#F97316]",
        "values": {
            "PM2.5": 145.0,
            "PM10": 230.0,
            "NO": 36.0,
            "NO2": 68.0,
            "NOx": 92.0,
            "NH3": 38.0,
            "CO": 2.4,
            "SO2": 26.0,
            "O3": 55.0,
            "Benzene": 5.2,
            "Toluene": 10.5
        }
    },
    {
        "id": "severe",
        "title": "Severe Winter Smog Inversion",
        "subtitle": "Trapped pollutants, calm winds & biomass smoke",
        "icon": "fire",
        "tag": "Severe (>400)",
        "tagColor": "#881337",
        "tagClass": "text-rose-400 bg-rose-500/10 border-rose-500/30",
        "dotClass": "bg-rose-400 shadow-[0_0_6px_#881337]",
        "values": {
            "PM2.5": 310.0,
            "PM10": 460.0,
            "NO": 65.0,
            "NO2": 115.0,
            "NOx": 170.0,
            "NH3": 68.0,
            "CO": 4.8,
            "SO2": 42.0,
            "O3": 72.0,
            "Benzene": 8.8,
            "Toluene": 18.0
        }
    }
]

# Feature metadata (units, recommended min/max, descriptions)
POLLUTANTS_META = [
    {
        "key": "PM2.5",
        "name": "Particulate Matter 2.5",
        "unit": "µg/m³",
        "group": "Particulate Matter",
        "desc": "Fine inhalable particles with diameters 2.5 micrometers and smaller.",
        "min": 0, "max": 500, "step": 1, "default": 85
    },
    {
        "key": "PM10",
        "name": "Particulate Matter 10",
        "unit": "µg/m³",
        "group": "Particulate Matter",
        "desc": "Inhalable coarse particles such as road dust, soot, and pollen.",
        "min": 0, "max": 600, "step": 1, "default": 135
    },
    {
        "key": "NO2",
        "name": "Nitrogen Dioxide",
        "unit": "µg/m³",
        "group": "Nitrogen Oxides",
        "desc": "Pungent gas produced primarily from vehicular traffic and power plants.",
        "min": 0, "max": 400, "step": 1, "default": 38
    },
    {
        "key": "NO",
        "name": "Nitric Oxide",
        "unit": "µg/m³",
        "group": "Nitrogen Oxides",
        "desc": "Combustion byproduct rapidly converting to NO2 in ambient air.",
        "min": 0, "max": 250, "step": 0.5, "default": 18
    },
    {
        "key": "NOx",
        "name": "Total Nitrogen Oxides",
        "unit": "µg/m³",
        "group": "Nitrogen Oxides",
        "desc": "Combined concentration of NO and NO2 reflecting heavy emissions.",
        "min": 0, "max": 500, "step": 1, "default": 48
    },
    {
        "key": "CO",
        "name": "Carbon Monoxide",
        "unit": "mg/m³",
        "group": "Carbon & Sulfur",
        "desc": "Colorless, odorless poisonous gas from incomplete engine combustion.",
        "min": 0, "max": 35, "step": 0.1, "default": 1.4
    },
    {
        "key": "SO2",
        "name": "Sulfur Dioxide",
        "unit": "µg/m³",
        "group": "Carbon & Sulfur",
        "desc": "Toxic gas emitted by fossil fuel combustion and industrial refineries.",
        "min": 0, "max": 300, "step": 0.5, "default": 16
    },
    {
        "key": "O3",
        "name": "Ground-level Ozone",
        "unit": "µg/m³",
        "group": "Secondary Pollutants",
        "desc": "Formed through photochemical reactions between sunlight, NOx, and VOCs.",
        "min": 0, "max": 300, "step": 1, "default": 42
    },
    {
        "key": "NH3",
        "name": "Ammonia",
        "unit": "µg/m³",
        "group": "Secondary Pollutants",
        "desc": "Emitted from fertilizer use, agricultural livestock, and urban waste.",
        "min": 0, "max": 500, "step": 1, "default": 22
    },
    {
        "key": "Benzene",
        "name": "Benzene (VOC)",
        "unit": "µg/m³",
        "group": "Volatile Organics",
        "desc": "Volatile aromatic hydrocarbon associated with petrochemical exhaust.",
        "min": 0, "max": 50, "step": 0.1, "default": 2.8
    },
    {
        "key": "Toluene",
        "name": "Toluene (VOC)",
        "unit": "µg/m³",
        "group": "Volatile Organics",
        "desc": "Industrial solvent vapor commonly present in urban motor exhaust.",
        "min": 0, "max": 100, "step": 0.1, "default": 5.8
    }
]


@app.route("/")
def index():
    model, _, _ = load_model_artifacts()
    model_status = "Random Forest Regressor (Trained)" if model is not None else "CPCB Benchmark Standards (Operational)"
    return render_template(
        "index.html",
        pollutants=POLLUTANTS_META,
        presets=PRESETS,
        model_status=model_status,
        is_ml=(model is not None)
    )


@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"success": False, "error": "No input JSON received"}), 400

        # Extract features and cast to float
        input_data = {}
        for col in FEATURE_COLUMNS:
            raw_val = data.get(col, 0)
            try:
                input_data[col] = float(raw_val)
            except (ValueError, TypeError):
                input_data[col] = 0.0

        report = predict_aqi_full_report(input_data)
        return jsonify({"success": True, "report": report})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/presets", methods=["GET"])
def api_presets():
    return jsonify({"success": True, "presets": PRESETS})


@app.route("/api/meta", methods=["GET"])
def api_meta():
    model, _, _ = load_model_artifacts()
    return jsonify({
        "success": True,
        "is_ml_model": (model is not None),
        "model_name": "Random Forest Regressor (100 Estimators)" if model is not None else "CPCB NAQI Standard Engine",
        "pollutants": POLLUTANTS_META
    })


if __name__ == "__main__":
    # Ensure port 5000 or custom port
    port = int(os.environ.get("PORT", 5000))
    print(f"\n* Starting AQI Web Application on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
