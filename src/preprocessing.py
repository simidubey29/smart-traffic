import pandas as pd
import os

# Get current file directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build correct path
file_path = os.path.join(BASE_DIR, '..', 'data', 'Metro_Interstate_Traffic_Volume.csv')

df = pd.read_csv(file_path)

# Convert datetime
df['date_time'] = pd.to_datetime(df['date_time'])

# Extract features
df['hour'] = df['date_time'].dt.hour
df['day'] = df['date_time'].dt.day
df['month'] = df['date_time'].dt.month
df['weekday'] = df['date_time'].dt.weekday

# Encode weather
df = pd.get_dummies(df, columns=['weather_main'], drop_first=True)

# Drop unused
df = df.drop(['date_time', 'weather_description'], axis=1)

# Save cleaned file
output_path = os.path.join(BASE_DIR, '..', 'data', 'cleaned.csv')
df.to_csv(output_path, index=False)

print("✅ Data Preprocessed Successfully")