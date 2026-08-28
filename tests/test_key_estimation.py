"""Tests for chord-based key estimation."""

import unittest

import numpy as np

from leadsheetanalyser.key_estimation import estimate_key_from_chords


def kind(*intervals):
    out = np.zeros(11, dtype=int)
    for interval in intervals:
        out[interval - 1] = 1
    return out


class TestKeyEstimation(unittest.TestCase):
    def test_c_major_cadence(self):
        major = kind(4, 7)
        progression = [(0, major), (5, major), (7, major), (0, major)]
        tonic, mode, correlation = estimate_key_from_chords(progression)
        self.assertEqual((tonic, mode), (0, "major"))
        self.assertGreater(correlation, 0)

    def test_flat_and_root_kind_representations_agree(self):
        major = kind(4, 7)
        paired = [(0, major), (5, major), (7, major), (0, major)]
        flat = [[root, *chord_kind] for root, chord_kind in paired]
        self.assertEqual(
            estimate_key_from_chords(paired),
            estimate_key_from_chords(flat),
        )

    def test_invalid_events_do_not_count_towards_minimum(self):
        major = kind(4, 7)
        self.assertIsNone(
            estimate_key_from_chords([(0, major), None, [0, 1]], minimum_chords=2)
        )

    def test_minimum_must_be_positive(self):
        with self.assertRaises(ValueError):
            estimate_key_from_chords([], minimum_chords=0)


if __name__ == "__main__":
    unittest.main()
