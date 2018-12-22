#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""preLDAJSON.py

extract JSONed corpus and
and output prefix.svm and prefix.words(words file)


Usage:
  preLDAJSON.py <corpus_file> <prefix>
  preLDAJSON.py (-h | --help)
  preLDAJSON.py --version

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

KANJI_ALPHA_REGEXP = re.compile('[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\uD840-\uD87F\uDC00-\uDFFFぁ-んァ-ヶA-Za-z]+')
mt = MeCab.Tagger("mecabrc")

def pass_through_filter(text=''):
    w_list = text.split(' ')
    return w_list

def kanji_through_filter(text=''):
    w_list = text.split(' ')
    return [w for w in w_list if KANJI_ALPHA_REGEXP.match(w)]
    

def tagging(str_in):
    res = mt.parseToNode(str_in)
    ret = []
    while res:
        ret.append(res.surface[:])
        res = res.next
    return ' '.join(ret)
    

class NoWorkWalker:
    def __init__(self):
        self.value = 0

    def walk(self, file_body=''):
        pass

    def reduce(self, record):
        self.value += 1

    def zero(self, initial_value=0):
        self.value = initial_value


class JBOWWalker(NoWorkWalker):
    def __init__(self, convert_func=kanji_through_filter):
        self.zero(initial_value={})
        self.convf = convert_func
        self.docfreq = {}

    def regist_word(self, word='', doc_id=0):
        freq = self.value.get(word, 0)
        self.value[word] = freq + 1
        docx = self.docfreq.get(doc_id, {})
        doc_word_item = docx.get(word, 0)
        docx[word] = doc_word_item + 1
        self.docfreq[doc_id] = docx

    def walk(self, file_body='', doc_id=0):
        content = self.convf(file_body)
        self.docfreq[doc_id] = {}
        for w in content:
            self.regist_word(w, doc_id)

    def rewalk_doc_dict(self, svm_file='', words=[], docfreq={}, trash={}):
        num_docs = len(list(docfreq.keys()))
        rev_words = {}
        svm_file_lines = []

        for idx, w in enumerate(words):
            rev_words[w] = idx

        for k in docfreq.keys():
            freqdict = docfreq[k]
            keys = freqdict.keys()
            keys2 = [w for w in keys if w not in trash]
            record_list = []
            for w in keys2:
                record_list.append(
                    (rev_words[w], '%d:%d' % (rev_words[w], freqdict[w])))
            new_record_list = sorted(record_list, key=operator.itemgetter(0))
            write_line = ' '.join([x[1] for x in new_record_list])
            svm_file_lines.append(write_line)

        fp = open(svm_file, "w")
        fp.write('\n'.join(svm_file_lines))
        fp.close()

    def reduce(self,
               svm_file='',
               words_file='',
               least_freq_threshold=1,
               most_frequent_words_index=100):
        wordlist = sorted(self.value.items(),
                          key=lambda x: x[1], reverse=True)
        top_words_go_to_file = most_frequent_words_index
        filex = open('%s.stopwords%d.csv' %
                     (words_file, top_words_go_to_file), 'w', encoding='cp932')
        for i in range(top_words_go_to_file):
            word = wordlist[i][0]
            if word == '':
                word = '[半角スペース！]'
            elif word == ',':
                word = '[半角カンマ！]'
            elif word == '"':
                word = '[半角ダブルクォーテーションマーク]'
            else:
                word = wordlist[i][0]
            li = '%s,%d\n' % (word, wordlist[i][1])
            filex.write(li)
        filex.close()
        wcontent = []
        trash = {}
        wth = wordlist[most_frequent_words_index][1]
        i = 0
        for w, freq in wordlist:
            if freq > least_freq_threshold and freq < wth:
                wcontent.append(w)
                i += 1
            else:
                trash[w] = freq
        wbody = '\n'.join(wcontent)
        fp = open(words_file, "w", encoding='utf-8')
        fp.write(wbody)
        fp.close()
        self.rewalk_doc_dict(
            svm_file=svm_file, words=wcontent, docfreq=self.docfreq, trash=trash)


def retrieve_documents(filename='', prefix='', walker=JBOWWalker()):
    js = None
    with open(filename, 'r') as fp:
        js = json.load(fp)
    
    num = 0
    print('loading %s...done.' % filename)

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
                walker.walk(file_body=htag, doc_id='.'.join([aid, eda]))
                walker.walk(file_body=sentence, doc_id='.'.join([aid, eda]))

    walker.reduce(svm_file=prefix+'.svm', words_file=prefix+'.words',
                  least_freq_threshold=1, most_frequent_words_index=100)

    return num


def main(corpus_file='', out_prefix=''):
    num_articles = retrieve_documents(
        corpus_file, out_prefix, walker=JBOWWalker())
    print('%d articles are processed.' % num_articles)


from docopt import docopt


if __name__ == '__main__':
    arguments = docopt(__doc__, version='preJaText8 0.1')
    main(corpus_file=arguments[r'<corpus_file>'],
         out_prefix=arguments[r'<prefix>'])



