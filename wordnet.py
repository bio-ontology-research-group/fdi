#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys
DATA_ROOT = 'data/wordnet/'


def get_db_words(filename):
    words = set()
    with open(DATA_ROOT + filename, 'r') as f:
        for line in f:
            if line.startswith('  '):
                continue
            line = line.split('|')[0]
            items = line.split(' ')
            for item in items:
                ok = True
                item = item.replace('_', ' ')
                for i in item:
                    if not (i.isalpha() or i == ' '):
                        ok = False
                if ok and item != '':
                    words.add(item.lower())
    with open(DATA_ROOT + filename + '.txt', 'w') as f:
        for word in words:
            f.write(word + '\n')


def main(*args, **kwargs):
    get_db_words('data.adj')
    get_db_words('data.verb')
    get_db_words('data.adv')

if __name__ == '__main__':
    main(*sys.argv)
