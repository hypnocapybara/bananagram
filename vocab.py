import nltk
import itertools
from string import punctuation


DICT = {}


def add_word(word):
    it = DICT

    for i, char in enumerate(word):
        is_last = i == len(word) - 1

        if char not in it:
            it[char] = {}

        it = it[char]

        if is_last:
            it['$'] = True


def load_words():
    for word in nltk.corpus.words.words('en'):
        word = word.lower()

        if len(word) == 1 or any(char in punctuation for char in word):
            continue

        add_word(word)


def pick_possible_words(
        letters: list[str],
        min_length: int = 0,
        return_one: bool = False,
        must_have: str = ''
) -> list[str]:
    words = set()

    for chars in itertools.permutations(letters):
        if must_have and must_have not in chars:
            continue

        possible_words = []

        it_path = []
        it = DICT
        for c in chars:
            if c not in it:
                break

            it = it[c]
            it_path.append(c)

            if '$' in it:
                new_word = ''.join(it_path)
                if len(new_word) >= min_length and (not must_have or must_have in new_word):
                    if return_one:
                        return [new_word]
                    else:
                        possible_words.append(new_word)

        if possible_words:
            words.update(possible_words)

    words = list(words)
    return sorted(words, key=lambda x: len(x), reverse=True)
