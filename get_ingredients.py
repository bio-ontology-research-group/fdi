#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys
from stop_words import get_stop_words

stop_words = get_stop_words('english')
ignored_words = set()
DATA_ROOT = 'data/'

good_words = dict()
bad_words = dict()


def load_ignored_words():

    with open('data/ignored_words.txt', 'r') as f:
        for line in f:
            word = line.strip()
            ignored_words.add(word)
load_ignored_words()


def is_ok_letters(word):
    for c in word:
        if ord(c) < ord('a') or ord(c) > ord('z'):
            return False
    return True


def is_ok(word):
    if not is_ok_letters(word):
        return False
    if len(word) == 1 or word in stop_words:
        return False
    if word in ignored_words:
        return False
    if word.startswith('gkg'):
        return False
    return word.isalpha()


def clean(ing):
    res = ''
    for i in range(len(ing)):
        if ing[i].isalpha() or ing[i] in ' ,-.':
            if ing[i] in ',-.':
                res += ' '
            else:
                res += ing[i]
    return res.strip()


def parse_ingredients(ingreadients):
    ings = ingreadients.split('\n')
    for i in range(len(ings)):
        ings[i] = clean(ings[i])
        words = list()
        for word in ings[i].split():
            if is_ok(word):
                words.append(word)
                if word not in good_words:
                    good_words[word] = 0
                good_words[word] += 1
            else:
                if word not in bad_words:
                    bad_words[word] = 0
                bad_words[word] += 1
        words = list(set(words))
        # if len(words) == 0:
        #     print ings[i]
        ings[i] = ' '.join(words)
        if len(ings[i]) > 254:  # The this is probably some trash
            ings[i] = ''
    return list(set(ings))


def load_data():
    data = list()
    with open(DATA_ROOT + 'recipeitems-latest.json', 'r') as f:
        for line in f:
            doc = json.loads(line.strip())
            data.append((doc['name'].replace('\n',''), parse_ingredients(doc['ingredients'].lower())))
    return data


def main(*args, **kwargs):
    data = load_data()
    ings = list()
    for id, ing in data:
        for ingr in ing:
            ings.append((id, ingr))
    with open(DATA_ROOT + 'recipe_ingredients.txt', 'w') as f:
        for id, ing in ings:
            if ing:
                f.write(id.encode('utf-8') + '\t' + ing.encode('utf-8') + '\n')

    words = list()
    for key, value in good_words.iteritems():
        words.append({'word': key, 'count': value})
    words = sorted(words, key=lambda x: x['count'], reverse=True)

    with open(DATA_ROOT + 'recipe_words.txt', 'w') as f:
        for w in words:
            f.write(w['word'].encode('utf-8') + '\t' + str(w['count']) + '\n')


if __name__ == '__main__':
    main(*sys.argv)
