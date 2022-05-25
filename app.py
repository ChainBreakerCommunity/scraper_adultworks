import os
from flask import Flask, jsonify, request, make_response
from flask.helpers import send_from_directory
from flask_cors import CORS
import logging
import json 

class Environment:
    def __init__(self, filepath):
        with open(filepath) as json_file: 
            self.data = json.load(json_file)
        
    def get(self, key):
        return self.data[key]

# Instantiate app environemnt.
#environ = Environment("config.json")

# Configure logging.
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Ini app.
app = Flask(__name__)

# Cors.
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Main page.
@app.route('/')
def root():
    """
    Return the frontend of the application.
    """
    return send_from_directory("./static", 'index.html')

@app.route('/api/execute_scraper', methods = ["GET"])
def execute_scraper():
    os.system("python ./app/bot.py")
    return jsonify({"message": "bot executed"})

if __name__ == '__main__':
    print("PORT: ", 9100)
    app.run(port = 9100, debug=True)