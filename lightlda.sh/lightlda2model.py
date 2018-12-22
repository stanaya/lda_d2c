#!/usr/bin/python3

import re
import sys
import gzip
import svmlight
import numpy as np
import pickle

def nlexicon (data):
    vmax = 0
    for datum in data:
        if datum[0] > vmax:
            vmax = datum[0]
    return vmax + 1

def match (r,s):
    m = re.search (r,s)
    if m:
        return m.group (1)
    else:
        sys.stderr.write ('match(): invalid content.\n')
        sys.exit (0)

def read_param (file):
    with open (file, 'r') as fh:
        content = fh.read()
        alpha0 = float (match (r'alpha\s*=\s*([0-9.+\-]+)', content))
        beta0  = float (match (r'alpha\s*=\s*([0-9.+\-]+)', content))
        topics = int (match (r'topics\s*=\s*([0-9]+)', content))
        iters  = int (match (r'iters\s*=\s*([0-9]+)', content))
    return alpha0, beta0, topics, iters

def lightlda2beta (dir, topics, beta0):
    data = svmlight.loadex (dir + '/' + 'server_0_table_0.model')
    nlex = nlexicon (data)
    matrix = np.zeros ((nlex,topics)) + beta0
    for w, doc in data:
        L = len (doc.id)
        for j in range(L):
            k = doc.id[j]
            c = doc.cnt[j]
            matrix[w][k] += c
    s = np.sum (matrix, axis=0)
    return np.dot (matrix, np.diag (1.0/s))

def lightlda2gamma (dir, topics, alpha0):
    data = svmlight.loadex (dir + '/' + 'doc_topic.0')
    gamma = []
    for n, doc in data:
        v = np.zeros (topics) + alpha0
        L = len (doc.id)
        for j in range(L):
            k = doc.id[j]
            c = doc.cnt[j]
            v[k] += c
        gamma.append (v)
    return np.array (gamma)

def lightlda2model (dir):
    model = {}
    alpha0,beta0,topics,iters = read_param (dir + '/' + 'param')
    # print alpha0,beta0,topics,iters
    model['alpha'] = alpha0
    model['beta']  = lightlda2beta (dir, topics, beta0)
    model['gamma'] = lightlda2gamma (dir, topics, alpha0)
    return model

def usage ():
    print('usage: lightlda2model dir')
    sys.exit (0)

def main ():
    if len(sys.argv) < 2:
        usage ()
    dir = sys.argv[1]
    print('reading model..')
    model = lightlda2model (dir)
    print('saving model..')
    with gzip.open (dir + '/' + 'model', 'wb') as gf:
        pickle.dump (model, gf, 4)
    print('done.')


if __name__ == "__main__":
    main ()
