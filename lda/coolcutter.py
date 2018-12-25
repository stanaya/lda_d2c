#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""coolcutter.py

load svm (pseudo) file and drop following words:
 * document frequency is larger than 0.95 (document specific stop words).
 * documents frequence's frequency is smaller than 2.

output file is prefix.cool.svm.

Usage:
  coolcutter.py <prefix>
  coolcutter.py (-h | --help)
  coolcutter.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import re
import sys
import os
import operator


class SVMloader:
    def __init__(self):
        self.corpus = []

    def load(self, filename=''):
        fi = open(filename, 'r')
        lines = fi.read().splitlines()
        fi.close()

        self.corpus = self.decode(lines)
        return self.corpus

    def decode(self, lines=[]):
        corpus = []
        for li in lines:
            features = li.split()
            document = {}
            for f in features:
                wid, freq = f.split(':')
                document[int(wid, base=10)] = int(freq, base=10)
            corpus.append(document)

        return corpus


class SVMwriter:
    def __init__(self):
        self.corpus = []

    def write(self, filename='', corpus=[]):
        fi = open(filename, 'w')
        strrep = self.encode(corpus)
        fi.write(strrep)
        fi.close()

    def encode(self, corpus=[]):
        docs = []
        for doc in corpus:
            record = []
            new_record_list = sorted(doc.items(), key=lambda x: x[0])
            for k, v in new_record_list:
                record.append('%d:%d' % (k, v))
            recstr = ' '.join(record)
            docs.append(recstr)

        return '\n'.join(docs)


def calc_df(corpus=[]):
    dfs = {}
    for doc in corpus:
        for k, _ in doc.items():
            dfs[k] = dfs.get(k, 0) + 1
    return dfs


def make_delete_list(corpus=[], dfs={}, max_df=0.95, min_df=2):
    len_documents = len(corpus)
    rdict = {}
    for wid, df in dfs.items():
        if (df / len_documents) > max_df and (wid not in rdict):
            rdict[wid] = 1
        if df <= min_df and (wid not in rdict):
            rdict[wid] = 1
    return rdict


def drop_entries(corpus=[], min_tf=0, n_feature=1000, max_df=0.95, min_df=2):
    print('1. calculated df.')
    dfs = calc_df(corpus=corpus)

    print('2. omit exceed max df and lower df in probability...')
    rdict = make_delete_list(
        corpus=corpus, dfs=dfs, max_df=max_df, min_df=min_df)

    print('3. calculate tf in corpus.')
    bow = {}
    for doc in corpus:
        for k, v in doc.items():
            if k not in rdict:
                bow[k] = bow.get(k, 0) + v

    print('4. sort it')
    word_ranking = sorted(bow.items(), key=operator.itemgetter(1))
    drop_list = word_ranking[n_feature:]
    for k, v in word_ranking[:n_feature]:
        if v < min_tf:
            rdict[k] = 1
    for k, v in drop_list:
        if k not in rdict:
            rdict[k] = 1

    print('5. perform deletion')
    new_corpus = []
    idx = 0
    for doc in corpus:
        doc_dict = {}
        idx += 1
        for k, v in doc.items():
            if k not in rdict:
                doc_dict[k] = v
        new_corpus.append(doc_dict)
    return new_corpus


def main(prefix=''):
    corpus = SVMloader().load(filename=('%s.svm' % prefix))
    corpus = drop_entries(corpus)
    write_file_name = '%s.cool.svm' % prefix
    SVMwriter().write(write_file_name, corpus=corpus)
    print('write %s.' % write_file_name)


from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='coolcutter 0.1')
    main(prefix=arguments[r'<prefix>'])
