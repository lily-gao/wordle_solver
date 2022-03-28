from ..wordle_solver.solvers import GreedyEntropySolver, Solver
from ..wordle_solver.wordle import Wordle
from ..wordle_solver.runners import Runner


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

    def test_play_all(self):
        runner = Runner()
        nums_of_tries = runner.play_all()
        assert sum(nums_of_tries.values()) / len(nums_of_tries) <= 3.8
