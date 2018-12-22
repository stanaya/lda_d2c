#!/usr/bin/python

import lda
import sys
import getopt
import fmatrix
import numpy as np
import numpy.random as npr
import scipy.special

def usage ():
    print 'usage: runlda OPTIONS train model'
    print 'OPTIONS'
    print ' -K topics  number of topics in LDA'
    print ' -N iters   number of Gibbs iterations'
    print ' -a alpha   Dirichlet hyperparameter on topics'
    print ' -b beta    Dirichlet hyperparameter on words'
    print ' -h         displays this help'
    print '$Id: runlda.py,v 1.8 2015/10/02 01:37:48 daichi Exp $'
    sys.exit (0)

def main ():

    shortopts = "K:N:a:b:h"
    longopts = ['topics=','iters=','alpha=','beta=','help']
    K      = 10
    iters  = 1
    alpha  = 50.0 / K
    beta   = 0.01
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError, err:
        usage ()
    for o,a in opts:
        if o in ('-K', '--topics'):
            K     = int (a)
        elif o in ('-N', '--iters'):
            iters = int (a)
        elif o in ('-a', '--alpha'):
            alpha = float (a)
        elif o in ('-b', '--beta'):
            beta = float (a)
        elif o in ('-h', '--help'):
            usage ()
        else:
            assert False, "unknown option"

    if len(args) == 2:
        train = args[0]
        model = args[1]
    else:
        usage ()

    print 'LDA: K = %d, iters = %d, alpha = %g, beta = %g' \
          % (K,iters,alpha,beta)
          
    print 'loading data..'
    W,Z = ldaload (train, K)
    D   = len(W)
    V   = lexicon(W)
    NW  = np.zeros ((V,K), dtype=np.int32)
    ND  = np.zeros ((D,K), dtype=np.int32)
    NWsum = np.zeros (K, dtype=np.int32)
    print 'documents = %d, lexicon = %d' % (D,V)

    # initialize
    for n in range(D):
        N = len(Z[n])
        for i in xrange(N):
            w          = W[n][i]
            z          = Z[n][i]
            NW[w,z]   += 1
            ND[n,z]   += 1
            NWsum[z]  += 1

    for iter in xrange(iters):
        sys.stderr.write('Gibbs iteration [%d/%2d] PPL = %.4f\n' \
                         % (iter+1,iters,ldappl(W,Z,NW,ND,alpha,beta)))
        sys.stderr.flush()
        lda.gibbs (W, Z, NW, ND, NWsum, alpha, beta)
    sys.stderr.write('\n')
    save (model,W,Z,NW,ND)
    print 'done.'

def save (model,W,Z,NW,ND):
    wzsave (model,W,Z)
    np.savetxt (model + '.ND',ND,'%.7e')
    
def wzsave (model, W, Z):
    D = len (W)
    file = model + '.wz'
    print 'saving words and topics to %s ..' % file
    with open (file, 'w') as fh:
        for n in xrange(D):
            N = W[n].shape[0]
            for i in xrange(N):
                fh.write('%d\t%d\n' % (W[n][i], Z[n][i]))
            fh.write('\n')
    
def lexicon (words):
    v = None
    for word in words:
        if max(word) > v:
            v = max(word)
    return v + 1

def int32 (words):
    data = []
    for word in words:
        data.append (np.array(word, dtype=np.int32))
    return data

def ldaload (file, K):
    words = fmatrix.plain (file)
    topics = randtopic (words, K)
    return int32(words), int32(topics)
    
def randtopic (words, K):
    topics = []
    for word in words:
        topic = npr.randint(K, size=len(word))
        topics.append (topic)
    return topics

def ldappl (W,Z,NW,ND,alpha,beta):
    L = datalen(W)
    lik = polyad (ND,alpha) + polyaw (NW,beta)
    return np.exp (- lik / L)

def datalen (W):
    return sum (map (lambda x: x.shape[0], W))

def polyad (ND,alpha):
    D = ND.shape[0]
    K = ND.shape[1]
    nd = np.sum(ND,1)
    lik = np.sum (gammaln (K * alpha) - gammaln (K * alpha + nd))
    for n in xrange(D):
        lik += np.sum (gammaln (ND[n,:] + alpha) - gammaln (alpha))
    return lik

def polyaw (NW,beta):
    V = NW.shape[0]
    K = NW.shape[1]
    nw = np.sum(NW,0)
    lik = np.sum (gammaln (V * beta) - gammaln (V * beta + nw))
    for k in xrange(K):
        lik += np.sum (gammaln (NW[:,k] + beta) - gammaln (beta))
    return lik

def gammaln (x):
    return scipy.special.gammaln (x)

if __name__ == "__main__":
    main ()

    
