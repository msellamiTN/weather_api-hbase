from flask import jsonify, request
from app import app, db

@app.route('/api/weather/all', methods=['GET'])
def get_all_weather():
    weather_data = list(db.weather.find())
    for data in weather_data:
        data['_id'] = str(data['_id'])
        data['city_id'] = str(data['city_id'])
        data['insertion_time'] = data['insertion_time'].strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(weather_data) if weather_data else jsonify({"error": "Aucune donnée météorologique disponible"})

@app.route('/api/weather/humidity', methods=['GET'])
def get_weather_by_humidity():
    humidity = request.args.get('humidity', type=int)
    query = {"humidity": {"$gte": humidity}}
    weather_data = list(db.weather.find(query))
    for data in weather_data:
        data['_id'] = str(data['_id'])
        data['city_id'] = str(data['city_id'])
        data['insertion_time'] = data['insertion_time'].strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(weather_data) if weather_data else jsonify({"error": "Aucune donnée météorologique disponible pour l'humidité spécifiée"})

@app.route('/api/weather', methods=['GET'])
def get_weather_by_temp_range():
    temp_min = request.args.get('temp_min', type=float)
    temp_max = request.args.get('temp_max', type=float)
    query = {"temp_min": {"$gte": temp_min}, "temp_max": {"$lte": temp_max}}
    weather_data = list(db.weather.find(query))
    for data in weather_data:
        data['_id'] = str(data['_id'])
        data['city_id'] = str(data['city_id'])
        data['insertion_time'] = data['insertion_time'].strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(weather_data) if weather_data else jsonify({"error": "Aucune donnée météorologique disponible pour la plage de température spécifiée"})


