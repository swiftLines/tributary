import json
import redis as redis
# import the flask web framework
from flask import Flask, request, jsonify
from loguru import logger

# constants
HISTORY_LENGTH = 10
DATA_KEY = "engine_temperature"

# create a Flask server, and allow us to interact with it using the app
app = Flask(__name__)


# define an endpoint which accepts POST requests, and is reachable from
# the /record endpoint
@app.route('/record', methods=['POST'])
def record_engine_temperature():
    # extract JSON payload from the request
    payload = request.get_json(force=True)
    logger.info(f"(*) record request --- {json.dumps(payload)} (*)")
    # get the engine temperature from the payload
    engine_temperature = payload.get("engine_temperature")
    logger.info(f"engine temperature to record is: {engine_temperature}")
    # open a connection to the redis database 
    database = redis.Redis(host='redis', port=6379, decode_responses=True)
    # add key and engine temperature to head of list
    database.lpush(DATA_KEY, engine_temperature)
    logger.info(f"stashed engine temperature in redis: {engine_temperature}")
    # while the length of the list stored at key is greater than 
    # history length, remove and return the element from the tail
    # of the list
    while database.llen(DATA_KEY) > HISTORY_LENGTH:
        database.rpop(DATA_KEY)
    # assign the elements of the list stored at key to variable and start at the first element and end with the last element
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"engine temperature list now contains these values: {engine_temperature_values}")

    logger.info(f"record request successful")
    # return a json payload, and a 200 status code to the client
    return {"success": True}, 200


# define and endpoint which accepts POST requests, and is reachable
# from the /collect endpoint
@app.route('/collect', methods=['POST'])
def collect_engine_temperature():
    # open a connection to the redis database 
    database = redis.Redis(host='redis', port=6379, decode_responses=True)
    # assign the elements of the list stored at key to variable and start at the first element and end with the last element
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    # assign the most recent engine temperature reading in the database to a variable
    current_engine_temperature = engine_temperature_values[0]
    logger.info(f"current engine temperature: {current_engine_temperature}")
    # compute and assign the mean engine temperature drived from
    # the database
    average_engine_temperature = sum(engine_temperature_values) / len(engine_temperature_values)
    logger.info(f"average engine temperature: {average_engine_temperature}")
    # return a dictionary containing the engine current and average temperatures
    return{
        "current_engine_temperature": current_engine_temperature,
        "average_engine_temperature": average_engine_temperature
        }
