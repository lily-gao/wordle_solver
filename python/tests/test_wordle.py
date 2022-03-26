from ..wordle_solver.wordle import Wordle


class TestWordle:
    wordle = Wordle()

    def test_init(self):
        pass

    def test_non_repeating_letters(self):
        self.wordle.curr_word = 'abcde'
        assert self.wordle.guess('edcba') == (False, [1, 1, 2, 1, 1])
        assert self.wordle.guess('zzcba') == (False, [0, 0, 2, 1, 1])

    def test_repeating_letters(self):
        wordle = Wordle()
        wordle.curr_word = 'levee'
        assert wordle.guess('eeeee') == (False, [0, 2, 0, 2, 2])
        assert wordle.guess('velee') == (False, [1, 2, 1, 2, 2])
        assert wordle.guess('veeez') == (False, [1, 2, 1, 2, 0])
        assert wordle.guess('lllll') == (False, [2, 0, 0, 0, 0])
        assert wordle.guess('zllll') == (False, [0, 1, 0, 0, 0])
        assert wordle.guess('ezezz') == (False, [1, 0, 1, 0, 0])
        assert wordle.num_guesses == 6

    def test_successful_guess(self):
        self.wordle.curr_word = 'abcde'
        assert self.wordle.guess('abcde') == (True, [2, 2, 2, 2, 2])
        assert self.wordle.curr_word is None
