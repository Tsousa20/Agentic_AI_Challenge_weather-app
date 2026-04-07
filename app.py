from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)

WEATHER_ICONS = {
    113: "☀️", 116: "⛅", 119: "☁️", 122: "☁️",
    143: "🌫️", 176: "🌦️", 179: "🌨️", 182: "🌧️", 185: "🌧️",
    200: "⛈️", 227: "🌨️", 230: "❄️", 248: "🌁", 260: "🌁",
    263: "🌧️", 266: "🌧️", 281: "🌧️", 284: "🌧️",
    293: "🌧️", 296: "🌧️", 299: "🌧️", 302: "🌧️",
    305: "🌧️", 308: "🌧️", 311: "🌧️", 314: "🌧️",
    317: "🌨️", 320: "🌨️", 323: "🌨️", 326: "🌨️",
    329: "❄️", 332: "❄️", 335: "❄️", 338: "❄️",
    350: "🧊", 353: "🌧️", 356: "🌧️", 359: "🌧️",
    362: "🌨️", 365: "🌨️", 368: "🌨️", 371: "❄️",
    374: "🧊", 377: "🧊", 386: "⛈️", 389: "⛈️",
    392: "⛈️", 395: "⛈️",
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/weather")
def weather():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "City name is required", "code": 400}), 400

    url = f"https://wttr.in/{requests.utils.quote(city)}?format=j1"
    headers = {"User-Agent": "Mozilla/5.0 (WeatherApp/1.0)"}

    try:
        resp = requests.get(url, headers=headers, timeout=5)
    except requests.Timeout:
        return jsonify({"error": "Weather service timed out. Try again.", "code": 503}), 503
    except requests.RequestException as e:
        return jsonify({"error": "Could not reach weather service.", "code": 503}), 503

    if resp.status_code != 200:
        return jsonify({"error": "City not found.", "code": 404}), 404

    try:
        data = resp.json()
    except ValueError:
        return jsonify({"error": f"City '{city}' not found.", "code": 404}), 404

    current = data["current_condition"][0]
    area = data["nearest_area"][0]
    weather_code = int(current["weatherCode"])

    payload = {
        "city": area["areaName"][0]["value"],
        "country": area["country"][0]["value"],
        "temp_c": int(current["temp_C"]),
        "temp_f": int(current["temp_F"]),
        "feels_like_c": int(current["FeelsLikeC"]),
        "feels_like_f": int(current["FeelsLikeF"]),
        "description": current["weatherDesc"][0]["value"],
        "humidity": int(current["humidity"]),
        "wind_kmph": int(current["windspeedKmph"]),
        "wind_dir": current["winddir16Point"],
        "visibility_km": int(current["visibility"]),
        "pressure_mb": int(current["pressure"]),
        "uv_index": int(current["uvIndex"]),
        "cloud_cover": int(current["cloudcover"]),
        "icon": WEATHER_ICONS.get(weather_code, "🌡️"),
    }

    return jsonify(payload)


if __name__ == "__main__":
    app.run(debug=True)
