import pandas as pd
from xgboost import XGBRegressor
import pickle
from sklearn.metrics import r2_score

# Load dataset
df = pd.read_csv("data/Metro_Interstate_Traffic_Volume.csv")

df = df.dropna()

# Convert datetime
df['date_time'] = pd.to_datetime(df['date_time'])

# Time features
df['hour'] = df['date_time'].dt.hour
df['day'] = df['date_time'].dt.day
df['month'] = df['date_time'].dt.month
df['weekday'] = df['date_time'].dt.weekday()

# 🚀 Feature Engineering
df['is_weekend'] = df['weekday'].apply(lambda x: 1 if x >= 5 else 0)

df['rush_hour'] = df['hour'].apply(
    lambda x: 1 if (7 <= x <= 10 or 16 <= x <= 20) else 0
)

df['weather_severity'] = df['rain_1h'] + df['clouds_all'] / 100

# Features
X = df[['temp', 'rain_1h', 'clouds_all',
        'hour', 'day', 'month', 'weekday',
        'is_weekend', 'rush_hour', 'weather_severity']]

y = df['traffic_volume']

# Train model
model = XGBRegressor(n_estimators=300, learning_rate=0.05)
model.fit(X, y)

# Evaluate
y_pred = model.predict(X)
print("🎯 Accuracy (R2):", round(r2_score(y, y_pred), 2))

# Save
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(X.columns.tolist(), open("columns.pkl", "wb"))

print("✅ Model trained successfully!")