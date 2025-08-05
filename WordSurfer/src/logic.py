import gensim.downloader as api
from gensim.models import KeyedVectors
import typing as t
import os
import gzip
import shutil
from random import sample
import numpy as np
from configparser import ConfigParser
import json

from utils.get_resources import get_resource_file

model:KeyedVectors = None
vocab:t.List[str] = []
mesg:dict = dict()
config: ConfigParser = ConfigParser() 

def launch() -> None:
    """Load embeddings if needed unpack them and do other important stuff."""
    global model, vocab, mesg, sets
    config.read(str(get_resource_file('config.ini')))


    gz_path = api.load(str(config['General']['embeddings']), return_path=True)

    txt_path = os.path.splitext(gz_path)[0] + ".txt"
    if not os.path.exists(txt_path):
        print("Extracting some very important files...")
        with gzip.open(gz_path, 'rb') as f_in:
            with open(txt_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    data_path = str(get_resource_file("data/"))  + '/'
    with open(data_path + str(config['General']['language']) + '_vocab.txt', 'r') as voc:
        vocab = set(voc.read().split('\n'))

    result_file = data_path +  str(config['General']['embeddings']) + ".bin"
    if not os.path.exists(result_file):
        print("Transforming one substance to another, may take a while...")
        model = KeyedVectors.load_word2vec_format(txt_path, binary=False)
        clean_words = {word: model[word] for word in model.key_to_index
                       if word in vocab and word.isalpha()}
        model = KeyedVectors(vector_size=model.vector_size)
        model.add_vectors(keys=list(clean_words.keys()), weights=list(clean_words.values()))
        model.save(result_file)
    model = KeyedVectors.load(result_file, mmap='r') 

    vocab = [word for word in vocab if word in model.key_to_index]

    with open(data_path + str(config['General']['language']) + '_mesg.json', 'r') as f:
        mesg = json.load(f)

def split_positive_negative(expression: str) -> t.Tuple[t.List[str], t.List[str], t.List[str], t.List[str]]:
    """Split expression on four lists: positive, negative, not-presented pos/neg.
    :param expression: Expression containing letters and +/-
    :returns: a tuple of four lists of strings
    example usage:
    >>> split_positive_negative("aboba - cat + dog - ksljdfv")
    (['dog'], ['cat'], ['aboba'], ['ksljdfv'])"""

    splitted = expression.replace(' ', '').replace('\t', '').replace('\n', '').replace('-', '+-').split('+')
    pos, neg, unk_pos, unk_neg = [], [], [], []
    for word in splitted:
        ref, unk_ref = pos, unk_pos
        if word[0] == '-':
            word = word[1:]
            ref, unk_ref = neg, unk_neg
        if word not in model.key_to_index:
            unk_ref.append(word)
        else:
            ref.append(word)
    return pos, neg, unk_pos, unk_neg

def compute_expression(positive_words, negative_words) -> str:
    return model.most_similar(positive=positive_words, negative=negative_words, topn=1)[0][0]

if __name__ == "__main__":
    launch()
    mode = input(mesg['mode']['choose'] + "\n=>")
    while True:
        if mode == mesg['mode']['playground']:
            expression = input("Type expression\n=>")
            pos, neg, unk_pos, unk_neg = split_positive_negative(expression)
            if len(unk_pos) + len(unk_neg) != 0:
                print("Following words are unknown for us (we skipped them): ", end='')
            for w in unk_pos + unk_neg:
                print(w, end=' ')
            else:
                print()
            if len(pos) + len(neg) == 0:
                print("There is no words to compute expression, let's go next!")
            else:
                print(compute_expression(pos, neg))
        elif mode == mesg['mode']['victorine']:
            score = 0
            print("Choose number of words:\n1 - hah - just a warm up :)\n2 - easy")
            print("3 - already hard\n4.. - monster level XD")
            n_words = int(input())
            n_options = 4
            while True:
                n_positive = np.random.randint(1, n_words + 1)
                positive = sample(vocab, n_positive)
                negative = sample(vocab, n_words - n_positive)
                top_similar = model.most_similar(positive=positive, negative=negative, topn=max(10, n_options))
                target = top_similar[0][0]
                all_words = [target] + [w for w, _ in top_similar[-n_options + 1:]]
                print("Expression: ", ' + '.join(positive) + (' - ' if len(negative) else '') + ' - '.join(negative))
                print("Options: ", end='')
                idx = np.arange(len(all_words))
                np.random.shuffle(idx)
                for i in idx:
                    print(all_words[i], end='\t')
                ans = input("\ntype your choice\n=>")
                if ans == target:
                    score += 1
                    print("You are absolutely right! +1! Score: ", score)
                else:
                    print("Ooops... Correct words is", target)
        else:
            print("brr unknown mode")
            break

                               
