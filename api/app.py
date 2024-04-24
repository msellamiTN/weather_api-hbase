import json
import logging
import time
from datetime import datetime, timedelta
import requests
from flask import Flask, jsonify, request
import happybase

app = Flask(__name__)

# Establish connection to HBase
connection = happybase.Connection('152.228.228.55', port=9090, timeout=None, autoconnect=True)  # Adjust the host if needed
table_name = 'weather_data'
table = connection.table(table_name)
for key, row in table.scan():
    app.logger.info("\t{}: {}".format(key, row))


############ Helpers ############

def format_weather_data(weather_data):
    """ Formats weather data by converting data types and formatting dates. """
    formatted_data = []
    for key, data in weather_data:
        formatted_data.append({
            '_id': key.decode(),
            'city_id': data[b'weather_info:city_id'].decode(),
            'name': data[b'weather_info:name'].decode(),
            'coordinates': json.loads(data[b'weather_info:coordinates'].decode()),
            'temp_min': float(data[b'weather_info:temp_min'].decode()),
            'temp_max': float(data[b'weather_info:temp_max'].decode()),
            'humidity': int(data[b'weather_info:humidity'].decode()),
            'pressure': int(data[b'weather_info:pressure'].decode()),
            'wind_speed': float(data[b'weather_info:wind_speed'].decode()),
            'insertion_time': data[b'weather_info:insertion_time'].decode()
        })
    return formatted_data

############ Routes ############

@app.route('/api/weather/all', methods=['GET'])
def get_all_weather():
    """Returns all weather data."""
    try:
        weather_data = table.scan()
        formatted_data = format_weather_data(weather_data)
        return jsonify(formatted_data) if formatted_data else jsonify({"error": "No weather data available"})
    except Exception as e:
        app.logger.error(f"Error retrieving weather data: {e}")
        return jsonify({"error": "An error occurred while retrieving weather data"}), 500


@app.route('/api/weather/humidity', methods=['GET'])
def get_weather_by_humidity():
    """Returns weather data where humidity is greater than or equal to the specified value."""
    humidity = request.args.get('humidity', type=int)
    if humidity is None:
        return jsonify({"error": "Humidity value must be specified"}), 400

    filtered_data = []
    for key, data in table.scan():
        if int(data[b'weather_info:humidity']) >= humidity:
            filtered_data.append(data)

    formatted_data = format_weather_data(filtered_data)
    return jsonify(formatted_data) if formatted_data else jsonify({"error": "No weather data available for the specified humidity"})

@app.route('/api/weather/humidityBetween', methods=['GET'])
def get_weather_by_humidity_range():
    """Returns weather data where humidity falls within the specified range."""
    hum_min = request.args.get('hum_min', type=int)
    hum_max = request.args.get('hum_max', type=int)
    if hum_min is None or hum_max is None:
        return jsonify({"error": "Minimum and maximum humidity values must be specified"}), 400

    filtered_data = []
    for key, data in table.scan():
        humidity = int(data[b'weather_info:humidity'])
        if hum_min <= humidity <= hum_max:
            filtered_data.append(data)

    formatted_data = format_weather_data(filtered_data)
    return jsonify(formatted_data) if formatted_data else jsonify({"error": "No weather data available for the specified humidity range"})

@app.route('/api/weather', methods=['GET'])
def get_weather_by_temp_range():
    """Returns weather data where temperature falls within the specified range."""
    temp_min = request.args.get('temp_min', type=float)
    temp_max = request.args.get('temp_max', type=float)
    if temp_min is None or temp_max is None:
        return jsonify({"error": "Minimum and maximum temperature values must be specified"}), 400

    filtered_data = []
    for key, data in table.scan():
        temp = float(data[b'weather_info:temp_min'])
        if temp_min <= temp <= temp_max:
            filtered_data.append(data)

    formatted_data = format_weather_data(filtered_data)
    return jsonify(formatted_data) if formatted_data else jsonify({"error": "No weather data available for the specified temperature range"})

@app.route('/api/weather/by_name', methods=['GET'])
def get_weather_by_name():
    """Returns weather data for a specific city by name."""
    city_name = request.args.get('name', type=str)
    if not city_name:
        return jsonify({"error": "City name must be specified"}), 400

    filtered_data = []
    for key, data in table.scan():
        if data[b'weather_info:name'].decode('utf-8') == city_name:
            filtered_data.append(data)

    formatted_data = format_weather_data(filtered_data)
    return jsonify(formatted_data) if formatted_data else jsonify({"error": "No weather data available for the specified city name"})

@app.route('/api/weather/by_date', methods=['GET'])
def get_weather_by_date():
    """Returns weather data for a specific date."""
    date_str = request.args.get('date', type=str)
    if not date_str:
        return jsonify({"error": "Date must be specified"}), 400

    date = parse_date(date_str)
    if not date:
        return jsonify({"error": "Invalid date format. Please use 'day/month/year'"}), 400

    next_day = date + timedelta(days=1)

    filtered_data = []
    for key, data in table.scan(row_start=str(date), row_stop=str(next_day)):
        filtered_data.append(data)

    formatted_data = format_weather_data(filtered_data)
    return jsonify(formatted_data) if formatted_data else jsonify({"error": "No weather data available for the specified date"})

if __name__ == '__main__':
    # Establish connection to HBase
    
    app.run(debug=True, host='0.0.0.0', port=8082)
 
