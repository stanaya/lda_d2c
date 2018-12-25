#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""bun2nwords.py

extract prefix.bun.txt file and
output word frequencies file prefix.nwords.csv

format of csv

0, __N__, n_freq
1, [[[Reserved 1]]], 0 for later use
2, [[[Reserved 2]]], 0 ...
3, [[[Reserved 3]]], 0 ...
4, [[[Reserved 4]]], 0 ...
5, firstword, freq
6, 2ndword, freq
...



Usage:
  bun2nwords.py <prefix>
  bun2nwords.py (-h | --help)
  bun2nwords.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import re
import sys
import os
import operator
import csv

RESERVED_WORDS = 4 # from 1 to 4

def calc_bow(text=[]):
    bow = {}
    allwordsfreq = 0
    for idx, words in enumerate(text):
        if idx % 1000 == 999:
            print('processing %d' % (idx+1))
        for w in words[:-1].split(' '):
            bow[w] = bow.get(w,0) + 1
            allwordsfreq += 1
    return bow, allwordsfreq

def retrieve_documents(bun_file='', out_file=''):
    txt = None
    with open(bun_file, 'r') as fp:
        txt = fp.readlines()

    print('loading %s...done.' % bun_file)

    bow, allwordsfreq = calc_bow(text=txt)

    ls = [(k,v) for (k,v) in bow.items()]

    ls.sort(key=lambda x:x[1],reverse=True)

    ls = [('[[[Reserved %d]]]' % n , 0) for n in range(1, RESERVED_WORDS + 1)] + ls
    ls = [('__N__', allwordsfreq)] + ls
    nrows = 0
    with open(out_file, 'w', newline='') as csvfile:
        fwriter = csv.writer(csvfile, delimiter=',')
        for num, tup in enumerate(ls):
            word, freq = tup
            fwriter.writerow([num, word, freq])
            nrows = num
    return nrows

def main(bun_file='', out_file=''):
    num_rows = retrieve_documents(bun_file=bun_file, out_file=out_file)
    print('%d words are processed.' % num_rows)


from docopt import docopt


if __name__ == '__main__':
    arguments = docopt(__doc__, version='bun2nwords 0.1')
    prefix = arguments[r'<prefix>']
    main(bun_file=(prefix + '.bun.txt'),
         out_file=(prefix + '.nwords.csv'))
