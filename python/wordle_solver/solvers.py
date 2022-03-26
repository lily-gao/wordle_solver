import math
from collections import Counter
from english_words import english_words_lower_alpha_set
from abc import ABC, abstractmethod


class Solver(ABC):
    def __init__(self, corpus=None, outcomes=None, debug_log=False):
        self.corpus = corpus if corpus else Solver.default_corpus()
        self.outcomes = outcomes if outcomes else Solver.all_outcomes((0, 1, 2), 5)
        self.debug_log = debug_log

    @staticmethod
    def default_corpus():
        five_letter_words = [w for w in english_words_lower_alpha_set if len(w) == 5 and w.isalpha()]
        with open('./data/wordle_possible_answers.txt', 'r') as f:
            wordle_official_list = [line.strip() for line in f.readlines()]
        five_letter_words += [w for w in wordle_official_list if w not in five_letter_words]
        five_letter_words += ['tares']
        num_words = len(five_letter_words)
        num_bits_uncertainty = math.log(num_words, 2)
        print('solver initialized with default corpus, num words:', num_words)
        print('bits of info to uncover:', num_bits_uncertainty)
        return five_letter_words

    @staticmethod
    def all_outcomes(element_wise_outcomes, size):
        if size == 0:
            return [[]]
        elif size == 1:
            return [[e] for e in element_wise_outcomes]
        out = []
        for e in element_wise_outcomes:
            out += [[e] + o for o in Solver.all_outcomes(element_wise_outcomes, size - 1)]
        return out

    @abstractmethod
    def get_best_guess(self):
        pass

    @abstractmethod
    def reset(self):
        pass


class EntropySolver(Solver, ABC):
    @abstractmethod
    def update_pool(self, guess, outcome):
        pass

    @abstractmethod
    def get_entropy(self, word):
        pass

    @staticmethod
    def calc_entropy(outcome_probabilities):
        return - sum([p * math.log(p, 2) for p in outcome_probabilities])


class GreedyEntropySolver(EntropySolver):
    def __init__(self, corpus=None, outcomes=None, debug_log=False):
        super().__init__(corpus, outcomes, debug_log)
        # TODO private vars and methods???
        self.pool = self.corpus
        self.correct, self.present, self.present_positions, self.not_present = (None,) * 4

    def get_best_guess(self):
        entropies = {}
        print(f'getting entropies for {len(self.pool)} words')
        for idx, word in enumerate(self.pool):
            entropy, _ = self.get_entropy(word)
            entropies[word] = entropy
            if self.debug_log:
                print(f'{idx}/{len(self.pool) - 1}', word, entropy)
        best_guess = max(entropies, key=entropies.get)
        return best_guess, entropies  # todo are entropies actually needed

    def update_pool(self, guess, outcome):
        self.pool = self.get_possibilities(guess, outcome)

    def reset(self):
        self.pool = self.corpus

    def get_entropy(self, word):
        outcome_probabilities = []
        init_pool_len = len(self.pool)
        restricted_pool = set(self.pool)
        for outcome in self.outcomes:
            possibilities = self.get_possibilities(word, outcome, restricted_pool)
            if possibilities:
                outcome_probability = len(possibilities) / init_pool_len
                outcome_probabilities += [outcome_probability]
                restricted_pool.difference_update(possibilities)
        entropy = EntropySolver.calc_entropy(outcome_probabilities)
        return entropy, outcome_probabilities  # todo outcome_probabilities is for unit tests

    def get_possibilities(self, guess, outcome, restricted_pool=None):
        if restricted_pool is None:
            restricted_pool = self.pool
        self.correct, self.present, self.present_positions, self.not_present = \
            GreedyEntropySolver.parse_outcome(guess, outcome)
        possibilities = self.get_init_possibilities(restricted_pool)
        for word in list(possibilities.keys()):
            remaining_letters = possibilities[word]
            if not self.word_matches_present(remaining_letters) or \
                    not self.word_matches_not_present(remaining_letters):
                del possibilities[word]
                continue
        return list(possibilities.keys())

    @staticmethod
    def parse_outcome(guess, outcome):
        correct, present, present_positions, not_present = [], Counter(), [], set()
        for letter, letter_outcome in zip(guess, outcome):
            if letter_outcome == 0:
                not_present.add(letter)
                correct += [None]
                present_positions += [None]
            elif letter_outcome == 1:
                present[letter] += 1
                present_positions += [letter]
                correct += [None]
            elif letter_outcome == 2:
                correct += letter
                present_positions += [None]
        return correct, present, present_positions, not_present

    def get_init_possibilities(self, restricted_pool):
        possibilities = {}
        for word in restricted_pool:
            matches, remaining_letters = self.word_matches_correct_and_present_positions(word)
            if matches:
                possibilities[word] = remaining_letters
        return possibilities

    def word_matches_correct_and_present_positions(self, word):
        remaining_letters = Counter(word)
        for idx, (to_match, to_avoid) in enumerate(zip(self.correct, self.present_positions)):
            if to_match and to_match.isalpha():
                if word[idx] != to_match:
                    return False, None
                else:
                    remaining_letters[word[idx]] -= 1
            if to_avoid and to_avoid.isalpha() and word[idx] == to_avoid:
                return False, None
        return True, remaining_letters

    def word_matches_present(self, remaining_letters):
        for present_letter, present_count in self.present.items():
            count_after_present = remaining_letters[present_letter] - present_count
            # need exact count in letter in not_present as well, else need positive count (0 incl)
            if (present_letter in self.not_present and count_after_present != 0) or count_after_present < 0:
                return False
            # attention update remaining letters, not returning it
            remaining_letters[present_letter] = count_after_present
        return True

    def word_matches_not_present(self, remaining_letters):
        for letter, count in remaining_letters.items():
            if letter in self.not_present and count > 0:
                return False
        return True
