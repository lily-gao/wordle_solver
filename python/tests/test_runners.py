import pytest
from ..wordle_solver.solvers import GreedyEntropySolver, Solver
from ..wordle_solver.wordle import Wordle
from ..wordle_solver.runners import Runner


@pytest.fixture(scope='class')
def official_wordle_corpus():
    with open('./data/wordle_possible_answers.txt', 'r') as f:
        wordle_official_list = [line.strip() for line in f.readlines()]
    return wordle_official_list


class TestRunner:
    def test_init(self):
        corpus = ['aaaaaa', 'abbbbb', 'aacccc', 'aaaddd', 'aaaaee', 'ffffff']
        best_guesses = ['aaaaaa', 'aaaaee']
        outcomes = Solver.all_outcomes(element_wise_outcomes=(0, 1, 2), size=6)
        solver = GreedyEntropySolver(corpus=corpus, outcomes=outcomes)
        wordle = Wordle(corpus=corpus)
        runner = Runner(corpus_name='test_corpus', wordle=wordle, solver=solver)
        assert runner.solver == solver
        assert runner.wordle == wordle
        assert runner.init_best_guess in best_guesses

    def test_play(self):
        targets = ['aaron', 'ababa', 'abase', 'abide', 'abled', 'abode', 'abram', 'abuse']
        runner = Runner()
        for target in targets:
            runner.play(target=target)
            assert runner.wordle.num_guesses <= 4

    def test_play_all(self):
        runner = Runner(seed=0)
        nums_of_tries = runner.play_all().values()
        mean_num_tries = sum(nums_of_tries) / len(nums_of_tries)
        assert mean_num_tries <= 3.74
        assert max(nums_of_tries) <= 10

    def test_play_all_using_wordle_corpus(self, official_wordle_corpus):
        wordle = Wordle(corpus=official_wordle_corpus)
        runner = Runner(wordle=wordle, seed=0)
        nums_of_tries = runner.play_all().values()
        mean_num_tries = sum(nums_of_tries) / len(nums_of_tries)
        assert mean_num_tries <= 3.8
        assert max(nums_of_tries) <= 9
