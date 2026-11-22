import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(dotenv_path=BASE_DIR / ".env")

from src.predict import predict_aqi_full_report, load_model_artifacts, FEATURE_COLUMNS
from src.nearby_sources import find_nearby_pollutant_sources, CITY_CENTERS, haversine_distance
from src.realtime_api import fetch_live_air_quality

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)
app.secret_key = os.environ.get("SECRET_KEY", "aero-intel-default-secure-key-2026")
app.config["TEMPLATES_AUTO_RELOAD"] = True

AUTH_ENABLED = os.environ.get("AUTH_ENABLED", "true").lower() == "true"
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
API_ACCESS_TOKEN = os.environ.get("API_ACCESS_TOKEN", "aero-intel-token-2026")

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
        "city": "Bengaluru",
        "values": {
            "PM2.5": 18.0, "PM10": 34.0, "NO": 4.5, "NO2": 12.0, "NOx": 14.5,
            "NH3": 6.2, "CO": 0.45, "SO2": 6.0, "O3": 22.0, "Benzene": 0.5, "Toluene": 1.2
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
        "city": "Hyderabad",
        "values": {
            "PM2.5": 45.0, "PM10": 78.0, "NO": 10.0, "NO2": 24.0, "NOx": 30.0,
            "NH3": 14.0, "CO": 0.8, "SO2": 11.0, "O3": 30.0, "Benzene": 1.5, "Toluene": 3.0
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
        "city": "Mumbai",
        "values": {
            "PM2.5": 85.0, "PM10": 135.0, "NO": 18.0, "NO2": 38.0, "NOx": 48.0,
            "NH3": 22.0, "CO": 1.4, "SO2": 16.0, "O3": 42.0, "Benzene": 2.8, "Toluene": 5.8
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
        "city": "Kolkata",
        "values": {
            "PM2.5": 145.0, "PM10": 230.0, "NO": 36.0, "NO2": 68.0, "NOx": 92.0,
            "NH3": 38.0, "CO": 2.4, "SO2": 26.0, "O3": 55.0, "Benzene": 5.2, "Toluene": 10.5
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
        "city": "Delhi",
        "values": {
            "PM2.5": 310.0, "PM10": 460.0, "NO": 65.0, "NO2": 115.0, "NOx": 170.0,
            "NH3": 68.0, "CO": 4.8, "SO2": 42.0, "O3": 72.0, "Benzene": 8.8, "Toluene": 18.0
        }
    }
]

POLLUTANTS_META = [
    {"key": "PM2.5", "name": "Particulate Matter 2.5", "unit": "µg/m³", "group": "Particulate Matter", "desc": "Fine inhalable particles ≤ 2.5 µm.", "min": 0, "max": 500, "step": 1, "default": 85},
    {"key": "PM10", "name": "Particulate Matter 10", "unit": "µg/m³", "group": "Particulate Matter", "desc": "Inhalable coarse particles like dust and soot.", "min": 0, "max": 600, "step": 1, "default": 135},
    {"key": "NO2", "name": "Nitrogen Dioxide", "unit": "µg/m³", "group": "Nitrogen Oxides", "desc": "Gas from vehicular traffic and power plants.", "min": 0, "max": 400, "step": 1, "default": 38},
    {"key": "NO", "name": "Nitric Oxide", "unit": "µg/m³", "group": "Nitrogen Oxides", "desc": "Primary combustion gas converting to NO2.", "min": 0, "max": 250, "step": 0.5, "default": 18},
    {"key": "NOx", "name": "Total Nitrogen Oxides", "unit": "µg/m³", "group": "Nitrogen Oxides", "desc": "Combined concentration of NO and NO2.", "min": 0, "max": 500, "step": 1, "default": 48},
    {"key": "CO", "name": "Carbon Monoxide", "unit": "mg/m³", "group": "Carbon & Sulfur", "desc": "Gas from incomplete engine combustion.", "min": 0, "max": 35, "step": 0.1, "default": 1.4},
    {"key": "SO2", "name": "Sulfur Dioxide", "unit": "µg/m³", "group": "Carbon & Sulfur", "desc": "Gas from fossil fuel and industrial combustion.", "min": 0, "max": 300, "step": 0.5, "default": 16},
    {"key": "O3", "name": "Ground-level Ozone", "unit": "µg/m³", "group": "Secondary Pollutants", "desc": "Photochemical oxidant from NOx and VOCs.", "min": 0, "max": 300, "step": 1, "default": 42},
    {"key": "NH3", "name": "Ammonia", "unit": "µg/m³", "group": "Secondary Pollutants", "desc": "Agricultural and waste byproduct gas.", "min": 0, "max": 500, "step": 1, "default": 22},
    {"key": "Benzene", "name": "Benzene (VOC)", "unit": "µg/m³", "group": "Volatile Organics", "desc": "Aromatic hydrocarbon from fuel evaporation.", "min": 0, "max": 50, "step": 0.1, "default": 2.8},
    {"key": "Toluene", "name": "Toluene (VOC)", "unit": "µg/m³", "group": "Volatile Organics", "desc": "Industrial solvent vapor and fuel additive.", "min": 0, "max": 100, "step": 0.1, "default": 5.8}
]


@app.route("/favicon.ico")
def favicon_ico():
    resp = send_from_directory(
        str(BASE_DIR / "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/favicon.png")
def favicon_png():
    resp = send_from_directory(
        str(BASE_DIR / "static"),
        "favicon.png",
        mimetype="image/png"
    )
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/favicon.svg")
def favicon_svg():
    resp = send_from_directory(
        str(BASE_DIR / "static"),
        "favicon.svg",
        mimetype="image/svg+xml"
    )
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/apple-touch-icon.png")
def apple_touch_icon():
    resp = send_from_directory(
        str(BASE_DIR / "static"),
        "apple-touch-icon.png",
        mimetype="image/png"
    )
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/site.webmanifest")
def site_webmanifest():
    resp = send_from_directory(
        str(BASE_DIR / "static"),
        "site.webmanifest",
        mimetype="application/manifest+json"
    )
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/")
def index():
    if AUTH_ENABLED and not session.get("is_authenticated"):
        return redirect(url_for("login"))
    model, _, _ = load_model_artifacts()
    model_status = "Random Forest Regressor (Trained)" if model is not None else "CPCB Benchmark Standards (Operational)"
    return render_template(
        "index.html",
        pollutants=POLLUTANTS_META,
        presets=PRESETS,
        model_status=model_status,
        is_ml=(model is not None),
        city_centers=CITY_CENTERS,
        is_admin=session.get("is_admin", True),
        username=session.get("username", "admin"),
        auth_enabled=AUTH_ENABLED
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if not AUTH_ENABLED or session.get("is_authenticated"):
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        token = data.get("token", "").strip()

        if (username == ADMIN_USERNAME and password == ADMIN_PASSWORD) or (token and token == API_ACCESS_TOKEN):
            session["is_authenticated"] = True
            session["is_admin"] = True
            session["username"] = username or "admin"
            if request.is_json:
                return jsonify({"success": True, "redirect": url_for("index")})
            return redirect(url_for("index"))

        error = "Invalid credentials. Please verify your username and password."
        if request.is_json:
            return jsonify({"success": False, "error": error}), 401

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"success": False, "error": "No input JSON received"}), 400

        input_data = {}
        for col in FEATURE_COLUMNS:
            raw_val = data.get(col, None)
            if raw_val is not None and raw_val != "":
                try:
                    input_data[col] = float(raw_val)
                except (ValueError, TypeError):
                    input_data[col] = None
            else:
                input_data[col] = None

        report = predict_aqi_full_report(input_data)
        return jsonify({"success": True, "report": report})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/nearby-sources", methods=["GET"])
def api_nearby_sources():
    try:
        city = request.args.get("city", "").strip()
        if city in CITY_CENTERS and "lat" not in request.args:
            lat = CITY_CENTERS[city]["lat"]
            lon = CITY_CENTERS[city]["lon"]
        else:
            lat = float(request.args.get("lat", CITY_CENTERS["Delhi"]["lat"]))
            lon = float(request.args.get("lon", CITY_CENTERS["Delhi"]["lon"]))

        radius = float(request.args.get("radius", 35.0))
        wind_dir = request.args.get("wind_dir", None)
        wind_float = float(wind_dir) if wind_dir is not None and wind_dir != "" else None

        result = find_nearby_pollutant_sources(
            lat=lat,
            lon=lon,
            max_radius_km=radius,
            wind_direction=wind_float
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/realtime-air-quality", methods=["GET"])
def api_realtime_air_quality():
    try:
        lat = float(request.args.get("lat", CITY_CENTERS["Delhi"]["lat"]))
        lon = float(request.args.get("lon", CITY_CENTERS["Delhi"]["lon"]))
        city = request.args.get("city", "Delhi")

        telemetry = fetch_live_air_quality(lat=lat, lon=lon, city_name=city)
        return jsonify({"success": True, "telemetry": telemetry})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/presets", methods=["GET"])
def api_presets():
    return jsonify({"success": True, "presets": PRESETS})


@app.route("/api/cities", methods=["GET"])
def api_cities():
    return jsonify({"success": True, "cities": CITY_CENTERS})


OFFLINE_LOCALITIES = [
    {"name": "Shrirampur", "lat": 22.75, "lon": 88.34, "radius_km": 15},
    {"name": "Howrah", "lat": 22.5958, "lon": 88.2636, "radius_km": 15},
    {"name": "Salt Lake", "lat": 22.5867, "lon": 88.4178, "radius_km": 12},
    {"name": "New Town", "lat": 22.5851, "lon": 88.4616, "radius_km": 12},
    {"name": "Bandra", "lat": 19.0596, "lon": 72.8295, "radius_km": 10},
    {"name": "Andheri", "lat": 19.1136, "lon": 72.8697, "radius_km": 10},
    {"name": "Thane", "lat": 19.2183, "lon": 72.9781, "radius_km": 15},
    {"name": "Navi Mumbai", "lat": 19.0330, "lon": 73.0297, "radius_km": 20},
    {"name": "Noida", "lat": 28.5355, "lon": 77.3910, "radius_km": 15},
    {"name": "Gurugram", "lat": 28.4595, "lon": 77.0266, "radius_km": 20},
    {"name": "Ghaziabad", "lat": 28.6692, "lon": 77.4538, "radius_km": 15},
    {"name": "Whitefield", "lat": 12.9698, "lon": 77.7500, "radius_km": 12},
    {"name": "Electronic City", "lat": 12.8399, "lon": 77.6770, "radius_km": 12},
    {"name": "Secunderabad", "lat": 17.4399, "lon": 78.4983, "radius_km": 15},
]


@app.route("/api/reverse-geocode", methods=["GET"])
def api_reverse_geocode():
    try:
        lat = float(request.args.get("lat", 0.0))
        lon = float(request.args.get("lon", 0.0))
        if not lat or not lon:
            return jsonify({"success": False, "error": "Invalid coordinates"}), 400

        # 1. High-speed local locality lookup
        for item in OFFLINE_LOCALITIES:
            if haversine_distance(lat, lon, item["lat"], item["lon"]) <= item["radius_km"]:
                return jsonify({"success": True, "locality": item["name"]})

        # 2. Try BigDataCloud API
        try:
            url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=en"
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                loc = data.get("locality") or data.get("city") or data.get("principalSubdivision")
                if loc:
                    return jsonify({"success": True, "locality": loc})
        except Exception:
            pass

        # 2. Try OpenStreetMap Nominatim
        try:
            headers = {"User-Agent": "AeroIntel-AQI-Platform/2.6"}
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=14"
            resp = requests.get(url, headers=headers, timeout=3)
            if resp.status_code == 200:
                addr = resp.json().get("address", {})
                loc = (addr.get("suburb") or addr.get("town") or addr.get("city_district") or 
                       addr.get("city") or addr.get("village") or addr.get("county"))
                if loc:
                    return jsonify({"success": True, "locality": loc})
        except Exception:
            pass

        return jsonify({"success": False, "error": "Locality could not be determined"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/meta", methods=["GET"])
def api_meta():
    model, _, _ = load_model_artifacts()
    waqi_configured = bool(os.environ.get("WAQI_API_KEY", "").strip())
    return jsonify({
        "success": True,
        "is_ml_model": (model is not None),
        "model_name": "Random Forest Regressor (100 Estimators)" if model is not None else "CPCB NAQI Standard Engine",
        "pollutants": POLLUTANTS_META,
        "cities": CITY_CENTERS,
        "auth_enabled": AUTH_ENABLED,
        "waqi_configured": waqi_configured,
        "is_admin": session.get("is_admin", False)
    })


@app.route("/api/auth/login", methods=["POST"])
def api_auth_login():
    try:
        data = request.get_json(force=True) or {}
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        token = data.get("token", "").strip()

        if (username == ADMIN_USERNAME and password == ADMIN_PASSWORD) or (token == API_ACCESS_TOKEN):
            session["is_authenticated"] = True
            session["is_admin"] = True
            session["username"] = username or "admin"
            return jsonify({
                "success": True,
                "message": "Authentication successful.",
                "is_admin": True,
                "redirect": url_for("index")
            })

        return jsonify({
            "success": False,
            "error": "Invalid username or password. Check .env credentials."
        }), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/auth/logout", methods=["GET", "POST"])
def api_auth_logout():
    session.clear()
    return jsonify({
        "success": True,
        "message": "Logged out successfully.",
        "is_admin": False,
        "redirect": url_for("login")
    })


@app.route("/api/auth/status", methods=["GET"])
def api_auth_status():
    return jsonify({
        "success": True,
        "is_authenticated": session.get("is_authenticated", False),
        "is_admin": session.get("is_admin", False),
        "username": session.get("username", "Guest"),
        "auth_enabled": AUTH_ENABLED
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n* Starting AQI Web Application on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
