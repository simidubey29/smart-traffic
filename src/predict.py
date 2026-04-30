import pickle
import pandas as pd
import os
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, '..', 'model.pkl')
columns_path = os.path.join(BASE_DIR, '..', 'columns.pkl')

# Load model & columns
model = pickle.load(open(model_path, 'rb'))
columns = pickle.load(open(columns_path, 'rb'))

# Current time features
now = datetime.now()
from weather_api import get_weather

# Get live weather
temp, rain, clouds = get_weather()

input_data = {
    'temp': temp,
    'rain_1h': rain,
    'clouds_all': clouds,
    'hour': now.hour,
    'day': now.day,
    'month': now.month,
    'weekday': now.weekday()
}



# Convert to DataFrame
input_df = pd.DataFrame([input_data])

# 🔥 Match training columns (VERY IMPORTANT)
input_df = input_df.reindex(columns=columns, fill_value=0)

# Predict
prediction = model.predict(input_df)

traffic = int(prediction[0])

print("🚦 Predicted Traffic Volume:", traffic)

# Smart recommendation
if traffic > 4000:
    print("❌ Heavy Traffic – Avoid now")
elif traffic > 2000:
    print("⚠️ Moderate Traffic")
else:
    print("✅ Low Traffic – Best time to travel")