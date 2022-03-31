from ..wordle_solver.wordle import Wordle


class TestWordle:
    wordle = Wordle()

    def test_init(self):
        pass

    def test_new_game_with_target(self):
        corpus = ['aaaaa', 'bbbbb', 'ccccc']
        wordle = Wordle(corpus=corpus)
        assert len(wordle.corpus) == len(corpus)
        target_in_corpus = corpus[0]
        wordle.new_game(target=target_in_corpus)
        assert len(wordle.corpus) == len(corpus) - 1
        assert wordle.num_guesses == 0
        wordle.guess('ddddd')
        assert wordle.num_guesses == 1

        target_not_in_corpus = 'zzzzz'
        wordle.new_game(target=target_not_in_corpus)
        assert len(wordle.corpus) == len(corpus) - 1
        assert wordle.num_guesses == 0

    def test_new_game_without_target(self):
        corpus = ['aaaaa', 'bbbbb', 'ccccc']
        wordle = Wordle(corpus=corpus)
        assert len(wordle.corpus) == len(corpus)
        for i in range(1, len(wordle.corpus) + 1):
            target = wordle.new_game()
            assert wordle.num_guesses == 0
            wordle.guess('ddddd')
            assert wordle.num_guesses == 1
            assert len(wordle.corpus) == len(corpus) - i
            assert target in corpus
        assert wordle.new_game() is None
        assert wordle.curr_word is None

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
