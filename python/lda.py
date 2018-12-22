#!/usr/bin/python

import ldac
import sys
import getopt
import fmatrix
import numpy as np
import numpy.random as npr
import scipy.special
import logging
from   logging import elprintf

def usage ():
    print 'usage: lda.py OPTIONS train model'
    print 'OPTIONS'
    print ' -K topics  number of topics in LDA'
    print ' -N iters   number of Gibbs iterations'
    print ' -a alpha   Dirichlet hyperparameter on topics'
    print ' -b beta    Dirichlet hyperparameter on words'
    print ' -h         displays this help'
    print '$Id: lda.py,v 1.10 2016/02/06 14:05:38 daichi Exp $'
    sys.exit (0)

def main ():
    cls = '\x1b[K'
    shortopts = "K:N:a:b:h"
    longopts = ['topics=','iters=','alpha=','beta=','help']
    K      = 10
    iters  = 1
    alpha  = 0
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
    if alpha == 0:
        alpha = 50.0 / K

    if len(args) == 2:
        train = args[0]
        model = args[1]
    else:
        usage ()

    eprint('LDA: K = %d, iters = %d, alpha = %g, beta = %g' \
            % (K,iters,alpha,beta))
    logging.start (sys.argv, model)

    eprintf('loading data.. ')
    W,Z = ldaload (train, K)
    D   = len(W)
    V   = lexicon(W)
    N   = datalen(W)
    NW  = np.zeros ((V,K), dtype=np.int32)
    ND  = np.zeros ((D,K), dtype=np.int32)
    NWsum = np.zeros (K, dtype=np.int32)
    alpha_arr = np.zeros (K, dtype=np.float64)
    eprint ('documents = %d, lexicon = %d, nwords = %d' % (D,V,N))

    # initialize
    eprint('initializing..')
    ldac.init (W, Z, NW, ND, NWsum, alpha_arr, alpha)
    iter_step =  150

    for iter in xrange(iters):
        elprintf('%2d,%.4f' \
                 % (iter+1,ldappl(W,Z,NW,ND,alpha_arr,beta)))
        ldac.gibbs (W, Z, NW, ND, NWsum, alpha_arr, beta)

        if iter%iter_step == 0 and iter/iter_step >= 1 and iter/iter_step < 6:
            print "Update params.\n"
            update_hyper_params(NW, ND, alpha_arr, beta)
            fn = 'intermediate_' + str(iter)
            savealpha(fn, alpha_arr)
            #print iter, 'th intermediate beta is ', beta
    eprintf('\n')

    save (model,W,Z,NW,ND,alpha_arr,beta)
    logging.finish ()

def save (model,W,Z,NW,ND,alpha_arr,beta):
    eprint ('saving model.. ')
    savealpha (model,alpha_arr)
    savebeta  (model,NW,beta)
    savetheta (model,ND,alpha_arr)
    savewz    (model,W,Z)
    eprint ('done.')

def savealpha (model, alpha_arr):
    with open (model + '.alpha', 'w') as fh:
        K = alpha_arr.shape[0]
        for k in xrange(K):
            fh.write('%.7e\t%.7e\n' % (k, alpha_arr[k]))

def savebeta (model, NW, beta):
    betas = cnormalize (NW + beta)
    np.savetxt (model + '.beta', betas, '%.7e')

def savetheta (model, ND, alpha_arr):
    theta = rnormalize(ND + alpha_arr)
    np.savetxt (model + '.theta', theta, '%.7e')

def savewz (model, W, Z):
    D = len (W)
    file = model + '.wz'
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

def datalen (W):
    n = 0
    for w in W:
        n += len(w)
    return n

def eprint (s):
    sys.stderr.write (s + '\n')
    sys.stderr.flush ()

def eprintf (s):
    sys.stderr.write (s)
    sys.stderr.flush ()

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

def ldappl (W,Z,NW,ND,alpha_arr,beta):
    L = datalen(W)
    lik = polyad (ND,alpha_arr) + polyaw (NW,beta)
    return np.exp (- lik / L)

def datalen (W):
    return sum (map (lambda x: x.shape[0], W))

def polyad (ND,alpha_arr):
    D = ND.shape[0]
    K = ND.shape[1]
    sum_alpha = np.sum(alpha_arr)
    nd = np.sum(ND,1)
    sum_alpha_arr = np.full(D, sum_alpha)
    lik = np.sum (gammaln (sum_alpha_arr) - gammaln (sum_alpha_arr + nd))
    for n in xrange(D):
        lik += np.sum (gammaln (ND[n,:] + alpha_arr) - gammaln (alpha_arr))
    return lik

def polyaw (NW,beta):
    V = NW.shape[0]
    K = NW.shape[1]
    nw = np.sum(NW,0)
    beta_arr = np.full(V, beta)
    lik = np.sum (gammaln (V * beta) - gammaln (V * beta + nw))
    for k in xrange(K):
        lik += np.sum (gammaln (NW[:,k] + beta_arr) - gammaln (beta_arr))
    return lik

def gammaln (x):
    return scipy.special.gammaln (x)

def cnormalize (M): # column-wise normalize matrix
    s = np.sum(M,0)
    return np.dot(M,np.diag(1.0/s))

def rnormalize (M): # row-wise normalize matrix
    s = np.sum(M,1)
    new_M = M / s[:, np.newaxis]
    return new_M
    #return np.dot(np.diag(1.0/s),M)

def update_hyper_params(NW, ND, alpha_arr, beta):
    #
    update_alpha(ND, alpha_arr)
    #beta = update_beta(NW, beta)
    return beta

def update_alpha(ND, alpha_arr):
    D = ND.shape[0]
    K = ND.shape[1]
    #
    alpha_arr_tmp = alpha_arr
    nd = np.sum(ND,1)
    denom = cal_denom_new_alpha(nd, D, alpha_arr_tmp)
    for k in xrange(K):
        numer = cal_numer_new_alpha(ND, k, alpha_arr_tmp)
        alpha_arr[k] = numer / denom

def cal_denom_new_alpha(nd, D, alpha_arr_tmp):
    sum_alpha = np.sum(alpha_arr_tmp)
    sum_alpha_arr = np.full(D, sum_alpha)
    return np.sum(digamma(nd + sum_alpha_arr) - digamma(sum_alpha_arr))

def cal_numer_new_alpha(ND, k, alpha_arr_tmp):
    return np.sum( digamma(ND[:,k] + alpha_arr_tmp[k]) - digamma(alpha_arr_tmp[k])) * alpha_arr_tmp[k]

def update_beta(NW, beta):
    V = NW.shape[0]
    K = NW.shape[1]
    nw = np.sum(NW,0)
    denom = cal_denom_new_beta(nw, V, K, beta)
    numer = cal_numer_new_beta(nw, V, K, beta)
    print 'beta_d, beta_n = ', denom, numer
    return numer / denom

def cal_denom_new_beta(nw, V, K, beta):
    sum_beta_arr = np.full(K, V * beta)
    return np.sum(digamma(nw + sum_beta_arr) - digamma(sum_beta_arr))

def cal_numer_new_beta(nw, V, K, beta):
    beta_arr = np.full(K, beta)
    # substitute the mean frequencies of each topics.
    return np.sum(digamma( nw / V + beta_arr) - digamma(beta_arr)) * beta

def digamma(x):
    return scipy.special.digamma (x)

if __name__ == "__main__":
    main ()
