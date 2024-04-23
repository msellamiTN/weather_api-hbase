from flask import jsonify, request
from app import app, db
from datetime import datetime, timedelta


############ Helpers ############
def format_weather_data(weather_data):
    """ Formate les données météorologiques en convertissant les types de données et en formatant les dates. """
    for data in weather_data:
        data['_id'] = str(data['_id'])
        data['city_id'] = str(data['city_id'])
        data['insertion_time'] = data['insertion_time'].strftime('%Y-%m-%d %H:%M:%S')
    return weather_data

def parse_date(date_str):
    """ Analyse une chaîne de caractères représentant une date au format 'jour/mois/année'. """
    try:
        day, month, year = map(int, date_str.split('/'))
        return datetime(year, month, day)
    except ValueError:
        return None






############ Routes ############
"""
    GET: Retourne toutes les données météorologiques de la base de données.
    Aucun paramètre n'est requis.

    Réponse:
        - Succès: Liste de toutes les entrées météorologiques avec ID, ID de la ville, et heure d'insertion formatée.
        - Échec: Objet JSON indiquant l'absence de données.
"""
@app.route('/api/weather/all', methods=['GET'])
def get_all_weather():

    weather_data = list(db.weather.find())
    formatted_data = format_weather_data(weather_data)
    return jsonify(formatted_data) if weather_data else jsonify({"error": "Aucune donnée météorologique disponible"})


"""
    GET: Retourne les données météorologiques où l'humidité est supérieure ou égale au paramètre 'humidity'.
    Paramètres:
        - humidity (int): Valeur d'humidité minimum (inclus).

    Réponse:
        - Succès: Liste des données météorologiques correspondantes.
        - Échec: Objet JSON indiquant l'absence de données pour l'humidité spécifiée.
"""
@app.route('/api/weather/humidity', methods=['GET'])
def get_weather_by_humidity():

    humidity = request.args.get('humidity', type=int)
    query = {"humidity": {"$gte": humidity}}
    weather_data = list(db.weather.find(query))

    formatted_data = format_weather_data(weather_data)
    return jsonify(formatted_data) if weather_data else jsonify({"error": "Aucune donnée météorologique disponible pour l'humidité spécifiée"})


"""
    GET: Retourne les données météorologiques où l'humidité se situe entre les valeurs 'hum_min' et 'hum_max'.
    Paramètres:
        - hum_min (float): Température minimale (inclusive).
        - hum_max (float): Température maximale (inclusive).

    Réponse:
        - Succès: Liste des données météorologiques correspondantes.
        - Échec: Objet JSON indiquant l'absence de données pour l'humidité spécifiée.
"""
@app.route('/api/weather/humidityBetween', methods=['GET'])
def get_weather_by_humidity_range():

    hum_min = request.args.get('hum_min', type=float)
    hum_max = request.args.get('hum_max', type=float)

    query = {"humidity": {"$gte": hum_min}, "humidity": {"$lte": hum_max}}
    weather_data = list(db.weather.find(query))

    formatted_data = format_weather_data(weather_data)
    return jsonify(formatted_data) if weather_data else jsonify({"error": "Aucune donnée météorologique disponible pour l'humidité spécifiée"})


"""
    GET: Retourne les données météorologiques dont la température se situe entre les valeurs 'temp_min' et 'temp_max'.
    Paramètres:
        - temp_min (float): Température minimale (inclusive).
        - temp_max (float): Température maximale (inclusive).

    Réponse:
        - Succès: Liste des données météorologiques correspondantes.
        - Échec: Objet JSON indiquant l'absence de données pour la plage de température spécifiée.
"""
@app.route('/api/weather', methods=['GET'])
def get_weather_by_temp_range():

    temp_min = request.args.get('temp_min', type=float)
    temp_max = request.args.get('temp_max', type=float)

    query = {"temp_min": {"$gte": temp_min}, "temp_max": {"$lte": temp_max}}
    weather_data = list(db.weather.find(query))

    formatted_data = format_weather_data(weather_data)
    return jsonify(formatted_data) if weather_data else jsonify({"error": "Aucune donnée météorologique disponible pour la plage de température spécifiée"})


"""
    GET: Retourne les données météorologiques pour une ville spécifique par son nom.
    Paramètres:
        - name (str): Nom de la ville.

    Réponse:
        - Succès: Liste des données météorologiques pour la ville spécifiée.
        - Échec: Objet JSON indiquant l'absence de données pour le nom de ville spécifié.
"""
@app.route('/api/weather/by_name', methods=['GET'])
def get_weather_by_name():
    
    city_name = request.args.get('name', type=str)
    if not city_name:
        return jsonify({"error": "Le nom de la ville doit être spécifié"}), 400

    query = {"name": city_name}
    weather_data = list(db.weather.find(query))
    
    formatted_data = format_weather_data(weather_data)
    
    return jsonify(formatted_data) if weather_data else jsonify({"error": "Aucune donnée météorologique disponible pour la ville spécifiée"})


"""
    GET: Retourne les données météorologiques pour une date spécifique (jour/mois/année).
    Paramètres:
        - date (str): Date au format 'jour/mois/année'.

    Réponse:
        - Succès: Liste des données météorologiques pour la date spécifiée.
        - Échec: Objet JSON indiquant l'absence de données pour la date spécifiée.
"""
@app.route('/api/weather/by_date', methods=['GET'])
def get_weather_by_date():

    date_str = request.args.get('date')
    if not date_str:
        return jsonify({"error": "Veuillez spécifier une date au format 'jour/mois/année'"}), 400

    date = parse_date(date_str)
    if not date:
        return jsonify({"error": "Format de date invalide. Assurez-vous d'utiliser le format 'jour/mois/année'"}), 400

    query = {"insertion_time": {"$gte": date, "$lt": date + timedelta(days=1)}}
    weather_data = list(db.weather.find(query))

    formatted_data = format_weather_data(weather_data)

    return jsonify(formatted_data) if weather_data else jsonify({"error": "Aucune donnée météorologique disponible pour la date spécifiée"})

