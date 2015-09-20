# -*- coding: utf-8 -*-
from sentence_generator import SentenceGenerator
from scraper import Scraper
from sentence_classifier import SentenceClassifier

import logging

def train_on_data(sentence_gen):
    train_on = raw_input("train on yesterday or today? [y for yesterday, t for today] ")

    if train_on == "y":
        past_funny_train = open("yesterday_train_funny.txt", "a+")
        past_non_funny_train = open("yesterday_train_non_funny.txt", "a+")

        continue_training = True
        while continue_training:
            cur_sentence = unicode(sentence_gen.generate_sentences(1, "I", past_tense=False)[0])
            print cur_sentence + "\n"
            is_funny = raw_input("is this funny? [y/n] press q to quit: ")
            if is_funny == "y":
                past_funny_train.write(cur_sentence + "\n")
            elif is_funny != "q":
                past_non_funny_train.write(cur_sentence + "\n")
            else:
                continue_training = False
                past_funny_train.close()
                past_non_funny_train.close()


def randomly_generate_past_and_future_phrases(sentence_gen, n):
    z = sentence_gen.generate_sentences(n, "I", past_tense=False)
    za = sentence_gen.generate_sentences(n, "to")
    for y in z:
        print "Yesterday, " + sentence_gen.to_past_tense(y)
    for b in za:
        print "Today, I plan " + b

logging.basicConfig(level=logging.DEBUG)
y = SentenceClassifier()
y.train_classifier_from_file("yesterday_train_non_funny.txt", False)
y.train_classifier_from_file("yesterday_train_funny.txt", True)
x = Scraper(logging)
x.gather_reddit_data()
phrases = x.phrases
print "reddit data gathered"
print "the list is now " + str(len(phrases)) + " long "
x.gather_hn_data()
phrases = x.phrases
print "hn data gathered"
print "the list is now " + str(len(phrases)) + " long "
sentence_gen = SentenceGenerator(y)
for phrase in phrases:
    sentence_gen.train_model(phrase)
train_on_data(sentence_gen)
