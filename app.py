import json
import time
from datetime import datetime
import requests
from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client['weatherdb']

def get_weather_data(lat, lon, api_key):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "units": 'metric', 
        "appid": api_key
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Erreur de connexion:", e)
        return None

def get_data(lat, lon):
    api_key = "74fba207e3c6e53a8e1b95c9457311a8" 
    return get_weather_data(lat, lon, api_key)

def store_weather_data_in_db():
    if 'city' not in db.list_collection_names():
        city_collection = db['city']
        with open('city.json', 'r', encoding='utf-8') as d:
            data = json.load(d)
            for city in data[:5]:  # Import only the first 5 cities
                city_collection.insert_one(city)

    weather_collection = db['weather']
    city_collection = db['city']
    cursor = city_collection.find()

    for document in cursor:
        weather_data = get_data(document['coordinates']['lat'], document['coordinates']['lon'])
        if weather_data:
            weather_record = {
                "city_id": document['_id'],
                "name": document['name'],
                "coordinates": document['coordinates'],
                "temp_min": weather_data['main']['temp_min'],
                "temp_max": weather_data['main']['temp_max'],
                "humidity": weather_data['main']['humidity'],
                "pressure": weather_data['main']['pressure'],
                "wind_speed": weather_data['wind']['speed'],
                "insertion_time": datetime.now()
            }
            weather_collection.insert_one(weather_record)
            print(f"{document['name']} - Succès dans la collecte de données")
            time.sleep(1)

from routes import *

if __name__ == '__main__':
    store_weather_data_in_db()
    app.run(debug=True, host='localhost', port=8080)
