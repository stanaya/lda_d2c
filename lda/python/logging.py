#!/usr/bin/python
#
#    logging.py
#    logging module.
#    $Id: logging.py,v 1.3 2015/11/30 12:08:37 daichi Exp $
#
# usage:
#
# import sys
# import logging
# from   logging import lprintf
# from   logging import elprintf
#
# logging.start (sys.argv, model)
# lprintf('foo\n')
# elprintf('bar\n')
# logging.finish ()
#

import sys
import time
import socket

f   = None
cls = '\x1b[K'

def start (argv,model):
    global f
    f = open(model + '.log', 'w')
    f.write ('init   : %s\n' % ' '.join(argv))
    f.write ('host   : %s\n' % socket.gethostname())
    f.write ('start  : %s\n' % time.ctime())
    f.write ('============\n')
    f.flush ()

def finish ():
    global f
    f.write ('============\n')
    f.write ('finish : %s\n' % time.ctime())
    f.close ()

def lprintf (s):
    f.write (s)
    f.flush ()

def elprintf (s):
    global cls
    f.write (s + '\n')
    f.flush ()
    sys.stderr.write (cls + s + '\r')
    sys.stderr.flush ()
    
def main ():
    start ([], 'hoge')
    finish ()

if __name__ == "__main__":
    main ()
    
