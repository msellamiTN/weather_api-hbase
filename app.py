import requests
import json
import pymongo
from pymongo import MongoClient
from datetime import datetime
import time

client = MongoClient('mongodb', 27017)
db = client['weatherdb']

def get(lat, lon, api_key):
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
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print("Erreur de connexion:", e)
        return None

def get_data(lat, lon):
    api_key = "74fba207e3c6e53a8e1b95c9457311a8" 
    weather_data = get(lat, lon, api_key)
    if weather_data:
         return weather_data
    else:
        print("Impossible de récupérer les prévisions météorologiques")

if 'city' not in db.list_collection_names():
    city_collection = db['city']
    with open('city.json', encoding='utf-8') as d:
        data = json.load(d)
    for city in data:
        lon = city['coord']['lon']
        lat = city['coord']['lat']
        name = city['name']
        data = {
            "name": name,
            "coordinates": {"lon": lon, "lat": lat}
        }
        city_id = city_collection.insert_one(data).inserted_id

if 'weather' not in db.list_collection_names():
    W_collection = db['weather']

W_collection = db['weather']
city_collection = db['city']
cursor = city_collection.find()

for document in cursor:
    name = document['name']
    id = document['_id']
    lon = document['coordinates']['lon']
    lat = document['coordinates']['lat']
    rep = get_data(lat, lon)
    temp_min = rep['main']['temp_min']
    temp_max = rep['main']['temp_max']
    humidity = rep['main']['humidity']
    pressure = rep['main']['pressure']
    wind_speed = rep['wind']['speed']
    current_time = datetime.now()

    data_w = {
        "city_id": id,
        "name": name,
        "coordinates": {"lon": lon, "lat": lat},
        "temp_min": temp_min,
        "temp_max": temp_max,
        "humidity": humidity,
        "pressure": pressure,
        "wind_speed": wind_speed,
        "insertion_time": current_time  
    }

    data_weather = W_collection.insert_one(data_w)

    print(f"{name}Succès dans la collecte de données")
    
  
    time.sleep(3)

client.close()

