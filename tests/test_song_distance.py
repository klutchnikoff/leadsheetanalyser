import unittest
import numpy as np
from leadsheetanalyser.chord_dissimilarities import create_identity_system
from leadsheetanalyser.song_distance import ground_cost_matrix, song_distance, _reinterpretations, _embed
from leadsheetanalyser.chords import chord_name_to_tuple

class TestSongDistance(unittest.TestCase):
    def setUp(self):
        self.c_maj = chord_name_to_tuple('C:maj')
        self.f_maj = chord_name_to_tuple('F:maj')
        self.g_dom7 = chord_name_to_tuple('G:7')
        self.system = create_identity_system()
        
    def test_reinterpretations(self):
        chords = [self.c_maj, self.f_maj]
        R = _reinterpretations(chords)
        self.assertEqual(R.shape, (2, 12, 11))
        
    def test_embed(self):
        chords = [self.c_maj]
        R = _reinterpretations(chords).astype(float)
        emb_linear = _embed(R, self.system, mode="linear")
        emb_angular = _embed(R, self.system, mode="angular")
        self.assertEqual(emb_linear.shape, (1, 12, 11))
        self.assertEqual(emb_angular.shape, (1, 12, 11))
        
    def test_ground_cost_matrix_vectorized(self):
        chords_a = [self.c_maj, self.f_maj]
        chords_b = [self.g_dom7, self.c_maj]
        
        # p = 1.0
        M1 = ground_cost_matrix(chords_a, chords_b, W=self.system, p=1.0)
        self.assertEqual(M1.shape, (2, 2))
        
        # p = inf
        Minf = ground_cost_matrix(chords_a, chords_b, W=self.system, p=float('inf'))
        self.assertEqual(Minf.shape, (2, 2))
        
    def test_song_distance(self):
        song1 = [self.c_maj, self.f_maj, self.c_maj]
        song2 = [self.g_dom7, self.c_maj]
        
        dist = song_distance(song1, song2, W=self.system, p=1.0)
        self.assertIsInstance(dist, float)
        self.assertGreaterEqual(dist, 0.0)

if __name__ == '__main__':
    unittest.main()
