import gensim.downloader as api
from gensim.models import KeyedVectors
import os
import gzip
import shutil

def launch():
    gz_path = api.load("glove-twitter-100", return_path=True)

    txt_path = os.path.splitext(gz_path)[0] + ".txt"
    if not os.path.exists(txt_path):
        print("Extracting some very important files...")
        with gzip.open(gz_path, 'rb') as f_in:
            with open(txt_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    result_file = "glove.twitter.100d.model.bin"
    if not os.path.exists(result_file):
        print("Transforming one substance to another, may take a while...")
        model = KeyedVectors.load_word2vec_format(txt_path, binary=False)
        model.save(result_file)

    vocab = []
    model = KeyedVectors.load(result_file, mmap='r') 
    with open('eng_vocab.txt', 'r') as voc:
        word = voc.readline().strip()
        if word in model.key_to_index:
            vocab.append(word)
    return model, vocab

if __name__ == "__main__":
    model, vocab = launch()
    mode = input("What's mode you want to choose: playground (`p`) or victorine (`v`)\n=>")
    while True:
        if mode == 'p':
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
        if mode == 'v':
            score = 0
            num_words = 2
            pass
