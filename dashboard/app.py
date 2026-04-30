import streamlit as st
from datetime import datetime
import pickle
import pandas as pd
import os, sys
import matplotlib.pyplot as plt
import pydeck as pdk
import requests
import random

# ----------------------------
# ⚙️ CONFIG
# ----------------------------
st.set_page_config(page_title="Smart Traffic AI", layout="centered")

# ----------------------------
# IMPORTS
# ----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.weather_api import get_weather
from src.traffic_api import get_road_density, generate_area_grid, apply_density, get_city_factor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = pickle.load(open(os.path.join(BASE_DIR, '..', 'model.pkl'), 'rb'))
columns = pickle.load(open(os.path.join(BASE_DIR, '..', 'columns.pkl'), 'rb'))

# ----------------------------
# UI
# ----------------------------
st.markdown("<h1 style='text-align:center;'>🚦 Smart Traffic AI System</h1>", unsafe_allow_html=True)
st.markdown("🧠 AI predicts traffic using weather + time + smart density")

# ----------------------------
# AUTO CITY
# ----------------------------
def get_user_city():
    try:
        return requests.get("https://ipinfo.io/json").json().get("city", "Pune")
    except:
        return "Pune"

city = st.text_input("Enter City", get_user_city())

# ----------------------------
# RUN
# ----------------------------
if st.button("Predict Traffic"):

    with st.spinner("Analyzing live data..."):
        temp, rain, clouds, lat, lon = get_weather(city)

    if temp is None:
        st.error("❌ API Error")
        st.stop()

    now = datetime.now()

    # ----------------------------
    # INPUT DATA
    # ----------------------------
    input_data = pd.DataFrame([{
        'temp': temp,
        'rain_1h': rain,
        'clouds_all': clouds,
        'hour': now.hour,
        'day': now.day,
        'month': now.month,
        'weekday': now.weekday(),
        'is_weekend': 1 if now.weekday() >= 5 else 0,
        'rush_hour': 1 if (7 <= now.hour <= 10 or 16 <= now.hour <= 20) else 0,
        'weather_severity': rain + clouds/100
    }])

    input_data = input_data.reindex(columns=columns, fill_value=0)

    # ----------------------------
    # MAIN PREDICTION
    # ----------------------------
    base_pred = model.predict(input_data)[0]
    factor = get_city_factor(city)

    prediction = int(max(500, min(base_pred * factor * random.uniform(0.85, 1.15), 5000)))

    # ----------------------------
    # AREA TRAFFIC
    # ----------------------------
    areas = generate_area_grid(lat, lon)
    base_density = get_road_density(lat, lon)

    area_results = []

    for i, area in enumerate(areas):

        local_density = base_density * (1 + (i - 4) * 0.1)

        pred = apply_density(base_pred, local_density)

        area_results.append({
            "name": area["name"],
            "lat": area["lat"],
            "lon": area["lon"],
            "traffic": pred
        })

    # ----------------------------
    # RESULT
    # ----------------------------
    st.subheader(f"🚦 Traffic in {city}: {prediction}")

    if prediction > 2500:
        st.error("🔴 Heavy Traffic")
    elif prediction > 1200:
        st.warning("🟠 Moderate Traffic")
    else:
        st.success("🟢 Low Traffic")

    st.info("Higher number = more vehicles → more congestion")

    # ----------------------------
    # AREA DISPLAY
    # ----------------------------
    st.subheader("📍 Area-wise Traffic")

    for area in area_results:
        if area["traffic"] > 2500:
            st.error(f'{area["name"]}: 🔴 {area["traffic"]}')
        elif area["traffic"] > 1200:
            st.warning(f'{area["name"]}: 🟠 {area["traffic"]}')
        else:
            st.success(f'{area["name"]}: 🟢 {area["traffic"]}')

    # ----------------------------
    # METRICS
    # ----------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("🌡️ Temp", f"{temp:.1f}°C")
    col2.metric("🌧️ Rain", f"{rain}")
    col3.metric("☁️ Clouds", f"{clouds}%")

    # ----------------------------
    # GRAPH
    # ----------------------------
    st.subheader("📊 Traffic Trend")

    hours = list(range(24))
    preds = []

    for h in hours:
        temp_data = input_data.copy()
        temp_data['hour'] = h
        temp_data['rush_hour'] = 1 if (7 <= h <= 10 or 16 <= h <= 20) else 0
        temp_data = temp_data.reindex(columns=columns, fill_value=0)

        preds.append(model.predict(temp_data)[0] * factor)

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(hours, preds, marker='o')
    ax.grid()

    st.pyplot(fig, width="content")

    # ----------------------------
    # HEATMAP
    # ----------------------------
    st.subheader("🗺️ Traffic Heatmap")
    st.caption("🔴 Red = High traffic | 🟡 Moderate | 🟢 Low")

    heat_df = pd.DataFrame(area_results)

    heat_layer = pdk.Layer(
        "HeatmapLayer",
        data=heat_df,
        get_position='[lon, lat]',
        get_weight="traffic",
        radiusPixels=50,
    )

    deck = pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=11,
        ),
        layers=[heat_layer],
    )

    st.pydeck_chart(deck, width="stretch")

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("""
<div style='text-align:left; font-size:12px; color:gray; margin-top:20px;'>
✨ Crafted with data & intelligence — by Simi Dubey
</div>
""", unsafe_allow_html=True)