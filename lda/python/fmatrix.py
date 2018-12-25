#!/usr/bin/python
"""
fmatrix.py : loading sparse feature matrix.
$Id: fmatrix.py,v 1.1 2015/09/29 11:18:11 daichi Exp $
"""

import numpy as np

def plain (file):
    """
    build a plain word sequence for LDA.
    """
    data = []
    with open (file, 'r') as fh:
        for line in fh:
            words = parse (line)
            if len(words) > 0:
                data.append (words)
    return data

def parse (line):
    words = []
    tokens = line.split()
    if len(tokens) > 0:
        for token in tokens:
            [id,cnt] = token.split(':')
            # w = int(id) - 1
            w = int(id)
            c = int(cnt)
            words.extend ([w for x in xrange(c)])
        return words
    else:
        return []

