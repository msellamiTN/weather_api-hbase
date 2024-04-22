import json
from bson import ObjectId
from bson import json_util  # Importez json_util pour gérer la sérialisation ObjectId``
from flask import Flask, jsonify, request
from datetime import datetime
import time
import requests
import pymongo
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
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print("Erreur de connexion:", e)
        return None

def get_data(lat, lon):
    api_key = "74fba207e3c6e53a8e1b95c9457311a8" 
    weather_data = get_weather_data(lat, lon, api_key)
    if weather_data:
         return weather_data
    else:
        print("Impossible de récupérer les prévisions météorologiques")

def store_weather_data_in_db():
    if 'city' not in db.list_collection_names():
        city_collection = db['city']
        with open('city.json', encoding='utf-8') as d:
            data = json.load(d)
            for index, city in enumerate(data):
                if index >= 5:
                    break  # Sortir de la boucle après avoir lu les 20 premières villes
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

        print(f"{name} - Succès dans la collecte de données")
        
        time.sleep(1)


    
@app.route('/api/weather/all', methods=['GET'])
def get_all_weather():
    weather_data = list(db.weather.find())
    # Convertir les ObjectId en chaînes de caractères JSON
    for data in weather_data:
        data['_id'] = str(data['_id'])
        data['city_id'] = str(data['city_id'])
        # Convertir la date en un format sérialisable
        data['insertion_time'] = data['insertion_time'].strftime('%Y-%m-%d %H:%M:%S')
    if weather_data:
        return jsonify(weather_data)
    else:
        return jsonify({"error": "Aucune donnée météorologique disponible"})
    
@app.route('/api/weather/humidity', methods=['GET'])
def get_weather_by_humidity():
    humidity = request.args.get('humidity')
    
    query = {
        "humidity": {"$gte": int(humidity)}
    }
    weather_data = list(db.weather.find(query))
    
    # Convertir les ObjectId en chaînes de caractères JSON et formater l'heure d'insertion
    for data in weather_data:
        data['_id'] = str(data['_id'])
        data['city_id'] = str(data['city_id'])
        data['insertion_time'] = data['insertion_time'].strftime('%Y-%m-%d %H:%M:%S')
    
    if weather_data:
        return jsonify(weather_data)
    else:
        return jsonify({"error": "Aucune donnée météorologique disponible pour l'humidité spécifiée"})



@app.route('/api/weather', methods=['GET'])
def get_weather_by_temp_range():
    temp_min = request.args.get('temp_min')
    temp_max = request.args.get('temp_max')
    
    query = {
        "temp_min": {"$gte": float(temp_min)},
        "temp_max": {"$lte": float(temp_max)}
    }
    weather_data = list(db.weather.find(query))
    
    # Convertir les ObjectId en chaînes de caractères JSON et formater l'heure d'insertion
    for data in weather_data:
        data['_id'] = str(data['_id'])
        data['city_id'] = str(data['city_id'])
        data['insertion_time'] = data['insertion_time'].strftime('%Y-%m-%d %H:%M:%S')
    
    if weather_data:
        return jsonify(weather_data)
    else:
        return jsonify({"error": "Aucune donnée météorologique disponible pour la plage de température spécifiée"})

if __name__ == '__main__':
    store_weather_data_in_db()
    app.run(debug=True, host='localhost', port=8080)
