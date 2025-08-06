from random import sample
import numpy as np

from app import WordSurfer
from config import launch
from screens.playground import PlaygroundScreen


if __name__ == "__main__":
    app = WordSurfer(launch()) 
    playground = PlaygroundScreen(app.config)

    mode = input(app.config.messages['mode']['choose'] + "\n=>")
    while True:
        if mode == app.config.messages['mode']['playground']:
            expression = input("Type expression\n=>")
            pos, neg, unk_pos, unk_neg = playground.split_positive_negative(expression)
            if len(unk_pos) + len(unk_neg) != 0:
                print("Following words are unknown for us (we skipped them): ", end='')
            for w in unk_pos + unk_neg:
                print(w, end=' ')
            else:
                print()
            if len(pos) + len(neg) == 0:
                print("There is no words to compute expression, let's go next!")
            else:
                print(playground.compute_expression(pos, neg))
        elif mode == app.config.messages['mode']['victorine']:
            score = 0
            print("Choose number of words:\n1 - hah - just a warm up :)\n2 - easy")
            print("3 - already hard\n4.. - monster level XD")
            n_words = int(input())
            n_options = 4
            while True:
                n_positive = np.random.randint(1, n_words + 1)
                positive = sample(app.config.vocabulary, n_positive)
                negative = sample(app.config.vocabulary, n_words - n_positive)
                top_similar = app.config.model.most_similar(positive=positive, negative=negative, topn=max(10, n_options))
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

                               
