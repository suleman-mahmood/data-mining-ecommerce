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
Generate a list of keywords from grouped csv file 
Open the data set and load the data into the relevant 2D array
"""

data_file = open("dataset-grouped.csv")
file_reader = csv.reader(data_file)
file_data = list(file_reader)

# convert it into a numpy array
products = np.array(file_data)

# get the third column from the dataset
products = copy.deepcopy(products[:, 2])

"""Groups the similar products together"""

products_grouped = []
curr_group = []

# Iterate over all the products list
for product in products:

    # end of the group
    if product == "0":

        # append the whole list into the group and clear the list
        products_grouped.append(curr_group)
        curr_group = []
    else:
        curr_group.append(product)

"""Convert Prodcuts group into sentences"""

product_groups_to_sentences = []

for group in products_grouped:
    sen = '. '.join(group)
    product_groups_to_sentences.append(sen)

"""Computes the Keywords for all sentence groups"""

keywords = []

for sentence in product_groups_to_sentences:
    keywords.append(util.get_keywords_from_article(sentence))

"""Extract a list of words from tuples"""

keywords_containing_words = []

for keyword in keywords:
    words_list = []

    for (word, score) in keyword:
        words_list.append(word)

    keywords_containing_words.append(words_list)

"""Computes the permutation of top N words"""

keywords_list_for_each_product = []

for keywords in keywords_containing_words:
    keywords_list_for_each_product.append(
        util.get_permutations_from_keywords(keywords))

"""Calculates score for each keyword and then chooses the top ones from it"""
keyword_score = {}
i = 0

for keyword_pairs_list in keywords_list_for_each_product:

    for keyword_pair in keyword_pairs_list:
        curr_count = util.count_freq(
            keyword_pair, product_groups_to_sentences[i])

        if curr_count == 0:
            continue

        if keyword_pair in keyword_score:
            keyword_score[keyword_pair] += 1
        else:
            keyword_score[keyword_pair] = 1

    i += 1

"""write back to the file with keywords"""

output_file = open("dataset-keywords.csv", "w", newline="")
output_writer = csv.writer(output_file)
i = 0
writing_first_time = True

for row in file_data:
    new_row = row

    if row[0] != "0" and not writing_first_time:
        new_row.append("0")

    if writing_first_time:
        new_row.append(keywords_containing_words[i])
        i += 1
        writing_first_time = False

    if row[0] == "0":
        new_row.append("0")
        writing_first_time = True

    output_writer.writerow(new_row)

output_file.close()

"""write all the keywords into the keywords file"""

output_file = open("keywords.csv", "w", newline="")
output_writer = csv.writer(output_file)

sorted_keywords_score = dict(
    sorted(keyword_score.items(), key=lambda item: item[1]))
new_row = []

for key, value in sorted_keywords_score.items():
    sub_row = []

    sub_row.append(key)
    sub_row.append(value)

    new_row.insert(0, sub_row)

for row in new_row:
    output_writer.writerow(row)

output_file.close()
