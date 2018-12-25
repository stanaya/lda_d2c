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
          np.ndarray[dtype_t,ndim=1] NWsum not None):
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
    

def gibbs (list W,
           list Z,
           np.ndarray[dtype_t,ndim=2] NW not None,
           np.ndarray[dtype_t,ndim=2] ND not None,
           np.ndarray[dtype_t,ndim=1] NWsum not None,
           double alpha, double beta):
    cdef int D = ND.shape[0]
    cdef int K = ND.shape[1]
    cdef int V = NW.shape[0]
    cdef int N
    cdef np.ndarray[ftype_t,ndim=1] p = np.zeros (K)
    cdef np.ndarray[dtype_t,ndim=1] Wn
    cdef np.ndarray[dtype_t,ndim=1] Zn
    cdef Py_ssize_t n, i, j, k, Wni, z, znew
    cdef double total
    cdef np.ndarray[ftype_t,ndim=1] rands
    cdef np.ndarray[dtype_t,ndim=1] seq = np.zeros(D,dtype=np.int32)

    # shuffle
    for n in range(D):
        seq[n] = n
    npr.shuffle (seq)
    
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

            total = 0.0
            for k in range(K):
                p[k] = (NW[Wni,k] + beta) / (NWsum[k] + V * beta) * \
                       (ND[n,k] + alpha)
                total += p[k]
            
            rands[i] = total * rands[i]
            total = 0.0
            znew  = 0
            for k in range(K):
                total += p[k]
                if rands[i] < total:
                    znew = k
                    break

            Zn[i]          = znew
            NW[Wni,znew]  += 1
            ND[n,znew]    += 1
            NWsum[znew]   += 1

