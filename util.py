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

"""Constants"""


NUMBER_OF_TOP_KEYWORDS = 5


"""# Helper Functions"""


""" Checks whether the review_data is recent or not """


def is_recent(review_data):
    recent_dates = []

    for i in range(2, 61):
        x = str(i) + " seconds ago"
        y = str(i) + " minutes ago"
        z = str(i) + " hours ago"

        recent_dates.append(x)
        recent_dates.append(y)
        recent_dates.append(z)

    recent_dates_2 = [
        "1 second ago",
        "1 min ago",
        "1 hour ago",
        "1 day ago",
        "2 days ago",
        "3 days ago",
        "4 days ago",
        "5 days ago",
        "6 days ago",
        "7 days ago",
    ]

    recent_dates += recent_dates_2

    if review_data in recent_dates:
        return True

    return False


"""
This function recieves a list of words and then returns a list of combinations of the 2 tail keywords
"""


def get_permutations_from_keywords(keywords):
    keyword_pairs = []
    keywords_cubes = []

    # Iteratate over all the tuples
    for i in range(len(keywords)):

        # Iterate from the next word
        for j in range(len(keywords) - i - 1):

            # Create a new word from first and last word
            new_word = keywords[i] + " " + keywords[j + i + 1]
            keyword_pairs.append(new_word)

            # Flip this word also
            new_word = keywords[j + i + 1] + " " + keywords[i]
            keyword_pairs.append(new_word)

    # Iteratate over all the tuples
    for i in range(len(keywords)):

        # Iterate from the next word
        for j in range(len(keywords) - i - 1):

            # Iterate from the next to next word
            for k in range(len(keywords) - i - j - 2):

                # Create new words from first, second and third word

                x = keywords[i]
                y = keywords[i + j + 1]
                z = keywords[i + j + k + 2]

                new_word = x + " " + y + " " + z
                keywords_cubes.append(new_word)

                new_word = x + " " + z + " " + y
                keywords_cubes.append(new_word)

                new_word = y + " " + x + " " + z
                keywords_cubes.append(new_word)

                new_word = y + " " + z + " " + x
                keywords_cubes.append(new_word)

                new_word = z + " " + x + " " + y
                keywords_cubes.append(new_word)

                new_word = z + " " + y + " " + x
                keywords_cubes.append(new_word)

    return keyword_pairs + keywords_cubes


"""This function takes in a long sentence and then returns a list of Top N tuples (word, score) in an ordered fashion."""


def get_keywords_from_article(sentence):

    # get the total number of words in the article
    token_sen = nltk.word_tokenize(sentence)
    total_tokens = len(token_sen)

    # remove stop word from the sentence
    token_sen = util.remove_stop_words_1d(token_sen)

    tf_score = {}
    for each_word in token_sen:
        if each_word in tf_score:
            tf_score[each_word] += 1
        else:
            tf_score[each_word] = 1

    # Dividing by total_word_length for each dictionary element
    tf_score.update((x, y/int(total_tokens)) for x, y in tf_score.items())

    # get top keywords
    tf_score = util.get_top_n(tf_score, NUMBER_OF_TOP_KEYWORDS)

    return tf_score


"""Remove stop words from a list of sentences. Takes a 2d array of words and outputs the same 2d array but without any stop words"""


def remove_stop_words(list_sentences):
    stop_words = set(nltk.corpus.stopwords.words("english"))
    filtered_sentecnces = []

    for sen in list_sentences:
        filtered_sent = []

        for w in sen:
            if w not in stop_words:
                filtered_sent.append(w)

        filtered_sentecnces.append(filtered_sent)

    return filtered_sentecnces


"""Rmove stop words from a 1 dimenson list of words"""


def remove_stop_words_1d(sentence):
    numbers = ["0", "1", "2", "3", "4", "5", "6",
               "7", "8", "9", "-", "&", "_", "|", ","]

    stop_words = set(nltk.corpus.stopwords.words("english"))
    stop_words.add(".")
    stop_words.add("Pack")
    stop_words.add("Of")

    filtered_sent = []

    for w in sentence:
        number_exists = False

        for ch in w:
            if ch in numbers:
                number_exists = True

        if w not in stop_words and not number_exists:
            filtered_sent.append(w)

    return filtered_sent


""" get N important words in the document"""


def get_top_n(dict_elem, n):
    result = sorted(dict_elem.items(), key=itemgetter(1), reverse=True)[:n]
    return result


"""Calculates cosine similarity between two sentences"""


def calculate_similarity(sen1, sen2):
    l1 = []
    l2 = []

    X_set = set(sen1)
    Y_set = set(sen2)

    rvector = X_set.union(Y_set)
    for w in rvector:
        if w in X_set:
            l1.append(1)
        else:
            l1.append(0)
        if w in Y_set:
            l2.append(1)
        else:
            l2.append(0)
    c = 0

    for i in range(len(rvector)):
        c += l1[i]*l2[i]
    cosine = c / float((sum(l1)*sum(l2))**0.5)

    return cosine


"""This function returns a list of characters including: a-z and A-Z and '"""


def get_ascii_alphabets_list():
    special_chars = []
    special_chars.append(chr(39))

    for i in range(65, 91):
        special_chars.append(chr(i))

    for i in range(97, 123):
        special_chars.append(chr(i))

    return special_chars


"""remove duplicate elements from a list"""


def remove(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list


"""
 Simple python program to count
 occurrences of pat in txt.
"""


def count_freq(pat, txt):
    M = len(pat)
    N = len(txt)
    res = 0

    # A loop to slide pat[] one by one
    for i in range(N - M + 1):

        # For current index i, check
        # for pattern match
        j = 0
        while j < M:
            if (txt[i + j] != pat[j]):
                break
            j += 1

        if (j == M):
            res += 1
            j = 0
    return res
