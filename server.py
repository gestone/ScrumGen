"""
REST API for generating sentences.
"""

import logging
import psycopg2

from flask import Flask, jsonify, request
from logging.handlers import RotatingFileHandler
from sentence_generator import SentenceGenerator
from sentence_classifier import SentenceClassifier


app = Flask(__name__)

@app.before_first_request
def schedule_tasks():
    """
    Schedules the tasks to hit the Reddit API and scrapes HackerNews
    to put into the db.
    """
    print "TODO: IMPLEMENT SCHEDULER"

@app.route("/sentence")
def generate_sentence():
    """
    Generates a sentence and sends a JSON response in the form:
    {sentence : "foo bar."}.
    """
    classifier = SentenceClassifier(app.logger)
    generate = SentenceGenerator(classifier, app.logger)
    sentence = generate.generate_sentence(initial_word="I")
    app.logger.info("Generated sentence: %s" % sentence)
    return jsonify(sentence=sentence)

@app.route("/sentence", methods=['POST'])
def put_sentence():
    """
    Puts the classified sentence into the database.
    """
    sentence = request.form['sentence']
    was_funny = request.form['wasFunny']
    app.logger.info("Received sentence %s with funny = %s" % (sentence, was_funny))
    response = insert_sentence_into_db(sentence, was_funny)
    return jsonify(response=response)

def insert_sentence_into_db(sentence, funny):
    """
    Inserts a sentence into the database of sentences. The param,
    'sentence' is the sentence to be inserted, 'funny' is whether or not
    the sentence was funny or not.
    """
    conn = psycopg2.connect(database="textclassify", user="justinharjanto")
    cur = conn.cursor()

    app.logger.debug("Attempting to insert %s..." % sentence)
    sentence = sentence.replace("'", "''") # escape quotes
    sql_string = "INSERT INTO funny_sentences (sentence, funny) VALUES ('%s', '%s')" \
            % (sentence, funny)
    try:
        msg = "Successfully inserted %s" % sentence
        cur.execute(sql_string)
        app.logger.debug(msg)
        conn.commit()
    except psycopg2.IntegrityError:
        msg = "The phrase '%s' could not be inserted into the database" % sentence
        app.logger.debug(msg)
        conn.rollback()
    return msg

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
