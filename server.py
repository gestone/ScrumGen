"""
REST API for generating sentences.
"""

from flask import Flask
from flask import json
from flask import jsonify

APP = Flask(__name__)

@APP.route("/")
def hello():
    return jsonify(response="hello world!")

if __name__ == "__main__":
    APP.run()
