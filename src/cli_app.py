from app import WordSurfer
from config import launch
from screens.playground import PlaygroundScreen
from screens.quiz import QuizScreen


if __name__ == "__main__":
    app = WordSurfer(launch()) 
    playground = PlaygroundScreen(app.config)
    quiz = QuizScreen(app.config)

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
        elif mode == app.config.messages['mode']['quiz']:
            score = 0
            print("Choose number of words:\n1 - hah - just a warm up :)\n2 - easy")
            print("3 - already hard\n4.. - monster level XD")
            quiz.n_words = int(input())
            while True:
                expr, target, other = quiz.rand_expr(quiz.n_words, quiz.n_options)
                print(expr, '= ?')
                print("Answer options: ")
                for i, w in enumerate(other):
                    print(f'{i + 1}. {w}')
                ans = input("type your choice (number or word)\n=>")
                try:
                    ans = int(ans)
                    to_cmp = other.index(target) + 1
                except:
                    to_cmp = target
                if ans == to_cmp:
                    quiz.user_score += 1
                    print("You are absolutely right! +1! Score: ", quiz.user_score)
                else:
                    print("Ooops... Correct words is", target)
        else:
            print("brr unknown mode")
            break

