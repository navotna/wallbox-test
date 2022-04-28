"""A function that given 2 vectors of integers finds the first repeated number"""
import time
from typing import List, Optional
import unittest


def find_first_repeated_number(
    vector_1: List[int], vector_2: List[int]
) -> Optional[int]:
    """
    :param vector_1: vector of integers
    :param vector_2: vector of integers
    :return: first repeated number in both vectors
    """
    if not vector_1 or not vector_2:
        return None

    set_1, set_2 = set(vector_1), set(vector_2)
    for item_1, item_2 in zip(vector_1, vector_2):
        if item_1 in set_2:
            return item_1
        if item_2 in set_1:
            return item_2
    else:
        return None


class TestFirstRepeatedNumber(unittest.TestCase):
    def test_first_repeated_number_functional(self):
        for v1, v2, expected in [
            ([1, 2], [2, 3], 2),
            ([1, 2], [1, 2], 1),
            ([1, 2], [3, 4], None),
            ([1, 2], [], None),
            ([], [], None),
        ]:
            with self.subTest(v1=v1, v2=v2, expected=expected):
                self.assertEqual(find_first_repeated_number(v1, v2), expected)

    def test_first_repeated_number_performance(self):
        number_of_experiments = 10
        vector_length = 1000000
        for v1_generator, v2_generator, max_allowed_time_secs in [
            (range(vector_length), range(-1, -vector_length, -1), 0.5),
            (range(vector_length), range(0, -vector_length, -1), 0.1),
        ]:
            with self.subTest(
                v_gen1=v1_generator,
                v_gen2=v2_generator,
                max_allowed_time_secs=max_allowed_time_secs,
            ):
                duration_per_experiment = []
                for _ in range(number_of_experiments):
                    v1, v2 = list(v1_generator), list(v2_generator)
                    st_t = time.time()
                    find_first_repeated_number(v1, v2)
                    duration_per_experiment.append(time.time() - st_t)
                self.assertLessEqual(
                    sum(duration_per_experiment) / number_of_experiments,
                    max_allowed_time_secs,
                )
