import pickle
import matplotlib.pyplot as plt
from .wordle import Wordle
from .solvers import GreedyEntropySolver


class Runner:
    def __init__(self, corpus_name='five_letter_words', wordle=None, solver=None, debug_log=True):
        self.wordle = wordle if wordle else Wordle()
        self.solver = solver if solver else GreedyEntropySolver(debug_log=debug_log)
        self.init_best_guess = self.get_init_best_guess()
        self.debug_log = debug_log
        self.entropies_file_prefix = f'./entropies/{corpus_name}'
        self.init_entropies_file = f'{self.entropies_file_prefix}/init_entropies.pickle'
        self.game_entropies_file = f'{self.entropies_file_prefix}/game_entropies.pickle'

    def get_init_best_guess(self):
        try:
            with open(self.init_entropies_file, 'rb') as f:
                init_entropies = pickle.load(f)
                init_best_guess = reversed(sorted(init_entropies, key=init_entropies.get)).__next__()
        except FileNotFoundError:
            init_best_guess, init_entropies = self.solver.get_best_guess()
            with open(self.init_entropies_file, 'wb+') as f:
                pickle.dump(init_entropies, f)
            print('init entropies',
                  [(w, init_entropies[w]) for w in reversed(sorted(init_entropies, key=init_entropies.get))])
        return init_best_guess

    def play_all(self):
        num_tries = {}
        entropies = {}
        target = self.wordle.new_game()
        while target is not None:
            # init_best_guess obtained previously over the whole corpus, does not change with target
            best_guess = self.init_best_guess
            guess_is_successful = False
            while not guess_is_successful:
                guess_is_successful, outcome = self.wordle.guess(best_guess)
                print('TARGET: ', target, '| GUESS: ', best_guess, '| OUTCOME: ', outcome)
                if guess_is_successful:
                    num_tries[target] = self.wordle.num_guesses
                    print('GOT IT!: ', self.wordle.num_guesses, 'tries')
                    break  # not super necessary?
                self.solver.update_pool(best_guess, outcome)
                prev_guess = best_guess  # for logging entropies only
                if self.wordle.num_guesses == 1:
                    best_guess, guess_entropies = self.load_or_calculate_entropies(best_guess, outcome)
                else:
                    best_guess, guess_entropies = self.solver.get_best_guess()
                entropies[(target, prev_guess, self.wordle.num_guesses)] = guess_entropies
            target = self.wordle.new_game(debug_log=True)
        with open(self.game_entropies_file, 'wb+') as f:
            pickle.dump(entropies, f)
        print('mean num tries', sum(num_tries.values()) / len(num_tries.values()))
        print('max, min num tries', max(num_tries.values()), min(num_tries.values()))
        plt.hist(num_tries.values(), bins=range(1, max(num_tries.values()) + 2))
        return num_tries, entropies

    def load_or_calculate_entropies(self, guess, outcome):
        file_name = f'{self.entropies_file_prefix}/{guess}_{"".join([str(o) for o in outcome])}.pickle'
        try:
            with open(file_name, 'rb') as f:
                guess_entropies = pickle.load(f)
                best_guess = max(guess_entropies, key=guess_entropies.get)
                print('loaded entropies from file')
        except FileNotFoundError:
            print('file not found, calculating entropies')
            best_guess, guess_entropies = self.solver.get_best_guess()
            with open(file_name, 'wb') as f:
                pickle.dump(guess_entropies, f)
        return best_guess, guess_entropies

# def graph_outcomes(word, corpus=five_letter_words, outcomes=None):
#     if not outcomes:
#         outcomes = all_outcomes((0, 1, 2), 5)
#     init_copus_len = len(corpus)
#     corpus = set(corpus)
#     outcome_probabilities = {}
#     for outcome in outcomes:
#         possibilities = get_possibilities(word, outcome, corpus)
#         if possibilities:
#             outcome_probabilities[''.join([str(o) for o in outcome])] = len(possibilities) / init_copus_len
#             corpus.difference_update(possibilities)
#     sorted_probs = [p for p in reversed(sorted(outcome_probabilities.values()))]
#     plt.bar([i for i in range(len(sorted_probs))], sorted_probs)
#     plt.title(word)
#     plt.show()
#     print(sum(outcome_probabilities.values()), len(outcome_probabilities))

# for w in ['reese', 'eerie', 'isaac', 'raise', 'tares']:
#     graph_outcomes(w)
#     print(init_entropies[w])