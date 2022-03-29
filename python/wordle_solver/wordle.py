from collections import Counter
import random
from .solvers import Solver


class Wordle:
    def __init__(self, corpus=None, seed=None, debug_log=False):
        self.corpus = corpus.copy() if corpus else Solver.default_corpus()
        self.curr_word = None
        self.num_guesses = 0
        self.seed = seed
        self.debug_log = debug_log

    def new_game(self):
        if not self.corpus:
            return None
        if self.seed is not None:
            random.seed(self.seed)
        self.curr_word = random.choice(self.corpus)
        self.num_guesses = 0
        self.corpus.remove(self.curr_word)
        if self.debug_log:
            print(f'{len(self.corpus)} left after this word.')
        return self.curr_word

    def guess(self, guess):
        if not self.curr_word:
            raise ValueError('new game needs to be started before guessing')
        counter = Counter(self.curr_word)
        outcome = []
        to_fill = []
        for location, guess_letter in enumerate(guess):
            if guess_letter == self.curr_word[location]:
                outcome += [2]
                counter[guess_letter] -= 1
            elif guess_letter not in counter:
                outcome += [0]
            else:
                to_fill += [location]
                outcome += [None]
        for location in to_fill:
            guess_letter = guess[location]
            if counter[guess_letter] >= 1:
                outcome[location] = 1
                counter[guess_letter] -= 1
            else:
                outcome[location] = 0
        self.num_guesses += 1
        guess_is_successful = outcome == [2] * 5
        if guess_is_successful:
            self.curr_word = None
        return guess_is_successful, outcome
