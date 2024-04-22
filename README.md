# Meteorological_data_collection

Description:

This work was done as part of a class project to discover the functionality of Mongodb with Docker (Docker compose).

**__Composition of the repository📂:__**

```A total of 5 files```

1. app.py (Script used to collect data from the open weather website)

2. city.json (Json file containing information about the cities whose data we want to collect, name, location, etc.)

3. requirement.txt (file containing the dependencies and their version to be used to create the docker app.py image)

4. dockerfile (file with specifications for creating the docker app.py image)

5. docker-compose.yml (specification file for the docker-compose with a script_python container + a MongoDB container)

**__User guide😊__** 

__1. Clone the repository__

Do not hesitate to clone this repo in order to have access to these resources locally and test the set up.

__2. Put your API Key on the python script__ 

Create your Openweather api key on this site - https://openweathermap.org/api.
You need to register in the data current section to obtain the API key to use with python.

Go to the app.py script, then insert your key in the api-key variable in the get_data function


__3. Create the Docker image of the python script__ 

In your shell, access the current directory of the python script

Create the image from the dockerfile using this command in your shell:

```docker build -t get_data .```

Check that the image has been created using this command:

 ```docker images```

__4. Create the dockercompose__

In your shell, stay in the current directory.

Create the docker compose with the docker-compose.yml command in your shell:

```docker-compose up```


To check that all the commands have worked, access your Mongodb set up database with docker-compose.

You should find 2 collections there:

- city (with all the city data stored)

- weather (with the first collection of meteorological data launched with docker-compose)

__Good to know:__

Data is collected every 15 minutes for all cities.

**__Files description🎼__** 

__Docker-compose.yml:__

This YAML file is a configuration for Docker Compose:

- `version: '3.8'`: This specifies the version of the Docker Compose syntax used in this file.

- `services`: This section defines the Docker services you want to run.

- `mongodb`: A service using the `mongodb/mongodb-community-server:latest` image, which is the official Docker image for MongoDB Community Server. This service will be accessible on port 27017 of the host. It also uses a named volume `mongodb_data` to store MongoDB database data persistently.

- `python_script`: A service that builds an image from a Dockerfile in the current directory (context `.`). The Dockerfile is specified as `Dockerfile`. This service depends on the `mongodb` service to ensure MongoDB is started before running the Python script. It also mounts the `app.py` file into the container and sets an environment variable `MONGO_URI` to instruct the Python application how to connect to MongoDB. Finally, it executes a Python script named `app.py` in a loop every 900 seconds.

- `volumes`: This section defines the Docker volumes used by the services.

- `mongodb_data`: A named volume that will be used to store persistent data for MongoDB.


__Dockerfile:__

Base Image (FROM python:3.9-slim):

It specifies the base image for the Docker container. In this case, it's python:3.9-slim, which provides a lightweight Python environment based on Python 3.9.
Working Directory (WORKDIR /app):

It sets the working directory inside the container to /app. This is where the subsequent commands will be executed.
Copying Source Code (COPY . /app):

It copies all files and directories from the current directory (where the Dockerfile is located) to the /app directory inside the container. This includes the application code, as well as any other files required for the application to run.
Installing Dependencies (RUN pip install -r requirements.txt):

It installs the Python dependencies listed in the requirements.txt file. This file typically contains a list of Python packages required by the application. The pip install -r command reads this file and installs the specified packages into the container.
Command to Run the Application (CMD ["python", "app.py"]):

It specifies the default command to run when the container starts. In this case, it runs the Python script app.py using the python interpreter. This assumes that app.py is the main entry point of the application.

__app.py:__

Importing Libraries:

The script begins by importing necessary libraries:
requests: Used for making HTTP requests to the OpenWeatherMap API.
json: Required for working with JSON data.
pymongo: Utilized for interacting with MongoDB.
datetime: Used to get the current date and time.

MongoDB Connection:

It establishes a connection to the MongoDB server using pymongo.MongoClient. The connection is made to the host mongodb (which is the service name defined in the Docker Compose file) on port 27017.
Function Definitions:

get(lat, lon, api_key): This function fetches weather data from the OpenWeatherMap API for a given latitude, longitude, and API key. It constructs the API request URL, sends a GET request, and returns the JSON response containing weather data.
get_data(lat, lon): This function calls the get function to retrieve weather data for a specific location defined by latitude and longitude. If successful, it returns the weather data; otherwise, it prints an error message.
Checking Collection Existence and Data Insertion:

It checks if the 'city' collection exists in the MongoDB database. If not, it creates the collection and inserts city data from a JSON file named 'city.json'.
Similarly, it checks if the 'weather' collection exists. If not, it creates the collection.

Data Retrieval and Insertion:

It retrieves data from the 'city' collection using a cursor.
For each city document, it fetches weather data using the get_data function and extracts relevant weather information such as temperature, humidity, pressure, and wind speed.

It retrieves the current timestamp using datetime.now() to record the insertion time.
Constructs a dictionary data_w containing the collected weather data along with the city ID, name, coordinates, and insertion time.
Inserts the weather data into the 'weather' collection.

There is a 3 second time sleep to ensure that the api does not exceed 60 calls/minute.

Success Message and Connection Closing:

After data collection is complete, it prints a success message indicating the successful collection of data.


**__This could be a sticking point‼️:__**

- difficulty in understanding subscriptions and the associated endpoint. it's not the one call but the current data!

- The mongo command to enter the mongodb container became the mongosh command after version 6.0.0! Be careful, there is no problem linked to the mongodb container.






