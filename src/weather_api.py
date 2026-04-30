import requests
import os

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city):

    if not API_KEY:
        print("❌ API KEY NOT FOUND")
        return None, None, None, None, None

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        res = requests.get(url, timeout=10)

        # 🚨 fallback for big cities (API fail case)
        if res.status_code != 200:
            print("API Error:", res.status_code)
            return 30, 0, 50, 19.07, 72.87   # Mumbai fallback

        data = res.json()

        temp = data["main"]["temp"]
        rain = data.get("rain", {}).get("1h", 0)
        clouds = data["clouds"]["all"]

        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]

        return temp, rain, clouds, lat, lon

    except Exception as e:
        print("Weather API Error:", e)

        # safe fallback
        return 28, 0, 40, 18.52, 73.85   # Pune fallback