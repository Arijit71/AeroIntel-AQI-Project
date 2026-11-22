# AeroIntel — Urban Air Quality & Health Risk Intelligence Platform

AeroIntel is an intelligent air quality monitoring, prediction, and source-attribution platform built for Indian urban airsheds.

Instead of displaying a single generic AQI number for an entire city, AeroIntel provides neighborhood-level air quality intelligence. It evaluates 11 criteria pollutants against official Central Pollution Control Board (CPCB) NAQI standards, tracks real-time wind vectors, maps nearby stationary emission sources (industrial zones, landfills, vehicular corridors), calculates whether plumes are blowing toward you, and predicts health risks for the public and sensitive groups.

---

## Quick Setup Guide

Follow these steps to get the entire system running on your computer.

### Step 1: Set Up Your `.env` File (First & Most Important)

The application relies on an environment file named `.env` in the root folder of the project to store server settings, login credentials, and optional API keys.

1. In the project root folder, find the file named `.env.example`.
2. Make a copy of it and name the new file `.env` (make sure it starts with a dot).
   - On Windows (PowerShell):
     ```powershell
     Copy-Item .env.example .env
     ```
   - On Mac / Linux:
     ```bash
     cp .env.example .env
     ```
3. Open `.env` in any text editor. The defaults work out of the box:

   ```env
   SECRET_KEY=aero-intel-secret-key-prod-9831478201
   PORT=5000
   AUTH_ENABLED=true
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=admin123
   API_ACCESS_TOKEN=aero-intel-token-2026
   WAQI_API_KEY=
   ```

   > Default login is **admin** / **admin123**. `WAQI_API_KEY` is completely optional (the app automatically uses Open-Meteo and regional CPCB baselines if left blank).

---

### Step 2: Install Dependencies

Make sure you have **Python 3.9 or higher** installed.

1. Open your terminal or command prompt in the `AQI_Project` folder.
2. (Recommended) Create and activate a clean virtual environment:
   - **Windows**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Mac / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. Install the required Python packages:
   ```bash
   pip install -r Requirements.txt
   ```

---

### Step 3: Start the Web Dashboard

Run the main web server:

```bash
python app.py
```

You should see output similar to:
```
* Starting AQI Web Application on http://127.0.0.1:5000
* Serving Flask app 'app'
* Running on http://127.0.0.1:5000
```

---

### Step 4: Open in Your Browser & Log In

1. Open your web browser (Chrome, Edge, Firefox, Brave, Safari) and navigate to:
   ```
   http://127.0.0.1:5000
   ```
2. You will be greeted by the **AeroIntel Access Gateway** login screen.
3. Enter the default operator credentials (from your `.env` file):
   - **Username**: `admin`
   - **Password**: `admin123`
4. Click **Authenticate & Enter System**. You are now in the live operational dashboard!

---

## How to Use the Dashboard

Once logged in, everything is interactive and updates in real time:

- **Location Dropdown & GPS**:
  - Select any metropolitan city from the top bar (Mumbai, Delhi NCR, Bengaluru, Kolkata, Chennai, Hyderabad, Ahmedabad, Lucknow).
  - Or click the **GPS** button. The browser will ask for location permission; once allowed, it detects your device coordinates, resolves your exact locality (e.g. *Shrirampur*, *Bandra*, *Noida*), and centers the radar map directly over your position.

- **Sync Station**:
  - Click **Sync Station** to fetch the latest real-time pollutant measurements and live wind data for your selected location.

- **Chemical Telemetry Matrix**:
  - The left grid displays 11 criteria pollutants with live values: `PM2.5`, `PM10`, `NO2`, `NO`, `NOx`, `CO`, `SO2`, `O3`, `NH3`, `Benzene`, and `Toluene`.
  - Move any range slider or type numbers directly into the boxes. The machine learning model recalculates the AQI immediately, and the status switches to an amber **Manual** mode so you can simulate "what-if" environmental scenarios.
  - Click **Sync Station** or pick a city at any time to restore genuine live station data.

- **Air Quality Assessment & CPCB Gauge**:
  - Displays the predicted AQI on the official CPCB 0–500 scale with dynamic color grading (Good, Satisfactory, Moderate, Poor, Very Poor, Severe).
  - Highlights the **Primary Threat Pollutant** and the **Foremost Emission Source**.
  - Provides tailored health guidance for the general public and sensitive groups (children, elderly, respiratory patients).

- **Atmospheric Source Attribution**:
  - Shows estimated percentage contributions by emission source: Vehicular Traffic, Industrial Fuel Combustion, Landfill & Waste Burning, Dust & Construction, and Secondary Atmospheric Reactions.
  - Lists actionable source intervention strategies.

- **Airshed Geographic Radar (Leaflet Map)**:
  - An interactive dark-themed map scanning a 35 km perimeter around you.
  - Drops color-coded pins on verified industrial clusters, thermal power stations, refineries, waste dumping grounds, and traffic corridors.
  - Compares the facility's bearing against the live wind direction to report whether it is currently **Downwind** (blowing toward you), **Crosswind**, or **Upwind**.
  - Click any point source card below the map to zoom in and inspect its telemetry.

- **Enlarge Map (Tactical View)**:
  - Click the expand icon on the top-left of the radar map canvas to pop open a fullscreen tactical radar view with background blur. Press `Esc` or click the minimize button to close.

- **Download Executive Report (PDF / Print)**:
  - Click **Download Executive Report** at the bottom of the Air Quality Assessment card. This produces a clean, high-contrast black-and-white printable executive report with complete pollutant tables, source breakdowns, and health advisories.

---

## Useful Commands & Extra Features

### 1. Run the Automated Test Suite
To verify that all endpoints, DOM IDs, authentication flows, and calculation engines are working properly:
```bash
python -m unittest discover tests
```
All 17 unit and integration tests should pass in under 2 seconds.

### 2. Retrain the Machine Learning Model
If you add new training rows to `data/processed/cleaned_city_day.csv` or want to retrain the Random Forest model from scratch:
```bash
python main.py
```
This runs the full data pipeline: data loading, cleaning, feature engineering, training a 100-tree Random Forest regressor, evaluating metrics (R², RMSE, MAE), generating diagnostic charts, and saving updated `.pkl` model artifacts to the `models/` directory.

### 3. Run the Streamlit Interface (Alternative UI)
AeroIntel also includes an alternative Streamlit dashboard:
```bash
streamlit run streamlit_app.py
```
This opens a clean analytical interface on `http://localhost:8501`.

---

## Project Structure

```
AQI_Project/
├── .env                     # Your active configuration and credentials (not committed to git)
├── .env.example             # Template file showing all configuration options
├── .gitignore               # Ignored files (virtual environment, cache, .env)
├── Requirements.txt         # Python library dependencies
├── README.md                # Project documentation and user guide
├── app.py                   # Main Flask backend application & REST API
├── main.py                  # End-to-end ML training and evaluation script
├── streamlit_app.py         # Streamlit alternative interface
│
├── data/
│   ├── raw/                 # Original air quality datasets
│   └── processed/           # Cleaned and processed dataset (cleaned_city_day.csv)
│
├── models/
│   ├── random_forest_model.pkl   # Trained Random Forest regressor
│   ├── scaler.pkl                # Fitted feature scaler
│   └── imputer.pkl               # Fitted missing-value imputer
│
├── src/
│   ├── data_loader.py            # Loads raw CSV data
│   ├── preprocessing.py          # Data cleaning and missing value handling
│   ├── feature_engineering.py    # Temporal and chemical feature generation
│   ├── model_training.py         # Model training routines
│   ├── evaluation.py             # Evaluation metrics (R2, RMSE, MAE)
│   ├── model_saving.py           # Model artifact serialization
│   ├── predict.py                # Prediction inference & CPCB sub-index engine
│   ├── source_identification.py  # Chemical fingerprinting & source attribution
│   ├── nearby_sources.py         # Point-source database & plume vector analysis
│   ├── realtime_api.py           # Live WAQI & Open-Meteo telemetry fetcher
│   ├── analysis.py               # Statistical and exploratory data analysis
│   └── visualization.py          # Chart generation utilities
│
├── static/
│   ├── js/app.js                 # Frontend interactive logic (Leaflet, sliders, GPS)
│   └── images/                   # Training evaluation and correlation plots
│
├── templates/
│   ├── index.html                # Main AeroIntel operational dashboard
│   └── login.html                # Operator access gateway login page
│
└── tests/
    ├── test_dom_elements.py      # DOM ID and UI structure verification tests
    └── test_new_features.py      # End-to-end API, auth, modal, and geocode tests
```

---

## Frequently Asked Questions

**Q: Do I need a paid API key to use AeroIntel?**  
No. AeroIntel is fully functional out of the box without any paid keys. It automatically pairs open-access weather feeds with verified CPCB regional baselines.

**Q: Why does the dashboard say "Mode: Manual"?**  
Whenever you move a slider or change an input in the Chemical Telemetry Matrix, the system switches to manual simulation mode so you know you are viewing what-if test values rather than live station readings. Clicking **Sync Station** restores live data.

**Q: How do I change my login password?**  
Open your `.env` file, change `ADMIN_PASSWORD=your_new_password`, and restart `python app.py`.

**Q: Can I turn off the login screen during local development?**  
Yes. In `.env`, set `AUTH_ENABLED=false` and restart `python app.py`. Visiting `http://127.0.0.1:5000` will then take you straight to the dashboard.
