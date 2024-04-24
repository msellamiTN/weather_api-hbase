import json
import requests
import happybase
from datetime import datetime
import time
from flask import Flask, jsonify, request

app = Flask(__name__)

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

def ingest_weather_data_to_hbase(connection, table, city_data,api_key):
    for city in city_data:
        lon = city['coord']['lon']
        lat = city['coord']['lat']
        name = city['name']
        city_id = city['id']

        weather_info = get_weather_data(lat, lon, api_key)

        if weather_info:
            temp_min = weather_info['main']['temp_min']
            temp_max = weather_info['main']['temp_max']
            humidity = weather_info['main']['humidity']
            pressure = weather_info['main']['pressure']
            wind_speed = weather_info['wind']['speed']
            current_time = datetime.now()

            data = {
                'city_id': str(city_id),
                'name': name,
                'coordinates': {'lon': lon, 'lat': lat},
                'temp_min': str(temp_min),
                'temp_max': str(temp_max),
                'humidity': str(humidity),
                'pressure': str(pressure),
                'wind_speed': str(wind_speed),
                'insertion_time': str(current_time)
            }

            table.put(
                str(city_id).encode(),
                {
                    b'weather_info:name': data['name'].encode(),
                    b'weather_info:coordinates': json.dumps(data['coordinates']).encode(),
                    b'weather_info:temp_min': data['temp_min'].encode(),
                    b'weather_info:temp_max': data['temp_max'].encode(),
                    b'weather_info:humidity': data['humidity'].encode(),
                    b'weather_info:pressure': data['pressure'].encode(),
                    b'weather_info:wind_speed': data['wind_speed'].encode(),
                    b'weather_info:insertion_time': data['insertion_time'].encode()
                }
            )

            print(f"{name}: Succès dans la collecte de données")
            time.sleep(3)

def setup_hbase_connection(host='152.228.228.55'):

    connection = happybase.Connection(host=host, port=9090, autoconnect=True)
    return connection

def setup_hbase_table(connection, table_name):
    if table_name.encode() not in connection.tables():
        connection.create_table(
            table_name,
            {'weather_info': dict()}
        )
    return connection.table(table_name)

@app.route('/api/weather/ingest', methods=['GET'])
def get_ingest_data():
    country = request.args.get('country', type=str)
    limit = request.args.get('limit', type=int)
    api_key = "4e0f8959dab541379b863bd8868196a6"  # current weather API KEY
    connection = setup_hbase_connection()
    table_name = 'weather_data'
    table = setup_hbase_table(connection, table_name)
    city_data = json.load(open('city.json', encoding='utf-8'))
    weather_data=ingest_weather_data_to_hbase(connection, table, city_data,api_key)
    connection.close()
    return jsonify({"info": f"succes d'ingestion de {limit} données météorologique de {country}"}) if weather_data else jsonify({"error": "Aucune donnée météorologique disponible"})

if __name__ == '__main__':
   
    app.run(debug=True, host='0.0.0.0', port=8081)
