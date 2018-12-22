#
#    lda.pyx
#    latent Dirichlet allocation in Cython.
#    $Id: ldac.pyx,v 1.2 2015/11/10 12:27:03 daichi Exp $
#
import numpy        as np
import numpy.random as npr
cimport numpy as np
cimport cython
ctypedef np.int32_t dtype_t
ctypedef np.float64_t ftype_t
cdef extern from "math.h":
    double log (double x)

@cython.boundscheck(False)

def init (list W,
          list Z,
          np.ndarray[dtype_t,ndim=2] NW not None,
          np.ndarray[dtype_t,ndim=2] ND not None,
          np.ndarray[dtype_t,ndim=1] NWsum not None,
          np.ndarray[ftype_t,ndim=1] alpha_arr not None,
          np.float64_t alpha):
    cdef int D = ND.shape[0]
    cdef int N
    cdef Py_ssize_t w, z

    for n in range(D):
        N = len(Z[n])
        for i in range(N):
            w         = W[n][i]
            z         = Z[n][i]
            NW[w,z]  += 1
            ND[n,z]  += 1
            NWsum[z] += 1

    for j in xrange(len(alpha_arr)):
      alpha_arr[j] = alpha


def gibbs (list W,
           list Z,
           np.ndarray[dtype_t,ndim=2] NW not None,
           np.ndarray[dtype_t,ndim=2] ND not None,
           np.ndarray[dtype_t,ndim=1] NWsum not None,
           np.ndarray[ftype_t,ndim=1] alpha_arr not None,
           double beta):
    cdef int D = ND.shape[0]
    cdef int K = ND.shape[1]
    cdef int V = NW.shape[0]
    cdef int N
    cdef np.ndarray[ftype_t,ndim=1] p = np.zeros (K)
    cdef np.ndarray[dtype_t,ndim=1] Wn
    cdef np.ndarray[dtype_t,ndim=1] Zn
    cdef Py_ssize_t n, i, j, k, Wni, z, znew, doc_len
    cdef double total, normalizer, sum_alpha
    cdef np.ndarray[ftype_t,ndim=1] rands
    cdef np.ndarray[dtype_t,ndim=1] seq = np.zeros(D,dtype=np.int32)

    # shuffle
    for n in range(D):
        seq[n] = n
    npr.shuffle (seq)

    sum_alpha = np.sum(alpha_arr)

    # sample
    for j in range(D):
        n  = seq[j]
        N  = len(Z[n])
        Zn = Z[n]
        Wn = W[n]
        rands = npr.rand (N)
        for i in range(N):
            Wni         = Wn[i]
            z           = Zn[i]
            NW[Wni,z]  -= 1
            ND[n,z]    -= 1
            NWsum[z]   -= 1
            doc_len = N - 1

            normalizer = 0.0
            for k in range(K):
                p[k] = (ND[n,k] + alpha_arr[k]) / (doc_len + sum_alpha) * (NW[Wni,k] + beta) / (NWsum[k] + beta * V)
                normalizer += p[k]

            total = 0.0
            znew  = 0
            for k in range(K):
                total += p[k] / normalizer
                if rands[i] < total:
                    znew = k
                    break

            Zn[i]          = znew
            NW[Wni,znew]  += 1
            ND[n,znew]    += 1
            NWsum[znew]   += 1
