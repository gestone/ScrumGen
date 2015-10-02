"""
Classifies new sentences as either
funny or not.
"""
import string
import math
import os
import psycopg2

from nltk import bigrams
from nltk.corpus import stopwords
from collections import Counter


class SentenceClassifier(object):
    """
    An implementation of a Naive Bayes classifier
    used to classify if sentences are funny are not.
    """

    STOP_WORDS = stopwords.words("english")

    def __init__(self, logger):
        """
        Constructs an untrained Naive Bayes classifier.
        """
        self.logger = logger
        self.vocab = Counter()
        self.funny = Counter()
        self.not_funny = Counter()
        self.num_funny = 0.0
        self.num_not_funny = 0.0
        self._train_classifier_from_db()

    def classify(self, sentence):
        """
        Classifies a new sentence. Returns true
        if the classifier is deemed to be funny,
        false otherwise. If the classifier has not been
        trained, throws a ValueError.
        """

        if not self.vocab or not self.not_funny or not self.funny:
            self.logger.info("Classifier has not been trained yet")
            return True

        counts = self._clean_and_count_sentence(sentence)

        # Calculate the prior probabilities
        total_sentences = self.num_funny + self.num_not_funny
        p_funny_prior = self.num_funny / total_sentences
        p_non_funny_prior = self.num_not_funny / total_sentences

        # Calculate the log likelihood it is funny given that a word
        # or n-gram has appeared. LL is used to avoid floating point errors
        # with small probabilities.

        ll_prob_funny = math.log(p_funny_prior)
        ll_prob_not_funny = math.log(p_non_funny_prior) if p_non_funny_prior == 0 else 0

        sum_funny_values = float(sum(self.funny.values()))
        sum_non_funny_values = float(sum(self.not_funny.values()))
        sum_both_values = sum_funny_values + sum_non_funny_values

        for feature, count in counts.iteritems():
            if feature in self.vocab: # word or n-gram needs to be in the union of the vocab
                p_w_given_funny = self.funny.get(feature, 0.0) / sum_funny_values
                p_w_given_not_funny = self.not_funny.get(feature, 0.0) / sum_non_funny_values

                # factor in the prob word appearing. cannot ignore this in the denominator
                # because this probability is dependent on the feature
                prob_word_appearing = self.vocab[feature] / sum_both_values

                if p_w_given_funny > 0:
                    ll_prob_funny += math.log(count * p_w_given_funny / prob_word_appearing)
                if p_w_given_not_funny > 0:
                    ll_prob_not_funny += math.log(count * p_w_given_not_funny / prob_word_appearing)


        return ll_prob_funny > ll_prob_not_funny


    def train_classifier(self, sentence, funny):
        """
        Trains the classifier. The sentence
        param is a string representing an English sentence and
        the funny param is a boolean that indicates whether or not
        the sentence was funny or not.
        """

        self.logger.debug("Training classifier on sentence, '%s'" % sentence)
        counts = self._clean_and_count_sentence(sentence)

        self.vocab += counts
        if funny:
            self.funny += counts
            self.num_funny += 1.0
        else:
            self.not_funny += counts
            self.num_not_funny += 1.0


    def _train_classifier_from_db(self):
        """
        Trains the classifier from a database of sentences with each sentence
        deliminated by a new line character. The param, 'funny' represents
        if the sentences contained in the file are classified as funny or not.
        """
        self.logger.debug("Querying sentences from the DB...")
        conn = psycopg2.connect(database=os.environ["DATABASE"], user=os.environ["USER"])
        cur = conn.cursor()
        cur.execute("SELECT sentence, funny FROM funny_sentences")
        self.logger.debug("Successfully retrieved sentences from the DB")

        res = cur.fetchall()
        for sentence, funny in res:
            self.train_classifier(sentence, funny)


    def insert_sentence_into_db(self, sentence, funny):
        """
        Inserts a sentence into the database of sentences. The param,
        'sentence' is the sentence to be inserted, 'funny' is whether or not
        the sentence was funny or not.
        """
        conn = psycopg2.connect(database=os.environ["DATABASE"], user=os.environ["USER"])
        cur = conn.cursor()

        self.logger.debug("Attempting to insert %s..." % sentence)
        sentence = sentence.replace("'", "''") # escape quotes
        sql_string = "INSERT INTO funny_sentences (sentence, funny) VALUES ('%s', '%s')" \
                      % (sentence, funny)
        try:
            cur.execute(sql_string)
            self.logger.debug("Successfully inserted %s" % sentence)
            conn.commit()
        except psycopg2.IntegrityError:
            self.logger.warn("The phrase '%s' could not be inserted into the database" % sentence)
            conn.rollback()

    def _clean_and_count_sentence(self, sentence):
        """
        Cleans the sentence by removing stop words, punctuation, and
        converting to lowercase to ignore case. Then counts all the
        words along with their bigrams counts.
        Returns a counter with both the words and bigram counts included.
        """
        try:
            sentence = sentence.translate(string.maketrans("", ""), string.punctuation).lower()
        except TypeError:
            sentence = sentence.translate(string.punctuation).lower()
        sentence = " ".join([word for word in sentence.split() if word not in self.STOP_WORDS])

        # Count each of the words and their bigrams and add their counts
        word_counts = Counter(sentence.split())
        bigram_counts = Counter(bigrams(sentence.split()))
        return word_counts + bigram_counts
