import pattern.en as en
import random
import itertools
import re
import json # for storage in the PostgreSQL DB

class SentenceGenerator:
    """
    Generates random sentences. Since SentenceGenerator is
    implemented using a Markov Model, input data must first
    be put in to train the model before being able to generate
    sentences.
    """

    def __init__(self):
        """
        Constructs a new instance of SentenceGenerator with
        an untrained Markov Model.
        """
        self.model = {}

    def _pairwise(self, iterable):
        """
        Returns a list of tuples in the form:
        s -> (s0, s1), (s1, s2)...
        """
        a, b = itertools.tee(iterable)
        next(b, None)
        return itertools.izip(a, b)

    def _is_end_word(self, word):
        """
        Checks to see if the word is a terminal word,
        true if so, false otherwise.
        """
        return bool(re.match("\w+[:.?!]", word))


    def train_model(self, input_data):
        """
        Trains the model with input_data, a simple space seperated
        English sentence(s). If the last sentence or phrase does not
        contain ending punctuation, a "." will be appended to the last
        word contained.
        """
        split_data = input_data.split()

        # Clean the input and make sure that the last element
        # has some form of punctuation, if not, append '.'.
        if split_data and not self._is_end_word(split_data[-1]):
            split_data[-1] += "."

        markov_states = self._pairwise(split_data)

        for init_state, pos_state in markov_states:
            all_pos_states = self.model.get(init_state, [])
            all_pos_states.append(pos_state)
            self.model[init_state] = all_pos_states


    def generate_sentences(self, n = 1, initial_word = None):
        """
        Randomly generates n number of sentences with an initial word.
        By default, n = 1 and the initial word will be random.
        If the initial word is not in the model, an ValueError exception
        will be thrown.
        Returns a list of strings each of which is a sentence.
        """

        all_sentences = []

        # if a word was passed in, use that as the state
        if initial_word:
            # verify that its in the dictionary
            if initial_word not in self.model:
                raise ValueError("\'" + initial_word + "\' was not found")
            cur_state = initial_word
        else:
            cur_state = random.choice(self.model.keys())

        while len(all_sentences) < n:
            cur_sentence = []
            cur_sentence.append(cur_state)

            while not self._is_end_word(cur_state):
                # get all possible states and randomly
                # choose a state to go to
                all_future_states = self.model[cur_state]
                cur_state = random.choice(all_future_states)
                cur_sentence.append(cur_state)

            # finished generating a sentence, generate a new state if not passed one
            cur_state = initial_word if initial_word else random.choice(self.model.keys())

            all_sentences.append(" ".join(cur_sentence))

        return all_sentences

    def get_json_rep(self):
        """
        Returns the JSON representation of the underlying Markov Model.
        """
        return json.dumps(self.model)
