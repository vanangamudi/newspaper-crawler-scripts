import re
import html
from glob import glob
from collections import Counter
from tqdm import tqdm

import string
import unicodedata

re1 = re.compile(r'  +')


def fixup(x):

    x = x.replace('#39;', "'")
    x = x.replace('amp;', '&')
    x = x.replace('#146;', "'")
    x = x.replace('nbsp;', ' ')
    x = x.replace('#36;', '$')
    x = x.replace('\\n', "\n")
    x = x.replace('quot;', "'")
    x = x.replace('<br />', "\n")
    x = x.replace('\\"', '"')
    x = x.replace('<unk>','u_n')
    x = x.replace(' @.@ ','.')
    x = x.replace(' @-@ ','-')
    x = x.replace('\\', ' \\ ')
    x = x.replace('\u200d','')
    x = x.replace('\xa0',' ')
    x = x.replace('\u200c','')
    x = x.replace('"',' ')
    x = x.replace('"',' ')
    x = x.replace('"',' ')
    
    x = re.sub('[\(\[].*?[\)\]]', '', x)
    x = re.sub('<[^<]+?>', '', x)
    x = re.sub('[A-Za-z]+','ENG ', x)
    x = re.sub(r'\d+.?(\d+)?','NUM ',x).replace("(","").replace(")","")

    return re1.sub(' ', html.unescape(x))

def ismalayalam(char):
    return ord(char) >= 0x0D00 and ord(char) <= 0x0D7F

def punct_tokenize(line):
    words = []
    i = 0
    p = 0
    line = list(line)
    PREV_LETTER = None
    STATES = ['MALAYALAM', 'ASCII', 'PUNCT']
    while i < len(line):
        #if tamil.utf8.istamil(line[i]):
        if ismalayalam(line[i]):
            if PREV_LETTER == 'MALAYALAM':
                i += 1
            else:
                words.append(''.join(line[p:i]).strip())
                p = i
                i += 1
                PREV_LETTER = 'MALAYALAM'
        

        elif line[i] in string.ascii_letters:
            if PREV_LETTER == 'ASCII':
                i += 1
            else:
                words.append(''.join(line[p:i]).strip())
                p = i
                i += 1
                PREV_LETTER = 'ASCII'
        
        else:
            if PREV_LETTER == 'PUNCT':
                i += 1
            else:
                line[i] = unicodedata.normalize('NFD', line[i])
                words.append(''.join(line[p:i]).strip())
                p = i
                i += 1
                PREV_LETTER = 'PUNCT'
            
    words.append(''.join(line[p:i]).strip())
    return [word for word in words if word]

import argparse
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='compile all articles into a single text file')
    parser.add_argument('-o','--output-file',
                        help='path to the output file',
                        default='a.out', dest='dest_file')
    parser.add_argument('-i','--input-dir',
                        help='path to the input dir',
                        default='../data/malayalam', dest='input_dir')
    
    args = parser.parse_args()

    dest_file = open(args.dest_file, 'w')
    counter = Counter()
    for f in tqdm(glob(r'{}/*/*/*/*/*.txt'.format(args.input_dir))):
        with open(f) as f:
            for line in f.readlines()[2:]:
                l = fixup(line)

                for line in l.split('. '):
                    if not len(line) < 10:
                        words = punct_tokenize(line)
                        #print(line)
                        #print(words)
                        counter.update(words)
                        dest_file.write(' '.join(words) + '\n')
                

    with open('word_freq_punct_tokenized.csv' ,'w') as of:
        for word, count in sorted(counter.items(), key=lambda x:x[1], reverse=True):
            of.write('|'.join([word, str(count)]) + '\n')


     
