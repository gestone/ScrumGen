import pattern.en as en
import random
import itertools
import re
import json # for storage in the PostgreSQL DB

from itertools import cycle
from nltk import bigrams  # to get tuples from a sentence in the form: (s0, s1), (s1, s2)
from pattern.en import parsetree

class SentenceGenerator:
    """
    Generates random sentences. Since SentenceGenerator is
    implemented using a Markov Model, input data must first
    be put in to train the model before being able to generate
    sentences.
    """

    def __init__(self, classifier):
        """
        Constructs a new instance of SentenceGenerator with
        an untrained Markov Model.
        """
        self.model = {}
        self.classifier = classifier

    def _is_end_word(self, word):
        """
        Checks to see if the word is a terminal word,
        true if so, false otherwise.
        """
        return bool(re.match("\w+[:.?!*\\-]+", word))

    def _is_verb(self, word):
        return parsetree(word)[0].words[0].type == "VB"


    def to_past_tense(self, sentence):
        """
        Converts the given sentence to a given tense. The
        param, sentence is a string that represents a string.
        Returns a string representing the sentence
        in the specified tense.
        """
        punc, sentence = sentence[-1], sentence[0:-1] # to avoid parsing issues with library
        parsed_chunks = parsetree(sentence)[0].words # since there's only 1 sentence


        updated_sentence = [en.conjugate(c.string, "1sgp").strip() if c.type == "VBP" else c.string.strip()
                            for c in parsed_chunks]

        # combine all the stray ' that the parser parses
        final_sentence = []
        next_elem = updated_sentence.pop(0)
        while updated_sentence:
            cur, next_elem = next_elem, updated_sentence.pop(0)
            if "'" in next_elem or "," in next_elem:
                final_sentence.append(cur + next_elem)
                if updated_sentence:
                    next_elem = updated_sentence.pop(0)
            else:
                final_sentence.append(cur)

        final_sentence.append(next_elem)
        return " ".join(final_sentence) + punc

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

        # bigrams returns -> [(s0, s1), (s1, s2)...]
        # where each s_i is a word
        markov_states = bigrams(split_data)

        for init_state, pos_state in markov_states:
            all_pos_states = self.model.get(init_state, [])
            all_pos_states.append(pos_state)
            self.model[init_state] = all_pos_states


    def generate_sentences(self, n = 1, initial_word = None, past_tense = False):
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

            while not self._is_end_word(cur_state) and cur_state in self.model.keys():
                # get all possible states and randomly
                # choose a state to go to
                all_future_states = self.model[cur_state]
                cur_state = random.choice(all_future_states)
                cur_sentence.append(cur_state)

            # finished generating a sentence, generate a new state if not passed one
            cur_state = initial_word if initial_word else random.choice(self.model.keys())
            full_sentence = " ".join(cur_sentence) if not past_tense else self.to_past_tense(" ".join(cur_sentence))

            if self.classifier.classify(full_sentence):
                all_sentences.append(full_sentence)

        return all_sentences


    def get_json_rep(self):
        """
        Returns the JSON representation of the underlying Markov Model.
        """
        return json.dumps(self.model)
