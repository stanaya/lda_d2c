#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
"""
import sys


def usage():
    print('usage: preNIPS.py NIPS_1987-2015.csv wordsfile.txt')
    print('       output sparse matrix file that work for LDA.py')
    print('       also put words list file.')
    sys.exit(0)


def main(filename="NIPS_1987-2015.csv", wordsfile='words.txt'):
    mtx, row, column = loadNIPScsv(filename, wordsfile)
    svm_file = transpose_NIPS(mtx, row, column, filename)
    print('generated %s and %s' % (svm_file, wordsfile))
    print("next, run LDA.py to obtain latent dirichlet allocations.")


def loadNIPScsv(filename=None, wordsfile=None):
    import csv
    before_transposed = []
    max_vocab_number = -1
    wf = open(wordsfile, "w")
    with open(filename, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row_number, row in enumerate(spamreader):
            if row_number % 100 == 0:
                print("reading %d..." % row_number)
            if row_number == 0:
                continue
            max_vocab_number = row_number  # 1 origin
            wf.write(row[0]+'\n')
            datum = map(int, row[1:])
            before_transposed.append(datum)
    num_rows = len(before_transposed[0])
    num_columns = max_vocab_number
    wf.close()
    return before_transposed, num_rows, num_columns


def transpose_NIPS(mtx=[], num_rows=-1, num_columns=-1, filename=''):
    # should use os.path...
    temp_svm_filename = filename + ".pseudo.svm"

    fi = open(temp_svm_filename, "w")
    for j in xrange(0, num_rows):
        row_list = []
        for i in xrange(0, num_columns):
            item_v = mtx[i][j]
            if item_v == 0:
                continue

            row_list.append("%d:%d" % (i, item_v))
        if j % 100 == 0:
            print("writing %d..." % j)
        fi.write(" ".join(row_list) + "\n")
    fi.close()

    return temp_svm_filename


if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()

    main(sys.argv[1], sys.argv[2])
