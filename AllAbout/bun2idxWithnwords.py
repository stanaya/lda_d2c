#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""bun2idxWithnwords.py

extract prefix.bun.txt file and
add index numbers of each words by using prefix.nwords.csv.

Usage:
  bun2idxWithnwords.py <prefix>
  bun2idxWithnwords.py (-h | --help)
  bun2idxWithnwords.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import re
import sys
import os
import operator
import csv

RESERVED_WORDS = 4  # from 1 to 4
UNK = 1


def retrieve_documents(bun_file='', w2idx={}, out_file=''):
    with open(bun_file, 'r') as fp:
        txt = fp.readlines()

    print('loading %s...done.' % bun_file)
    num = 0
    with open(out_file, 'w') as ofile:
        for lnum, lstr in enumerate(txt):
            linearray = []
            for w in lstr[:-1].split(' '):
                idx = w2idx.get(w, UNK)
                linearray.append(idx)
                if lnum % 2 == 0:
                    # original text
                    pass
                else:
                    # summary
                    pass
            ofile.write(' '.join(linearray) + '\n')
            if num % 1000 == 999:
                print('processing %d...' % (num + 1))
            num += 1
    return num


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


def main(bun_file='', nw_file='', out_file=''):
    w2idx, idx2w, numwords = read_w2idx_idx2w(nw_file=nw_file)
    num_rows = retrieve_documents(
        bun_file=bun_file, w2idx=w2idx, out_file=out_file)
    print('%d words are processed.' % num_rows)

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='bun2idxWithnwords 0.1')
    prefix = arguments[r'<prefix>']
    main(bun_file=(prefix + '.bun.txt'),
         nw_file=(prefix + '.nwords.csv'),
         out_file=(prefix + '.idx.txt'))
