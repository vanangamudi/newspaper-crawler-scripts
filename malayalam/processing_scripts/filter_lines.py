import re
import html
from glob import glob
from collections import Counter
from tqdm import tqdm

import string
import unicodedata

import sys
import pickle
import argparse

import unicodedata

from word_freq import ismalayalam

def unicodeToAscii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='filter empty lines and then some')
    
    parser.add_argument('-i','--input-file',
                        help='path to the input file',
                        dest='input_file')
    
    parser.add_argument('-o','--output-file',
                        help='path to the output file',
                        default='a.out', dest='dest_file')
    
    args = parser.parse_args()

    input_file = open(args.input_file)
    dest_file = open(args.dest_file, 'w')
    lines = []
    orig_lines = input_file.readlines()
    for line in tqdm(orig_lines):
        line  = line.strip(string.punctuation)
        if line and len(line.split()) > 2 :
            if not len(line.strip(string.punctuation + ' ')):
                continue
            
            line = line.split()

            malayalam_word_count = 0
            for word in line:
                if ismalayalam(word[0]):
                    malayalam_word_count += 1

            if float(malayalam_word_count)/len(line) < 0.3 :
                continue

            words = line
            line = ' '.join(words)
            if len(words) < 3 and len(line) < 30:
                continue

            lines.append(line)
                

    lines = sorted(lines, key=lambda x: len(x))
    dest_file.write('\n'.join(lines))
    print('removed {} lines'.format(len(orig_lines) - len(lines)))
     
