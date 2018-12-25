#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""generateCSVofKIJI.py

scan All About CSV of HTML files and emits single JSON file.

Usage:
  generateCSVofKIJI.py <corpus_dir> <kiji_dir> <csv_file>
  generateCSVofKIJI.py (-h | --help)
  generateCSVofKIJI.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import re
import sys
import os
import operator
import csv
# import html2text
import json
import lxml
from bs4 import BeautifulSoup
from pprint import pprint

HEADER = """<html>
<head></head><body>
"""

FOOTER = """</body></html>
"""


def get_articles(soup=None, mustshow=False):
    ret = {}
    articles = []
    ret['articles'] = articles
    tmpdict = {}
    isfirst = True
    ishead = False
    descendants = soup.descendants
    for node in descendants:
        name = getattr(node, "name", None)
        if name is not None:
            if name == 'a' or name == 'img':
                pass
                # print(node)
            elif name.startswith('h3'):
                ishead = True
            elif name == 'font':
                pass
            elif name == 'b':
                ishead = True
            elif name != 'br':
                pass
                # print('tag=' + name)
        elif not node.isspace():  # leaf node, don't print spaces
            if mustshow:
                print('HEADINGS: ' + node)
            if isfirst is False:
                # emit
                ret['articles'].append(tmpdict)
            if ishead:
                if isfirst:
                    # normal case
                    isfirst = False
                tmpdict = {'H3': str(node), 'text': []}
                ishead = False
            else:
                if isfirst:
                    # rare case...
                    tmpdict = {'H3': '', 'text': [str(node)]}
                    isfirst = False
                else:
                    tmpdict['text'] = tmpdict['text'] + [str(node)]

    if mustshow:
        pprint(ret)
    return ret


def get_array_of_articles(doc_dict, html, tf=False):
    success = True
    new_dict = {}
    soup = BeautifulSoup(HEADER + html + FOOTER, 'lxml')
    try:
        new_dict = get_articles(soup.body, tf)
    except:
        success = False
    return new_dict, success


def get_content_dict(fail, display_counter, html, doc_id, series_id, doc_dict):
    content_dict, tf = get_array_of_articles(doc_dict,
                                             html, (display_counter % 250 == 0))
    doc_id_str = str(doc_id)
    series_id_str = str(series_id)
    if tf is False:
        fail += 1
    if series_id == 1:
        tmpdict = {series_id_str: content_dict}
        doc_dict[doc_id_str] = tmpdict
    else:
        doc_dict[doc_id_str][series_id_str] = content_dict

    return fail, doc_dict


def get_doc_dict(reader=None):
    fail = 0
    total = 0

    doc_dict = {}

    doc_id = 0
    old_doc_id = -1
    series_id = 1
    html = ''
    display_counter = 0
    for row in reader:
        if len(row) > 1 and row[0].isdigit() and row[1].isdigit():
            if html != '':
                # emit text dictionaries...
                total += 1
                # print(html)
                fail, doc_dict = get_content_dict(
                    fail, display_counter, html, doc_id, series_id, doc_dict)
            old_doc_id = doc_id
            doc_id = int(row[0])
            if old_doc_id == doc_id:
                actual_series_id = int(row[1])
                series_id = actual_series_id
            else:
                series_id = 1
            if display_counter % 100 == 0:
                print(doc_id, series_id)
            display_counter += 1
            # print(row[2])
            html = ','.join(row[2:])
        else:
            html += ','.join(row)
    if html != '':
        fail, doc_dict = get_content_dict(
            fail, display_counter, html, doc_id, series_id, doc_dict)

    return doc_dict, fail, total


def eat_the_rich(filepath=''):
    print(filepath)
    csv.field_size_limit(300000)
    doc_dict = {}
    with open(filepath, newline='') as csvfile:
        # dialect = csv.Sniffer().sniff(csvfile.read(20000))
        # csvfile.seek(0)
        reader = csv.reader(csvfile)
        # ... process CSV file contents here ...
        doc_dict, fail, total = get_doc_dict(reader)
    return doc_dict, fail, total


def john_sky_walker(path='', outfile=''):
    doc_file_id = 0
    doc_dict = {}
    fail = 0
    total = 0
    for root, _, files in os.walk(path):
        files2 = sorted(files)
        for fn, file_ in enumerate(files2):
            if file_ == '.DS_Store':
                continue
            file_path = os.path.join(root, file_)
            if fn == 0:
                print(root)
            articles, fa, to = eat_the_rich(file_path)
            print('fail = %d, total = %d' % (fa, to))
            fail += fa
            total += to
            doc_file_id += 1
            doc_dict = {**doc_dict, **articles}
    return doc_file_id, doc_dict, fail, total



NUMREGEX = re.compile(r'([0-9]+)')

def readCSVFiles(prefix='', directory='./corpus', sortFirstNum=False):
    path = directory
    retlist = []
    for root, _, files in os.walk(path):
        files2 = sorted(files)
        for fn, file_ in enumerate(files2):
            if file_ == '.DS_Store':
                continue
            file_path = os.path.join(root, file_)
            if fn == 0:
                print(root)
            if file_.startswith(prefix):
                retlist.append((file_, file_path))

    if sortFirstNum:
        newlist = []
        for file, path in retlist:
            num = 0
            try:
                num = int(NUMREGEX.search(file).group(0))
            except:
                num = 0
            newlist.append((num, file, path))
        retlist = sorted(newlist, key=lambda z: z[0])
        retlist = [(x[1], x[2]) for x in retlist]

    return retlist


def readIchikawaFiles(prefix='20181205_allabout_', directory='./corpus'):
    return readCSVFiles(prefix=prefix, directory=directory)


def readKijiFiles(prefix='GSAP_ArticleId_', directory='./corpus', sortFirstNum=True):
    return readCSVFiles(prefix=prefix, directory=directory, sortFirstNum=sortFirstNum)

# def main(corpus_dir='', outfile=''):
#     _, doc_dict, fail, total = john_sky_walker(
#         path=corpus_dir, outfile=outfile)
#     print('all %d articles are parsed.' % len(doc_dict))
#     print('%d failed. %d total.' % (fail, total))
#     with open(outfile, 'w') as ofile:
#         json.dump(doc_dict, ofile)


def main(corpus_dir='', kiji_dir='', csv_file=''):
    ich_files = readIchikawaFiles(directory=corpus_dir)
    kiji_files = readKijiFiles(directory=corpus_dir)
    print(ich_files)
    print(kiji_files)

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='generateCSVofKIJI 0.1')
    kiji_dir = arguments[r'<kiji_dir>']
    csv_file = arguments[r'<csv_file>']
    corpus_dir = arguments[r'<corpus_dir>']
    main(corpus_dir=corpus_dir,
         kiji_dir=kiji_dir,
         csv_file=csv_file)
