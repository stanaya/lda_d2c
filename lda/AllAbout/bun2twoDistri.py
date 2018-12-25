#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""json2bun.py

extract JSONed corpus and
output csv file of structured text.

Usage:
  json2bun2.py <csv_file> <prefix>
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


def retrieve_documents_with_words(filename='', prefix='', filter=AAfilter):
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
                    h = row
                elif row[0] == 'T':
                    y = int(row[1])
                    t = row
                    if filter(x, y):
                        fwriter.writerow(h)
                        fwriter.writerow(t)
    return nrow


def main(csv_file='', out_prefix=''):
    num_articles = retrieve_documents_with_words(
        csv_file, out_prefix)
    print('%d articles are processed.' % num_articles)

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='bun2twoDistri 0.1')
    main(csv_file=arguments[r'<csv_file>'],
         out_prefix=arguments[r'<prefix>'])
