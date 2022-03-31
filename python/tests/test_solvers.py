from ..wordle_solver.solvers import GreedyEntropySolver
from ..wordle_solver.solvers import EntropySolver
from .conftest import tol


class TestGreedyEntropySolver:
    solver = GreedyEntropySolver()

    def test_init(self):
        pass

    def test_get_best_guess(self):
        self.solver.pool = ['aaaaa', 'abbbb', 'aaccc', 'aaadd', 'aaaae', 'fffff']
        best_guesses = ['aaaaa', 'aaaae']
        best_guess, entropies = self.solver.get_best_guess()
        sorted_by_entropies = sorted(entropies.items(), key=lambda elem: elem[1], reverse=True)
        best_entropy = sorted_by_entropies[0][1]
        assert best_guess in best_guesses
        for w in best_guesses:
            assert entropies[w] == best_entropy

    def test_update_pool(self):
        self.solver.pool = ['aaaaa', 'abbbb', 'aaccc', 'aaadd', 'aaaae', 'fffff']
        self.solver.update_pool(guess='aaccc', outcome=[2, 2, 0, 0, 0])
        assert sorted(self.solver.pool) == sorted(['aaaaa', 'aaadd', 'aaaae'])
        self.solver.update_pool(guess='aaadd', outcome=[2, 2, 2, 0, 0])
        assert sorted(self.solver.pool) == sorted(['aaaaa', 'aaaae'])
        self.solver.update_pool(guess='aaaaa', outcome=[2, 2, 2, 2, 0])
        assert self.solver.pool == ['aaaae']

    def test_get_possibilities(self):
        self.solver.pool = ['abcde', 'eycby', 'excbx', 'excbd', 'excxx', 'ebcxx', 'eycyy']
        assert self.solver.get_possibilities('abcde', [0, 1, 2, 0, 1]) == ['eycby', 'excbx']
        assert self.solver.get_possibilities('excbx', [2, 1, 2, 1, 2]) == ['ebcxx']
        self.solver.pool = ['gases', 'james', 'oases', 'hades']
        assert self.solver.get_possibilities('gases', [0, 2, 0, 2, 2]) == ['james', 'hades']
        self.solver.pool = ['ggggg', 'zzggg', 'zzzgg', 'zzzzg']
        assert self.solver.get_possibilities('ggaaa', [1, 1, 0, 0, 0]) == ['zzggg', 'zzzgg']
        assert self.solver.get_possibilities('gggaa', [1, 1, 0, 0, 0]) == ['zzzgg']
        self.solver.pool = ['kneed']
        assert self.solver.get_possibilities('raise', [0, 0, 0, 0, 1]) == ['kneed']
        self.solver.pool = ['ezeze', 'ezeee']
        assert self.solver.get_possibilities('reese', [0, 1, 2, 0, 2]) == ['ezeze', 'ezeee']

    # todo test is too long, maybe find smaller starting pool
    def test_get_entropy(self):
        self.solver.pool = self.solver.corpus
        more_than_one, less_than_one = [], []
        words_with_bad_entropies = []
        max_num_outcomes = min(len(self.solver.pool),  len(self.solver.outcomes))
        max_possible_entropy = EntropySolver.calc_entropy([1 / max_num_outcomes] * max_num_outcomes)
        for i, w in enumerate(self.solver.corpus):
            entropy, probabilities = self.solver.get_entropy(w)
            p_sum = sum(probabilities)
            print(i, w)
            if p_sum < 1 - tol:
                less_than_one += [w]
                print('<1', p_sum)
            elif 1 + tol < p_sum:
                more_than_one += [w]
                print('>1', p_sum)
            if entropy > max_possible_entropy:
                words_with_bad_entropies += [w]
                print('entropy out of bounds', entropy)
        assert len(more_than_one) == 0, f'words with probs > 1: {more_than_one}'
        assert len(less_than_one) == 0, f'words with probs < 1: {less_than_one}'
        assert len(words_with_bad_entropies) == 0, 'words with out of bound entropies'
