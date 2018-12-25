#!/usr/bin/python
# -*- coding: utf-8 -*-
"""preNewsGroups.py

collect NetNews articles from news_groups_dir
and output pseudo_svm_file and prefix.words(words file)


Usage:
  preNewsGroups.py [--pt] <news_groups_dir> <pseudo_svm_file> <prefix>
  preNewsGroups.py (-e | --each) <a_file>
  preNewsGroups.py (-h | --help)
  preNewsGroups.py --version

Options:
  --pt          pass through mode
  -h --help     Show this screen.
  --version     Show version.
  -e --each     process each file (not directory's posessions: not working yet)
"""

import re
import sys
import os
import operator
import nltk
from nltk.tokenize import TweetTokenizer
from nltk.tokenize.nist import NISTTokenizer
from nltk.corpus import stopwords
import codecs

HEADER_REGX = re.compile(
    r'^(Date|From|Message-ID|Newsgroups|Path|Subject|Approved|Archive|Control|Distribution|Expires|Followup-To|Injection-Date|Injection-Info|Organization|References|Summary|Supersedes|User-Agent|Xref|Lines): (.*)$')
# TKNZR = TweetTokenizer()
TKNZR = NISTTokenizer()
EWORDS = stopwords.words('english')
STOP_PATTERN = re.compile((u'|'.join(EWORDS))+ur'?siu')


def regexp_filter(text='', regexp=re.compile('[a-zA-Z]+')):
    clean_string = STOP_PATTERN.sub(u'', unicode(text, 'iso-8859-1'))
    w_list = TKNZR.tokenize(clean_string)
    w_list = [w for w in w_list if regexp.match(w)]
    return w_list

def pre_process_filter(text=''):
    clean_string = STOP_PATTERN.sub(u'', unicode(text, 'iso-8859-1'))
    w_list = TKNZR.tokenize(clean_string)

    return w_list


def pass_through_filter(text=''):
    w_list = TKNZR.tokenize(unicode(text, 'iso-8859-1'))
    return w_list


class NoWorkWalker:
    def __init__(self):
        self.value = 0

    def walk(self, file_body=''):
        pass

    def reduce(self, record):
        self.value += 1

    def zero(self, initial_value=0):
        self.value = initial_value


class BOWWalker(NoWorkWalker):
    def __init__(self, convert_func=pass_through_filter):
        self.zero(initial_value={})
        self.convf = convert_func
        self.docfreq = {}

    def regist_word(self, word=u'', doc_id=0):
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
        num_docs = len(docfreq.keys())
        rev_words = {}
        svm_file_lines = []

        for idx, w in enumerate(words):
            rev_words[w] = idx

        for k in range(num_docs):
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

    def reduce(self, svm_file='', words_file='', freq_threshold=50):
        wordlist = sorted(self.value.items(),
                          key=lambda x: x[1], reverse=True)
        wcontent = []
        trash = {}
        for w, freq in wordlist:
            if freq > freq_threshold:
                wcontent.append(w)
            else:
                trash[w] = freq
        wbody = u'\n'.join(wcontent)
        fp = codecs.open(words_file, "w", encoding='utf-8')
        fp.write(wbody)
        fp.close()
        self.rewalk_doc_dict(
            svm_file=svm_file, words=wcontent, docfreq=self.docfreq, trash=trash)


def get_doc_attribute(file_path):
    fp = open(file_path, "r")
    content = fp.readlines()
    fp.close()

    body = []
    doc_dict_entry = {}

    for li in content:
        m = HEADER_REGX.match(li)
        if m is None:
            body.append(li)
        else:
            field_name = m.group(0)
            attribute = m.group(1)
            doc_dict_entry[field_name] = attribute

    return ''.join(body), doc_dict_entry


def john_sky_walker(path, svm_file, prefix, walker=NoWorkWalker()):
    doc_id = 0
    doc_dict = {}
    for root, dirs, files in os.walk(path):
        for fn, file_ in enumerate(files):
            if file_ == '.DS_Store':
                continue
            file_path = os.path.join(root, file_)
            if fn == 0:
                print(root)
            body, doc_dict[doc_id] = get_doc_attribute(file_path)
            walker.walk(file_body=body, doc_id=doc_id)
            doc_id += 1
    walker.reduce(svm_file=svm_file, words_file=prefix+'.words')
    return doc_id, doc_dict


def main(news_groups_dir='.', svm_file='', out_prefix='', passthrough=False):
    if passthrough is True:
        conv_func = pass_through_filter
    else:
        conv_func = regexp_filter # pre_process_filter

    num_articles, ddict = john_sky_walker(
        news_groups_dir, svm_file, out_prefix, walker=BOWWalker(convert_func=conv_func))


from docopt import docopt


if __name__ == '__main__':
    arguments = docopt(__doc__, version='preNewsGroups 0.1')
    main(news_groups_dir=arguments[r'<news_groups_dir>'],
         svm_file=arguments['<pseudo_svm_file>'], out_prefix=arguments[r'<prefix>'], passthrough=arguments['--pt'])
