# -*- coding: utf-8 -*-
from sentence_generator import SentenceGenerator
from scraper import Scraper
from sentence_classifier import SentenceClassifier

import logging

def train_on_data(sentence_gen, sentence_classifier):
    continue_training = True
    while continue_training:
        cur_sentence = unicode(sentence_gen.generate_sentences(1, initial_word="I")[0])
        print cur_sentence + "\n"
        is_funny = raw_input("is this funny? [y/n] press q to quit: ")
        sentence_classifier.insert_sentence_into_db(cur_sentence, bool(is_funny == "y"))
        if is_funny == "q":
            continue_training = False


def randomly_generate_past_and_future_phrases(sentence_gen, n):
    z = sentence_gen.generate_sentences(n, "I")
    za = sentence_gen.generate_sentences(n, "to")
    for y in z:
        print "Yesterday, " + sentence_gen.to_past_tense(y)
    for b in za:
        print "Today, I plan " + b

logging.basicConfig(level=logging.INFO)

y = SentenceClassifier(logging)
sentence_gen = SentenceGenerator(y, logging)
train_on_data(sentence_gen, y)
# y.train_classifier_from_file("yesterday_train_non_funny.txt", False)
# y.train_classifier_from_file("yesterday_train_funny.txt", True)
# x = Scraper(logging)
# x.gather_reddit_data()
# phrases = x.phrases
# print "reddit data gathered"
# print "the list is now " + str(len(phrases)) + " long "
# x.gather_hn_data()
# phrases = x.phrases
# print "hn data gathered"
# print "the list is now " + str(len(phrases)) + " long "
# x.insert_into_db()
# for phrase in phrases:
#     sentence_gen.train_model(phrase)

