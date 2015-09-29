"""
REST API for generating sentences.
"""

import logging

from flask import Flask, jsonify, request
from logging.handlers import RotatingFileHandler
from sentence_generator import SentenceGenerator
from sentence_classifier import SentenceClassifier


app = Flask(__name__)

@app.before_first_request
def scheduler():
    print "TODO: IMPLEMENT SCHEDULER"

@app.route("/sentence")
def generate_sentence():
    classifier = SentenceClassifier(app.logger)
    generate = SentenceGenerator(classifier, app.logger)
    sentence = generate.generate_sentence(initial_word="I")
    app.logger.info("Generated sentence: %s" % sentence)
    return jsonify(sentence=sentence)

@app.route("/sentence", methods=['POST'])
def put_sentence():
    print "TODO: IMPLEMENT PUT SENTENCE"

def setup_logger():
    """
    Sets up the logger to info level as well as setting up the log file.
    """
    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s%(lineno)d} %(message)s")
    handler = RotatingFileHandler("server.log", maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

if __name__ == "__main__":
    setup_logger()
    app.run()
