#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""json2bun.py

extract JSONed corpus and
output csv file of structured text.

Usage:
  json2bun2.py <csv_file> <nwords> <prefix>
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
import json
import csv


def ret_true(x=0, y=0):
    return True


def AAfilter(x=0, y=0):
    return (x > 2) and (y > 2) and (x <= 75) and (y <= 250)


def retrieve_documents(filename='', prefix='', filter=ret_true):
    nrow = 0
    with open(filename, newline='') as csvfile:
        outfilename = prefix + '.distri.csv'
        with open(outfilename, 'w') as outp:
            fwriter = csv.writer(outp, delimiter=',')
            reader = csv.reader(csvfile)
            x = 0
            y = 0
            for row in reader:
                nrow += 1
                if row[0] == 'H':
                    x = int(row[1])
                elif row[0] == 'T':
                    y = int(row[1])
                    if filter(x, y):
                        fwriter.writerow([x, y])
    return nrow



def lookup_dictionaries(li=[], w2idx={}):
    ishead = False
    istext = False
    if li[0] == 'H':
        ishead = True
    elif li[0] == 'T':
        istext = True

    words = li[3:-1]
    idxwords = [str(w2idx.get(w, 1)) for w in words]
    return ' '.join(idxwords)


def retrieve_documents_with_words(filename='', prefix='', w2idx={}, period=500, filter=AAfilter):
    nrow = 0
    with open(filename, newline='') as csvfile:
        outfilename = prefix + '.idx2.txt'
        with open(outfilename, 'w') as outp:
            # fwriter = csv.writer(outp, delimiter=',')
            reader = csv.reader(csvfile)
            x = 0
            y = 0
            counter = 0
            for row in reader:
                nrow += 1
                if row[0] == 'H':
                    x = int(row[1])
                    h = row
                elif row[0] == 'T':
                    y = int(row[1])
                    t = row
                    if filter(x, y):
                        counter += 1
                        if (counter % period) == (period - 1):
                            hline = lookup_dictionaries(h, w2idx=w2idx)
                            tline = lookup_dictionaries(t, w2idx=w2idx)
                            outp.write(hline + '\n')
                            outp.write(tline + '\n')
    return nrow

def read_w2idx_idx2w(nw_file=''):
    w2idx = {}
    idx2w = {}
    nrows = 0
    with open(nw_file, 'r', newline='') as csvfile:
        freader = csv.reader(csvfile, delimiter=',')
        for tup in freader:
            num, word, _ = tup
            w2idx[word] = num
            idx2w[num] = word
            nrows = num
    return w2idx, idx2w, nrows


def main(csv_file='', nwords='', out_prefix=''):
    w2idx, _, _ = read_w2idx_idx2w(nw_file=nwords)
    num_articles = retrieve_documents_with_words(
        csv_file, out_prefix, w2idx=w2idx, period=500)
    print('%d articles are processed.' % num_articles)

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='bun2twoIdx 0.1')
    main(csv_file=arguments[r'<csv_file>'],
         nwords=arguments[r'<nwords>'],
         out_prefix=arguments[r'<prefix>'])
