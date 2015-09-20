"""
Classifies new sentences as either
funny or not.
"""
import string
import math

from nltk import bigrams
from nltk.corpus import stopwords
from collections import Counter


class SentenceClassifier(object):
    """
    An implementation of a Naive Bayes classifier
    used to classify if sentences are funny are not.
    """

    STOP_WORDS = stopwords.words("english")

    def __init__(self):
        """
        Constructs an untrained Naive Bayes classifier.
        """
        self.vocab = Counter()
        self.funny = Counter()
        self.not_funny = Counter()
        self.num_funny = 0.0
        self.num_not_funny = 0.0

    def classify(self, sentence):
        """
        Classifies a new sentence. Returns true
        if the classifier is deemed to be funny,
        false otherwise. If the classifier has not been
        trained, throws a ValueError.
        """

        if not self.vocab:
            raise ValueError("Classifier has not been trained yet")

        counts = self._clean_and_count_sentence(sentence)

        # Calculate the prior probabilities
        total_sentences = self.num_funny + self.num_not_funny
        p_funny_prior = self.num_funny / total_sentences
        p_non_funny_prior = self.num_not_funny / total_sentences

        # Calculate the log likelihood it is funny given that a word
        # or n-gram has appeared. LL is used to avoid floating point errors
        # with small probabilities.

        ll_prob_funny = math.log(p_funny_prior)
        ll_prob_not_funny = math.log(p_non_funny_prior)

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

        counts = self._clean_and_count_sentence(sentence)

        self.vocab += counts
        if funny:
            self.funny += counts
            self.num_funny += 1.0
        else:
            self.not_funny += counts
            self.num_not_funny += 1.0


    def train_classifier_from_file(self, file_name, funny):
        """
        Trains the classifier from a text file of sentences with each sentence
        deliminated by a new line character. The param, 'funny' represents
        if the sentences contained in the file are classified as funny or not.
        If the file does not exist, an IOError will be thrown.
        """
        with open(file_name) as file_contents:
            content = file_contents.readlines()

        for sentence in content:
            self.train_classifier(sentence, funny)


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
