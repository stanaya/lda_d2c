#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""json2bun.py

extract JSONed corpus and
output csv file of structured text.

Usage:
  json2bun2.py <corpus_file> <prefix>
  json2bun2.py (-h | --help)
  json2bun2.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import re
import sys
import os
import operator
import MeCab
import json
import csv

mt = MeCab.Tagger("mecabrc")


def tagging(str_in):
    res = mt.parseToNode(str_in)
    ret = []
    while res:
        ret.append(res.surface[:])
        res = res.next
    return ' '.join(ret)


def retrieve_documents(filename='', prefix=''):
    js = None
    with open(filename, 'r') as fp:
        js = json.load(fp)

    num = 0
    print('loading %s...done.' % filename)
    outfilename = prefix + '.bun2.csv'
    with open(outfilename, 'w') as outp:
        fwriter = csv.writer(outp, delimiter=',')
        for aid, con in js.items():
            for eda, con2 in con.items():
                articles = con2['articles']
                for ax in articles:
                    H3 = ax['H3']
                    htag = tagging(H3)
                    TEXT = ax['text']
                    concate = ''.join(TEXT)
                    sentence = tagging(concate)
                    num += 1
                    htag_list = htag.split(' ')
                    text_list = sentence.split(' ')
                    h_field = ['H', len(htag_list)] + htag_list
                    t_field = ['T', len(text_list)] + text_list
                    fwriter.writerow(h_field)
                    fwriter.writerow(t_field)
    return num


def main(corpus_file='', out_prefix=''):
    num_articles = retrieve_documents(
        corpus_file, out_prefix)
    print('%d articles are processed.' % num_articles)

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='json2bun2 0.1')
    main(corpus_file=arguments[r'<corpus_file>'],
         out_prefix=arguments[r'<prefix>'])
