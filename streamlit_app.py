"""
AeroIntel - Streamlit Companion Dashboard
A pure Python interactive interface for exploring AQI predictions,
pollutant distributions, and health advisories.
"""

import streamlit as st
import pandas as pd
from src.predict import (
    predict_aqi_full_report,
    load_model_artifacts,
    FEATURE_COLUMNS,
    get_aqi_category
)

st.set_page_config(
    page_title="AeroIntel | Air Quality & Health Intelligence",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main {
        background-color: #0A0E17;
    }
    .metric-card {
        background: #111726;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .badge-status {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🍃 AeroIntel Air Quality & Health Intelligence")
st.markdown("Predict the **Air Quality Index (AQI)** and get real-time health risk advisories based on atmospheric pollutant concentrations.")

# Check Model Status
model, _, _ = load_model_artifacts()
if model is not None:
    st.success("Trained Random Forest Regressor is loaded and operational.")
else:
    st.info("Operating on Indian CPCB National Air Quality Index standards.")

# Sidebar Presets
st.sidebar.header("Scenario Presets")
preset_choice = st.sidebar.selectbox(
    "Select a pre-configured scenario:",
    ["Custom Inputs", "Clean Coastal / Hill Station", "Suburban Living Area", "Typical Urban Daytime", "Heavy Traffic / Industrial", "Severe Winter Smog"]
)

preset_defaults = {
    "PM2.5": 85.0, "PM10": 135.0, "NO": 18.0, "NO2": 38.0, "NOx": 48.0,
    "NH3": 22.0, "CO": 1.4, "SO2": 16.0, "O3": 42.0, "Benzene": 2.8, "Toluene": 5.8
}

if preset_choice == "Clean Coastal / Hill Station":
    preset_defaults = {"PM2.5": 18.0, "PM10": 34.0, "NO": 4.5, "NO2": 12.0, "NOx": 14.5, "NH3": 6.2, "CO": 0.45, "SO2": 6.0, "O3": 22.0, "Benzene": 0.5, "Toluene": 1.2}
elif preset_choice == "Suburban Living Area":
    preset_defaults = {"PM2.5": 45.0, "PM10": 78.0, "NO": 10.0, "NO2": 24.0, "NOx": 30.0, "NH3": 14.0, "CO": 0.8, "SO2": 11.0, "O3": 30.0, "Benzene": 1.5, "Toluene": 3.0}
elif preset_choice == "Typical Urban Daytime":
    preset_defaults = {"PM2.5": 85.0, "PM10": 135.0, "NO": 18.0, "NO2": 38.0, "NOx": 48.0, "NH3": 22.0, "CO": 1.4, "SO2": 16.0, "O3": 42.0, "Benzene": 2.8, "Toluene": 5.8}
elif preset_choice == "Heavy Traffic / Industrial":
    preset_defaults = {"PM2.5": 145.0, "PM10": 230.0, "NO": 36.0, "NO2": 68.0, "NOx": 92.0, "NH3": 38.0, "CO": 2.4, "SO2": 26.0, "O3": 55.0, "Benzene": 5.2, "Toluene": 10.5}
elif preset_choice == "Severe Winter Smog":
    preset_defaults = {"PM2.5": 310.0, "PM10": 460.0, "NO": 65.0, "NO2": 115.0, "NOx": 170.0, "NH3": 68.0, "CO": 4.8, "SO2": 42.0, "O3": 72.0, "Benzene": 8.8, "Toluene": 18.0}

# Main Layout
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("Pollutant Concentrations")
    
    tab1, tab2, tab3 = st.tabs(["Particulate Matter", "Gases & Combustion", "Secondary & VOCs"])
    
    input_values = {}
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            input_values["PM2.5"] = st.slider("PM2.5 (µg/m³)", 0.0, 500.0, float(preset_defaults["PM2.5"]), 0.5)
        with c2:
            input_values["PM10"] = st.slider("PM10 (µg/m³)", 0.0, 600.0, float(preset_defaults["PM10"]), 1.0)
            
    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            input_values["NO2"] = st.slider("NO2 (µg/m³)", 0.0, 400.0, float(preset_defaults["NO2"]), 0.5)
            input_values["NO"] = st.slider("NO (µg/m³)", 0.0, 250.0, float(preset_defaults["NO"]), 0.5)
            input_values["NOx"] = st.slider("NOx (µg/m³)", 0.0, 500.0, float(preset_defaults["NOx"]), 1.0)
        with c2:
            input_values["CO"] = st.slider("CO (mg/m³)", 0.0, 35.0, float(preset_defaults["CO"]), 0.1)
            input_values["SO2"] = st.slider("SO2 (µg/m³)", 0.0, 300.0, float(preset_defaults["SO2"]), 0.5)

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            input_values["O3"] = st.slider("O3 (µg/m³)", 0.0, 300.0, float(preset_defaults["O3"]), 0.5)
            input_values["NH3"] = st.slider("NH3 (µg/m³)", 0.0, 500.0, float(preset_defaults["NH3"]), 1.0)
        with c2:
            input_values["Benzene"] = st.slider("Benzene (µg/m³)", 0.0, 50.0, float(preset_defaults["Benzene"]), 0.1)
            input_values["Toluene"] = st.slider("Toluene (µg/m³)", 0.0, 100.0, float(preset_defaults["Toluene"]), 0.1)

# Generate Prediction Report
report = predict_aqi_full_report(input_values)

with col_right:
    st.subheader("AQI & Health Assessment")
    
    # AQI Metric Box
    aqi_val = report["aqi"]
    cat_color = report["category_color"]
    cat_name = report["category"]
    
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.04); border: 2px solid {cat_color}; border-radius: 16px; padding: 1.5rem; text-align: center; margin-bottom: 1.25rem;">
        <span style="font-size: 0.85rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.08em;">Predicted AQI</span>
        <h1 style="font-size: 3.5rem; margin: 0.2rem 0; color: {cat_color}; font-weight: 800;">{aqi_val}</h1>
        <div style="background: {cat_color}22; color: {cat_color}; display: inline-block; padding: 0.35rem 1rem; border-radius: 999px; font-weight: 700; font-size: 1rem; border: 1px solid {cat_color}66;">
            {cat_name}
        </div>
        <p style="font-size: 0.85rem; color: #D1D5DB; margin-top: 0.75rem;">{report['summary']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dominant Pollutant Callout
    st.info(f"**Primary Driver:** {report['dominant_pollutant']} is responsible for the highest sub-index in this scenario.")
    
    # Advisories
    with st.expander("General Public Health Advisory", expanded=True):
        st.write(report["health_advisory"])
        
    with st.expander("Sensitive Groups Advisory", expanded=True):
        st.write(report["sensitive_advisory"])

    # Sub-indices table
    if report["sub_indices"]:
        st.write("#### Pollutant Sub-Index Breakdown")
        df_sub = pd.DataFrame(list(report["sub_indices"].items()), columns=["Pollutant", "Sub-Index"])
        st.bar_chart(df_sub.set_index("Pollutant"))
