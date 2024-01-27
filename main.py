import copy
import random
from collections import defaultdict
from typing import DefaultDict

from vocab import load_words, pick_possible_words


Field = DefaultDict[int, DefaultDict[int, str]]
AnchorPoint = tuple[int, int, int]


def init_field() -> Field:
    return defaultdict(lambda: defaultdict(lambda: ''))


def letters_around(field, x, y) -> int:
    result = 0

    for i in range(-1, 2):
        for g in range(-1, 2):
            if i == g == 0:
                continue

            if field[x + i][y + g]:
                result += 1

    return result


def get_anchor_points(field: Field) -> list[AnchorPoint]:
    result = []

    for x in list(field.keys()):
        for y in list(field[x].keys()):
            if not field[x][y]:
                continue

            result.append((x, y, letters_around(field, x, y)))

    return sorted(result, key=lambda x: x[2])


def pick_first_word(letters: list[str], start_length: int = 7) -> str:
    attempts = 10
    letters_size = 8
    word_length = start_length

    while word_length > 3:
        for i in range(attempts):
            sample = random.sample(letters, min(letters_size, len(letters)))
            words = pick_possible_words(sample, word_length, return_one=True)

            if len(words) > 0:
                return words[0]

        word_length -= 1

    return ''


def pick_words(letters: list[str], start_length: int = 6, must_have: str = '') -> list[str]:
    attempts = 10
    letters_size = 8
    word_length = start_length
    result = set()

    while word_length >= 3:
        for i in range(attempts):
            sample = random.sample(letters, min(letters_size, len(letters)))
            words = pick_possible_words(sample, word_length, must_have=must_have)

            if len(words) > 0:
                result.update(words)

        word_length -= 1

    result = list(result)
    return sorted(result, key=lambda x: len(x), reverse=True)


def can_put_word(field: Field, x: int, y: int, word: str, is_horizontal: bool) -> tuple[bool, tuple[int, int] | None]:
    anchor_letter = field[x][y]
    index = word.index(anchor_letter)

    first_part = word[:index]
    second_part = word[index + 1:]

    # free spots: len(first_part) + 1 and len(second_part) + 1
    if is_horizontal:
        for i in range(1, len(first_part) + 2):
            if field[x-i][y]:
                return False, None

        for i in range(1, len(second_part) + 2):
            if field[x+i][y]:
                return False, None

        return True, (x - index, y)
    else:
        for i in range(1, len(first_part) + 2):
            if field[x][y-i]:
                return False, None

        for i in range(1, len(second_part) + 2):
            if field[x][y+i]:
                return False, None

        return True, (x, y - index)


def print_field(field: Field):
    min_y = max_y = 0
    min_x = min(field.keys())
    max_x = max(field.keys())

    for x in field.keys():
        min_y = min(min_y, min(field[x].keys()))
        max_y = max(max_y, max(field[x].keys()))

    print('================')

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            print(field[x][y] or ' ', end=' ')
        print()

    print('================')


def solve(init_letters: list[str]):
    field = init_field()
    first_word = pick_first_word(init_letters)

    assert first_word, 'no first word found!'
    good_enough_solutions = []
    solution = put_word_and_step(
        field,
        init_letters,
        0,
        0,
        first_word,
        None,
        True,
        good_enough_solutions
    )

    if solution:
        print('ideal solution found!')
        print_field(solution)
    elif good_enough_solutions:
        print(len(good_enough_solutions), 'good enough solution found!')
        field, left_letters = good_enough_solutions[0]
        print_field(field)
        print('letters left:', left_letters)
    else:
        print('no solution found! :(')
        return


def put_word_and_step(
        field: Field,
        letters: list[str],
        x: int,
        y: int,
        word: str,
        reuse_letter: str | None,
        is_horizontal: bool,
        good_enough_solutions: list[tuple[Field, list[str]]],
) -> Field | None:
    new_field = copy.deepcopy(field)
    new_letters = letters.copy()

    for i, letter in enumerate(word):
        if reuse_letter and letter == reuse_letter:
            reuse_letter = None
        else:
            new_letters.remove(letter)

        if is_horizontal:
            new_field[x + i][y] = letter
        else:
            new_field[x][y + i] = letter

    if len(new_letters) == 0:
        return new_field

    if len(new_letters) <= 1:
        good_enough_solutions.append((new_field, new_letters))

    print_field(new_field)

    anchor_points = get_anchor_points(new_field)
    points_to_try = anchor_points[:4]
    for x, y, _ in points_to_try:
        letter = new_field[x][y]
        words = pick_words([letter, *new_letters], 6, must_have=letter)
        # could be 300+ words...

        for word in words[:10]:
            can_put, where = can_put_word(new_field, x, y, word, True)
            if can_put:
                solution = put_word_and_step(
                    new_field,
                    new_letters,
                    where[0],
                    where[1],
                    word,
                    letter,
                    True,
                    good_enough_solutions
                )
                if solution:
                    return solution

            can_put, where = can_put_word(new_field, x, y, word, False)
            if can_put:
                solution = put_word_and_step(
                    new_field,
                    new_letters,
                    where[0],
                    where[1],
                    word,
                    letter,
                    False,
                    good_enough_solutions
                )
                if solution:
                    return solution

    return None


if __name__ == '__main__':
    load_words()
    print('dict loaded!')

    a = pick_words(['a', 'c'], must_have='a')

    init_string = 'ielebtaemltnvaaoalpse'
    init_letters = [c for c in init_string]

    solve(init_letters)
