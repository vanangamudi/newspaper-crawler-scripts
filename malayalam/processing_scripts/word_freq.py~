import re
import html
from glob import glob
from collections import Counter
from tqdm import tqdm

import string
import tamil
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

def allow_only_tamil(word):
    return ''.join(i for i in word if tamil.utf8.istamil(i))

def punct_tokenize(line):
    words = []
    i = 0
    p = 0
    line = list(line)
    PREV_LETTER = None
    STATES = ['TAMIL', 'ASCII', 'PUNCT']
    while i < len(line):
        #if tamil.utf8.istamil(line[i]):
        if ord(line[i]) >= 0x0B02 and ord(line[i]) <= 0x0BCD:
            if PREV_LETTER == 'TAMIL':
                i += 1
            else:
                words.append(''.join(line[p:i]).strip())
                p = i
                i += 1
                PREV_LETTER = 'TAMIL'
        

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
            
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='compile all articles into a single text file')
    parser.add_argument('-o','--output-file',
                        help='path to the output file',
                        default='a.out', dest='dest_file')
    
    args = parser.parse_args()

    dest_file = open(args.dest_file, 'w')
    counter = Counter()
    for f in tqdm(glob(r'*/*/*/*/*.txt')):
        with open(f) as f:
            for line in f.readlines()[2:]:
                l = fixup(line)

                for line in l.split('. '):
                    if not len(line) < 10:
                        """
                        words = [word.strip(string.punctuation) for word in line.split()]
                        words = [allow_only_tamil(word) for word in words]
                        """
                        words = punct_tokenize(line)
                        #print(line)
                        #print(words)
                        counter.update(words)
                        dest_file.write(' '.join(words) + '\n')
                

    with open('word_freq_punct_tokenized.csv' ,'w') as of:
        for word, count in sorted(counter.items(), key=lambda x:x[1], reverse=True):
            of.write('|'.join([word, str(count)]) + '\n')


     
