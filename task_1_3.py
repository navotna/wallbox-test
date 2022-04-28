"""
A function that given a sequence of coin flips (0 is tails, 1 is heads) finds the
minimum quantity of permutations so that the sequence ends interspersed. For
example, given the sequence 0,1,1,0 how many changes are needed so that the
result is 0,1,0,1
"""
import math
import unittest
from typing import List


def count_number_of_changes(seq: List[int]):
    """Calculates minimal amount of element flips (1 to 0 OR 0 to 1)
    so the sequence will not have repeated elements:
    [0,0,0,0,1,0,1,1] -> [(1),0,(1),0,1,0,1,(0)] -> 3
    """
    seq_len = len(seq)
    seq_str = "".join([str(each) for each in seq])
    first_1_str = "".join(["10" for _ in range(math.ceil(seq_len / 2))])[:seq_len]
    first_0_str = "0" + first_1_str[:-1]
    seq_int = int("1" + seq_str, 2)
    first_1_int = int("1" + first_1_str, 2)
    first_0_int = int("1" + first_0_str, 2)

    return min(
        [bin(seq_int ^ first_1_int).count("1"), bin(seq_int ^ first_0_int).count("1")]
    )


class TestFirstRepeatedNumber(unittest.TestCase):
    def test_first_repeated_number_functional(self):
        for seq, min_number in [
            # [0, (1), (0), 1, 0]
            ([0, 0, 1, 1, 0], 2),
            # [(1), 0, (1), 0, 1, (0), 1, (0)] OR [0, (1), 0, (1), 1, (0), 1, (0)]
            ([0, 0, 0, 0, 1, 1, 1, 1], 4,),
            ([1], 0),
        ]:
            with self.subTest(sequnce=seq, expected=min_number):
                self.assertEqual(count_number_of_changes(seq), min_number)
