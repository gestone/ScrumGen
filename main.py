# -*- coding: utf-8 -*-
from sentence_generator import SentenceGenerator

x = SentenceGenerator()
x.train_model("")
print x.get_json_rep()
print x.generate_sentences(10, "PostgreSQL")
