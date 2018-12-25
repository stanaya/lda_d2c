#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import codecs
import gzip
import pickle


def usage():
    print('visLDA.py: visualize allocations of LDA.')
    print('But this time, only emits one csv file(columns = topics, rows = word rank).')
    print()
    print(' $ python visLDA.py prefix pickle4.gz words.txt')
    print('   prefix: corpus name (such as model, NIPS).')
    print('   pickle4.gz: emit from lightlda2pickle.py (for example, pickle4.gz)')
    print('   words.txt: word file (for example, NIPS.words)')
    quit()


def read_wz(wz_filename):
    # key: (word_id, topic_id), value: frequency of word_id with topic_id.
    bag_of_words = {}
    max_topic_id = -1
    with open(wz_filename, "r") as wzf:
        entire_file_list = wzf.read().splitlines()
        doc_id = 0
        for lin in entire_file_list:
            splitted = lin.split()
            len_tuple = len(splitted)
            if len_tuple != 2:
                doc_id += 1
                if doc_id % 100 == 0:
                    print('make bag of words: doc id %d' % doc_id)
                continue
            # valid entries
            word_id, topic_id = map(int, splitted)
            freq = bag_of_words.get((word_id, topic_id), 0)
            bag_of_words[(word_id, topic_id)] = freq + 1
            if topic_id > max_topic_id:
                max_topic_id = topic_id
    print('read %d documents. %d topics.' % (doc_id, max_topic_id + 1))
    return bag_of_words, (max_topic_id+1)


def read_zerofile(zero_filename):
    # key: (word_id, topic_id), value: frequency of word_id with topic_id.
    bag_of_words = {}
    max_topic_id = -1
    with open(zero_filename, "r") as zf:
        entire_file_list = zf.read().splitlines()
        doc_id = 0
        for lin in entire_file_list:
            splitted = lin.split()
            doc_id = int(splitted[0])
            len_tuple = len(splitted)
            if doc_id % 100 == 0:
                print('make bag of words: doc id %d' % doc_id)
            for i in range(1, len_tuple):
                word_id, topic_id = map(int, splitted[i].split(':'))

                freq = bag_of_words.get((word_id, topic_id), 0)
                bag_of_words[(word_id, topic_id)] = freq + 1
                if topic_id > max_topic_id:
                    max_topic_id = topic_id
    print('read %d documents. %d topics.' % (doc_id, max_topic_id + 1))
    return bag_of_words, (max_topic_id+1)


def split_by_topic(k=-1, bag_of_words={}):
    splitted_dicts = [{} for x in range(k)]
    for key, v in bag_of_words.items():
        wid, tid = key
        splitted_dicts[tid - 1][(wid, tid, v)] = 0

    ranking_lists = []
    for i in range(k):
        lis = sorted(splitted_dicts[i].keys(),
                     key=lambda x: x[2], reverse=True)
        ranking_lists.append(lis)

    return ranking_lists


def make_csv_matrix(lexicon=[], ranking_lists=[], num_topics=10, rows=-1):
    result = []
    for j in range(rows):
        subarray = ['' for j in range(num_topics)]
        result.append(subarray)

    for i in range(num_topics):
        ranking_each = ranking_lists[i]
        for y, wid_tid_freq in enumerate(ranking_each):
            if y < rows:
                wid, tid, freq = wid_tid_freq
                result[y][i] = '%s(%f)' % (lexicon[wid], freq)
                try:
                    result[y][i].encode('cp932')
                except:
                    result[y][i] = '[活字無し](%d)' % freq

    return result


def give_presentation(csv_filename='words.topics.csv',
                      lexicon={},
                      ranking_lists=[],
                      num_words=None):
    import csv

    with open(csv_filename, 'w', encoding='cp932') as csvfile:
        spamwriter = csv.writer(csvfile, lineterminator='\n')
        len_of_topics = []
        for t in ranking_lists:
            len_of_topics.append(len(t))
        num_topics = len(len_of_topics)
        max_rows = max(len_of_topics)
        rows = num_words
        if num_words is None:
            rows = max_rows
        print('draw %d records.' % rows)
        spamwriter.writerow(['topic%d' % idx for idx in range(num_topics)])
        data = make_csv_matrix(lexicon, ranking_lists, num_topics, rows)
        for r in range(rows):
            spamwriter.writerow(data[r])


def model2bows(model=None):
    pwk = model['P(w|k)']
    pwkman = model['P(w|k)/P(w)']
    return pwk, pwkman, model['topics'], model['nlex']


def main(prefix="NIPS", pickled_file='pickle4.gz', wordsfile=None):
    words = []
    with open(wordsfile, "r", encoding='utf-8') as wfile:
        words = wfile.read().splitlines()

    with gzip.open(pickled_file, "rb") as gf:
        model = pickle.load(gf)
    normal, maniac, topics, _ = model2bows(model=model)
    ranking_lists_normal = split_by_topic(topics, normal)
    ranking_lists_maniac = split_by_topic(topics, maniac)

    give_presentation(prefix + '.topics.normal.csv',
                      lexicon=words,
                      ranking_lists=ranking_lists_normal)

    give_presentation(prefix + '.topics.maniac.csv',
                      lexicon=words,
                      ranking_lists=ranking_lists_maniac)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        usage()

    main(sys.argv[1], sys.argv[2], sys.argv[3])
