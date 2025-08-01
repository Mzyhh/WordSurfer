import gensim.downloader as api
from gensim.models import KeyedVectors
import os
import gzip
import shutil
from random import sample
import numpy as np

import env
import json

def launch(settings, embeddings):
    gz_path = api.load(embeddings[settings["language"]], return_path=True)

    txt_path = os.path.splitext(gz_path)[0] + ".txt"
    if not os.path.exists(txt_path):
        print("Extracting some very important files...")
        with gzip.open(gz_path, 'rb') as f_in:
            with open(txt_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    with open(settings['data path'] + settings['language'] + settings['vocab postfix'], 'r') as voc:
        vocab = set(voc.read().split('\n'))

    result_file = settings["data path"] +  embeddings[settings["language"]] + ".bin"
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

    with open(settings['data path'] + settings['language'] + '_mesg.json', 'r') as f:
        mesg = json.load(f)
    return model, vocab, mesg

if __name__ == "__main__":
    with open(env.SETTINGS_PATH, 'r') as f:
        settings, embeddings = json.load(f)
    model, vocab, mesg = launch(settings, embeddings)
    mode = input(mesg['mode']['choose'] + "\n=>")
    while True:
        if mode == mesg['mode']['playground']:
            expression = input("Type expression\n=>")
            expression = expression.replace(' ', '').replace('\t', '').replace('\n', '').replace('-', '+-').split('+')
            positive = []
            negative = []
            for word in expression:
                l = positive
                if word[0] == '-':
                    word = word[1:]
                    l = negative
                if word not in model.key_to_index:
                    print("Sorry, I have not ever seen word: ", word, ". I skip it.")
                    continue
                l.append(word) 
            print(model.most_similar(positive=positive, negative=negative, topn=1)[0][0])
        if mode == mesg['mode']['victorine']:
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

                               
