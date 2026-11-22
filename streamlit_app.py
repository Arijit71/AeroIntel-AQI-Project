import streamlit as st
import pandas as pd
from src.predict import (
    predict_aqi_full_report,
    load_model_artifacts,
    FEATURE_COLUMNS,
    get_aqi_category
)
from src.nearby_sources import get_nearby_sources_for_city, CITY_CENTERS
from src.realtime_api import fetch_live_air_quality

st.set_page_config(
    page_title="AeroIntel | Air Quality & Health Intelligence",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #07090E;
        color: #F1F5F9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .metric-card {
        background: rgba(16, 20, 32, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    div[data-testid="stSidebar"] {
        background-color: #0B0E17;
        border-right: 1px solid rgba(255, 255, 255, 0.07);
    }
    .stSlider > div > div > div > div {
        background-color: #F59E0B !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🍃 AeroIntel Air Quality & Health Intelligence")
st.markdown("Predict the **Air Quality Index (AQI)**, identify chemical threat drivers, analyze nearby emission point sources, and review health advisories.")

model, _, _ = load_model_artifacts()
if model is not None:
    st.success("Trained Random Forest Regressor is operational.")
else:
    st.info("Operating on Indian CPCB National Air Quality Index standards.")

st.sidebar.header("Monitoring Airshed & Presets")
city_list = list(CITY_CENTERS.keys())
selected_city = st.sidebar.selectbox("Select Urban Airshed:", city_list, index=0)

preset_defaults = {
    "PM2.5": 85.0, "PM10": 135.0, "NO": 18.0, "NO2": 38.0, "NOx": 48.0,
    "NH3": 22.0, "CO": 1.4, "SO2": 16.0, "O3": 42.0, "Benzene": 2.8, "Toluene": 5.8
}

if st.sidebar.button("📡 Sync Real-Time Station Data", use_container_width=True):
    with st.spinner(f"Retrieving atmospheric feed for {selected_city}..."):
        coords = CITY_CENTERS[selected_city]
        telemetry = fetch_live_air_quality(lat=coords["lat"], lon=coords["lon"], city_name=selected_city)
        if telemetry and "pollutants" in telemetry:
            p = telemetry["pollutants"]
            preset_defaults["PM2.5"] = float(p.get("pm25", p.get("PM2.5", preset_defaults["PM2.5"])))
            preset_defaults["PM10"] = float(p.get("pm10", p.get("PM10", preset_defaults["PM10"])))
            preset_defaults["NO2"] = float(p.get("no2", p.get("NO2", preset_defaults["NO2"])))
            preset_defaults["NO"] = float(p.get("no", p.get("NO", preset_defaults["NO"])))
            preset_defaults["NOx"] = float(p.get("nox", p.get("NOx", preset_defaults["NOx"])))
            preset_defaults["CO"] = float(p.get("co", p.get("CO", preset_defaults["CO"])))
            preset_defaults["SO2"] = float(p.get("so2", p.get("SO2", preset_defaults["SO2"])))
            preset_defaults["O3"] = float(p.get("o3", p.get("O3", preset_defaults["O3"])))
            preset_defaults["NH3"] = float(p.get("nh3", p.get("NH3", preset_defaults["NH3"])))
            preset_defaults["Benzene"] = float(p.get("benzene", p.get("Benzene", preset_defaults["Benzene"])))
            preset_defaults["Toluene"] = float(p.get("toluene", p.get("Toluene", preset_defaults["Toluene"])))
            st.session_state["synced_defaults"] = preset_defaults
            st.sidebar.success(f"Synced from: {telemetry.get('station_name', 'CPCB Regional Net')}")

if "synced_defaults" in st.session_state:
    preset_defaults = st.session_state["synced_defaults"]

preset_choice = st.sidebar.selectbox(
    "Or apply a standard scenario preset:",
    ["Current / Custom Inputs", "Clean Coastal / Hill Station", "Suburban Living Area", "Typical Urban Daytime", "Heavy Traffic / Industrial", "Severe Winter Smog"]
)

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

col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader(f"Pollutant Concentrations ({selected_city})")
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

report = predict_aqi_full_report(input_values)

with col_right:
    st.subheader("AQI & Source Intelligence")
    aqi_val = report["aqi"]
    cat_color = report["category_color"]
    cat_name = report["category"]
    
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.04); border: 2px solid {cat_color}; border-radius: 16px; padding: 1.5rem; text-align: center; margin-bottom: 1.25rem;">
        <span style="font-size: 0.85rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.08em;">Predicted AQI ({selected_city})</span>
        <h1 style="font-size: 3.5rem; margin: 0.2rem 0; color: {cat_color}; font-weight: 800;">{aqi_val}</h1>
        <div style="background: {cat_color}22; color: {cat_color}; display: inline-block; padding: 0.35rem 1rem; border-radius: 999px; font-weight: 700; font-size: 1rem; border: 1px solid {cat_color}66;">
            {cat_name}
        </div>
        <p style="font-size: 0.85rem; color: #D1D5DB; margin-top: 0.75rem;">{report['summary']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    pol_id = report.get("pollutant_identification", {})
    primary = pol_id.get("primary_driver")
    if primary:
        st.markdown(f"""
        <div style="background: rgba(245, 158, 11, 0.08); border-left: 4px solid {primary['badge_color']}; padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #9CA3AF;">Identified Primary Threat</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #F3F4F6; margin-top: 2px;">
                {primary['name']} ({primary['key']})
            </div>
            <div style="font-size: 0.82rem; color: {primary['badge_color']}; font-weight: 600; margin-top: 2px;">
                {primary['status']} • {primary['concentration']} {primary['unit']} ({primary['exceedance_ratio']}× NAAQS Standard)
            </div>
            <div style="font-size: 0.8rem; color: #D1D5DB; margin-top: 4px;">
                {primary['health_impact']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    src_data = report.get("source_attribution", {})
    if src_data:
        dominant_src = src_data.get("dominant_source", {})
        st.write(f"#### 🏭 Estimated Source Attribution")
        st.caption(f"**Foremost Emission Driver:** {dominant_src.get('name')} ({dominant_src.get('percentage')}%)")

        sources = src_data.get("sources_breakdown", [])
        if sources:
            df_src = pd.DataFrame([{"Source": s["name"], "Contribution (%)": s["percentage"]} for s in sources])
            st.bar_chart(df_src.set_index("Source"), horizontal=True)

        with st.expander("Atmospheric Diagnostic & Targeted Actions", expanded=True):
            st.markdown(src_data.get("diagnostic_summary", ""))
            st.write("**Targeted Mitigation Interventions:**")
            for action in src_data.get("interventions", []):
                st.markdown(f"- {action}")

    with st.expander("Health Risk Guidance"):
        st.write(f"**General Population:** {report['health_advisory']}")
        st.write(f"**Sensitive Demographics:** {report['sensitive_advisory']}")

    if report["sub_indices"]:
        with st.expander("CPCB Pollutant Sub-Index Breakdown"):
            df_sub = pd.DataFrame(list(report["sub_indices"].items()), columns=["Pollutant", "Sub-Index"])
            st.bar_chart(df_sub.set_index("Pollutant"))

st.markdown("---")
st.subheader(f"📍 Nearby Emission Hotspots & Airshed Radar ({selected_city})")

nearby_result = get_nearby_sources_for_city(selected_city, max_radius_km=35.0)
hotspots = nearby_result.get("hotspots", [])
st.info(nearby_result.get("diagnostic_summary", ""))

if hotspots:
    df_map = pd.DataFrame([{
        "lat": h["lat"],
        "lon": h["lon"],
        "Facility": h["name"],
        "Category": h["category"],
        "Distance (km)": h["distance_km"],
        "Plume Alignment": h["wind_alignment"],
        "Pollutants": ", ".join(h.get("key_pollutants", []))
    } for h in hotspots])

    c_map, c_table = st.columns([1, 2])
    with c_map:
        st.write("**Airshed Geographic Radar**")
        st.map(df_map[["lat", "lon"]], zoom=10)

    with c_table:
        st.write("**Ranked Nearby Emission Sources**")
        st.dataframe(
            df_map[["Facility", "Category", "Distance (km)", "Plume Alignment", "Pollutants"]],
            width="stretch",
            hide_index=True
        )
else:
    st.write("No major stationary industrial point sources recorded within 35 km.")
