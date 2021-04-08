"""
Importing all the packages
"""

import nltk
import numpy as np
import csv
import copy
import math
import util

from nltk import tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet

from operator import itemgetter

"""
Group products list from a csv file and store the grouped data into a new csv. 
Download all the popular packages in nltk, used in the later part of the code
"""

# nltk.download("popular")

"""Open the data set and load the data into the relevant 2D array"""

data_file = open("dataset.csv")
file_reader = csv.reader(data_file)
file_data = list(file_reader)
file_data = file_data[1:]

products = np.array(file_data)
products = copy.deepcopy(products[:, 2])

"""Convert the sentences into tokens while removing any other irrelevant characters"""

tokenized_products = []
special_chars = util.get_ascii_alphabets_list()

for sen in products:
    token_sen = nltk.word_tokenize(sen)
    new_sen_without_special_chars = []

    for w in token_sen:
        without_special_chars = ''.join(
            e for e in w if e.isalnum() and e in special_chars)

        if without_special_chars != "":
            new_sen_without_special_chars.append(without_special_chars)

    tokenized_products.append(new_sen_without_special_chars)

"""Remove Stop words from each sentence"""

filtered_products = util.remove_stop_words(tokenized_products)

"""Create stems of the words in the sentences"""

stemmer = nltk.stem.PorterStemmer()
stemmed_products = []

for sen in filtered_products:
    stemmed_sentence = []

    for w in sen:
        stemmed_sentence.append(stemmer.stem(w))

    stemmed_products.append(stemmed_sentence)

"""All the sentences are now stemmed and in order"""

stemmed_sentences = []

for sen in stemmed_products:
    sen.sort()
    sen = util.remove(sen)
    stemmed_sentences.append(" ".join(sen))

"""Convert the sentences into groups"""

visited = set()
list_not_grouped = True
groups = []
SIMILARITY_THRESHOLD = 0.90

while True:
    new_group = []

    # find the first element for this group
    for sen in stemmed_sentences:
        if sen not in visited:
            visited.add(sen)
            new_group.append(sen)
            break

        if sen == stemmed_sentences[-1]:
            list_not_grouped = False

    if not list_not_grouped:
        break

    for sen in stemmed_sentences:
        if sen not in visited:
            sim = util.calculate_similarity(new_group[0], sen)
            if sim >= SIMILARITY_THRESHOLD:
                visited.add(sen)
                new_group.append(sen)

    groups.append(new_group)

"""write back to the file in grouped form"""

output_file = open("dataset-grouped.csv", "w", newline="")
output_writer = csv.writer(output_file)

for group in groups:
    for entry in group:
        for i in range(len(file_data)):
            if stemmed_sentences[i] == entry:
                new_row = copy.deepcopy(file_data[i])
                new_row.append(stemmed_sentences[i])
                output_writer.writerow(new_row)
                break

    output_writer.writerow([0, 0, 0, 0, 0, 0, 0])

output_file.close()
