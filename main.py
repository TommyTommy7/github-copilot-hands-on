import streamlit as st
import requests
import datetime
import pandas as pd  # 表形式データ表示用

# Open-Meteo APIのエンドポイント
API_URL = "https://api.open-meteo.com/v1/forecast"

# 都市ごとの緯度と経度
LOCATIONS = {
    "大阪": {"lat": 34.6937, "lon": 135.5023},
    "東京": {"lat": 35.6895, "lon": 139.6917},
    "名古屋": {"lat": 35.1814, "lon": 136.9065},
    "福岡": {"lat": 33.5904, "lon": 130.4017},
    "札幌": {"lat": 43.0618, "lon": 141.3545},
    "仙台": {"lat": 38.2682, "lon": 140.8694},
}

# 天気コードのマッピング
WEATHER_MAPPING = {
    0: "晴れ",
    1: "主に晴れ",
    2: "曇りがち",
    3: "曇り",
    45: "霧",
    48: "霧（霜）",
    51: "小雨",
    53: "中程度の雨",
    55: "強い雨",
    61: "小雨",
    63: "中程度の雨",
    65: "強い雨",
    80: "小雨のシャワー",
    81: "中程度のシャワー",
    82: "激しいシャワー",
    # 必要に応じて他のコードを追加
}

def fetch_weather_forecast(lat, lon):
    """Open-Meteo APIを使用して指定された都市の1週間分の天気予報を取得する"""
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
        "timezone": "Asia/Tokyo"
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("天気予報の取得に失敗しました。")
        return None

def get_weather_description(weather_code):
    """天気コードを日本語の天気予報に変換する"""
    return WEATHER_MAPPING.get(weather_code, "不明")

def create_weather_dataframe(dates, max_temps, min_temps, precipitation, weather_codes):
    """天気予報データをデータフレームに変換する"""
    weather_descriptions = [get_weather_description(code) for code in weather_codes]
    return pd.DataFrame({
        "日付": [datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y年%m月%d日") for date in dates],
        "最高気温 (°C)": max_temps,
        "最低気温 (°C)": min_temps,
        "降水量 (mm)": precipitation,
        "天気予報": weather_descriptions
    })

def plot_temperature_chart(dates, max_temps, min_temps):
    """最高気温と最低気温の推移をグラフで表示する"""
    chart_data = pd.DataFrame({
        "最高気温 (°C)": max_temps,
        "最低気温 (°C)": min_temps
    }, index=[datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y年%m月%d日") for date in dates])
    st.line_chart(chart_data)

def main():
    st.title("1週間分の天気予報")
    st.write("Open-Meteo APIを使用して、指定された都市の天気予報を表示します。")

    # 都市を選択
    city = st.selectbox("都市を選択してください", list(LOCATIONS.keys()))
    location = LOCATIONS[city]

    # 天気予報データを取得
    forecast_data = fetch_weather_forecast(location["lat"], location["lon"])

    if forecast_data:
        # 日付ごとの天気予報を取得
        daily = forecast_data.get("daily", {})
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        precipitation = daily.get("precipitation_sum", [])
        weather_codes = daily.get("weathercode", [])

        # データフレームを作成して表示
        st.subheader(f"{city}の1週間の天気予報（表形式）")
        df = create_weather_dataframe(dates, max_temps, min_temps, precipitation, weather_codes)
        st.dataframe(df)

        # グラフを描画
        st.subheader(f"{city}の最高気温と最低気温の推移（グラフ）")
        plot_temperature_chart(dates, max_temps, min_temps)

if __name__ == "__main__":
    main()