"""
Generates random sentences using Markov Models.
"""
import psycopg2
import random
import re
import os

from nltk import bigrams  # to get tuples from a sentence in the form: (s0, s1), (s1, s2)

class SentenceGenerator(object):
    """
    Generates random sentences. Since SentenceGenerator is
    implemented using a Markov Model, input data must first
    be put in to train the model before being able to generate
    sentences.
    """

    def __init__(self, classifier, logger):
        """
        Constructs a new instance of SentenceGenerator with
        an untrained Markov Model.
        """
        self.model = {}
        self.classifier = classifier
        self.logger = logger
        self._train_model()

    @classmethod
    def _is_end_word(cls, word):
        """
        Checks to see if the word is a terminal word,
        true if so, false otherwise.
        """
        return bool(re.match(r"\w+[:.?!*\\-]+", word))


    def train_model(self, input_data):
        """
        Trains the model with input_data, a simple space seperated
        English sentence(s). If the last sentence or phrase does not
        contain ending punctuation, a "." will be appended to the last
        word contained.
        """
        self.logger.debug("Training generator on '%s' " % input_data)

        split_data = input_data.split()

        # Clean the input and make sure that the last element
        # has some form of punctuation, if not, append '.'.
        if split_data and not SentenceGenerator._is_end_word(split_data[-1]):
            split_data[-1] += "."

        # bigrams returns -> [(s0, s1), (s1, s2)...]
        # where each s_i is a word
        markov_states = bigrams(split_data)

        for init_state, pos_state in markov_states:
            all_pos_states = self.model.get(init_state, [])
            all_pos_states.append(pos_state)
            self.model[init_state] = all_pos_states

    def _train_model(self):
        """
        Trains the model with the results back from the Postgres database.
        """
        res = self._query_data()
        for phrase in res:
            self.train_model(phrase[0])

    def generate_sentence(self, initial_word=None):
        """
        Randomly generates a sentence with an initial word. If no initial
        word is specified, a random word will be chosen as the start word.
        """
        if initial_word:
            # verify that its in the dictionary
            if initial_word not in self.model:
                raise ValueError("\'" + initial_word + "\' was not found")
            cur_state = initial_word
        else:
            cur_state = random.choice(self.model.keys())

        # try generating a sentence 10000 times, if not possible, return err msg
        for _ in xrange(10000):
            cur_sentence = []
            cur_sentence.append(cur_state)

            while not self._is_end_word(cur_state) and cur_state in self.model.keys():
                # get all possible states and randomly choose a state to go to
                all_future_states = self.model[cur_state]
                cur_state = random.choice(all_future_states)
                cur_sentence.append(cur_state)

            # finished generating a sentence, generate a new state if not passed one
            cur_state = initial_word if initial_word else random.choice(self.model.keys())
            full_sentence = " ".join(cur_sentence)

            if self.classifier.classify(full_sentence):
                self.logger.debug("Successfully generated a sentence!")
                return full_sentence

        return "Error could not generate sentence."


    def _query_data(self):
        """
        Queries the phrases to be trained on from the PostgresDB.
        """
        self.logger.debug("Querying phrases from the DB...")
        conn = psycopg2.connect(database=os.environ["DATABASE"], user=os.environ["USER"])
        cur = conn.cursor()
        cur.execute("SELECT phrase FROM phrases ORDER BY fetch_date DESC")
        self.logger.debug("Success, returning results")
        return iter(cur.fetchall())
