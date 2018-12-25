#!/usr/local/bin/python
#
#    svmlight.py
#    SVMlight format IO, like fmatrix.py.
#    $Id: svmlight.py,v 1.1 2018/10/18 12:58:30 daichi Exp $
#
import numpy as np

class document:
    def __init__ (self):
        self.id  = []
        self.cnt = []

def load (file):
    data = []
    with open (file, 'r') as fh:
        for line in fh:
            tokens = line.split()
            if len(tokens) > 1:
                doc = document ()
                for token in tokens[1:]:
                    id,cnt = token.split(':')
                    doc.id.append (int(id))
                    doc.cnt.append (int(cnt))
                data.append (doc)
    return data

def loadex (file):
    data = []
    with open (file, 'r') as fh:
        for line in fh:
            tokens = line.split()
            if len(tokens) > 1:
                n = int (tokens[0])
                doc = document ()
                for token in tokens[1:]:
                    id,cnt = token.split(':')
                    doc.id.append (int(id))
                    doc.cnt.append (int(cnt))
                data.append ((n,doc))
    return data

