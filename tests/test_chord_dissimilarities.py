"""
Tests for the leadsheetanalyser.chord_dissimilarities module.
"""
import unittest
import numpy as np
from leadsheetanalyser.chord_dissimilarities import (
    reinterpret_chord, modal_dissimilarity, simple_dissimilarity,
    tonal_dissimilarity, chord_name_to_tuple, modal_embedding,
    create_identity_system, create_tonal_system, modal_profile
)
from leadsheetanalyser.chords import map_chord


class TestChordDissimilarities(unittest.TestCase):
    """Test chord dissimilarity functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Get chord tuples in the correct format for dissimilarity functions
        self.c_maj_root, self.c_maj_kind = chord_name_to_tuple('C:maj')
        self.f_maj_root, self.f_maj_kind = chord_name_to_tuple('F:maj')
        self.a_min_root, self.a_min_kind = chord_name_to_tuple('A:min')
        self.g_dom7_root, self.g_dom7_kind = chord_name_to_tuple('G:7')
        
        # Create tuples for dissimilarity functions
        self.c_maj_tuple = (self.c_maj_root, self.c_maj_kind)
        self.f_maj_tuple = (self.f_maj_root, self.f_maj_kind)
        self.a_min_tuple = (self.a_min_root, self.a_min_kind)
        self.g_dom7_tuple = (self.g_dom7_root, self.g_dom7_kind)
    
    def test_chord_name_to_tuple(self):
        """Test chord name to tuple conversion (dissimilarity version)."""
        # Test with Harte notation
        root, kind_vec = chord_name_to_tuple('C:maj')
        self.assertEqual(root, 0)
        self.assertIsInstance(kind_vec, np.ndarray)
        self.assertEqual(len(kind_vec), 11)
        
        # Test with different chord types
        root_min, kind_vec_min = chord_name_to_tuple('A:min')
        self.assertEqual(root_min, 9)
        self.assertFalse(np.array_equal(kind_vec, kind_vec_min))  # Different chord types
    
    def test_simple_dissimilarity(self):
        """Test simple dissimilarity calculation."""
        # Test identity (chord with itself)
        identity_dissim = simple_dissimilarity(self.c_maj_tuple, self.c_maj_tuple)
        self.assertEqual(identity_dissim, 0.0)
        
        # Test different chords
        c_f_dissim = simple_dissimilarity(self.c_maj_tuple, self.f_maj_tuple)
        self.assertGreater(c_f_dissim, 0.0)
        self.assertIsInstance(c_f_dissim, (int, float))
        
        # Test symmetry (distance should be symmetric)
        f_c_dissim = simple_dissimilarity(self.f_maj_tuple, self.c_maj_tuple)
        self.assertEqual(c_f_dissim, f_c_dissim)
        
        # Test with major vs minor
        c_a_dissim = simple_dissimilarity(self.c_maj_tuple, self.a_min_tuple)
        self.assertGreater(c_a_dissim, 0.0)
    
    def test_tonal_dissimilarity(self):
        """Test tonal dissimilarity calculation."""
        # Test identity
        identity_tonal = tonal_dissimilarity(self.c_maj_tuple, self.c_maj_tuple)
        self.assertEqual(identity_tonal, 0.0)
        
        # Test different chords
        c_f_tonal = tonal_dissimilarity(self.c_maj_tuple, self.f_maj_tuple)
        self.assertGreaterEqual(c_f_tonal, 0.0)
        self.assertIsInstance(c_f_tonal, (int, float))
        
        # Test symmetry
        f_c_tonal = tonal_dissimilarity(self.f_maj_tuple, self.c_maj_tuple)
        self.assertEqual(c_f_tonal, f_c_tonal)
        
        # Tonal dissimilarity might be different from simple dissimilarity
        c_f_simple = simple_dissimilarity(self.c_maj_tuple, self.f_maj_tuple)
        # Both should be numeric types
        self.assertIsInstance(c_f_tonal, (int, float))
        self.assertIsInstance(c_f_simple, (int, float))
    
    def test_dissimilarities_function(self):
        """Test the main modal_dissimilarity function."""
        # Create identity system for testing
        identity_system = create_identity_system()
        
        # Test with two chords
        dissim_result = modal_dissimilarity(self.c_maj_tuple, self.f_maj_tuple, identity_system, p=1.0)
        
        # Should return a float
        self.assertIsInstance(dissim_result, float)
        self.assertGreaterEqual(dissim_result, 0.0)

    def test_modal_embedding(self):
        """Test the modal_embedding function."""
        identity_system = create_identity_system()
        emb_linear = modal_embedding(self.c_maj_kind, identity_system, mode="linear")
        self.assertEqual(emb_linear.shape, (11,))
        
        emb_angular = modal_embedding(self.c_maj_kind, identity_system, mode="angular")
        self.assertEqual(emb_angular.shape, (11,))
        self.assertAlmostEqual(np.linalg.norm(emb_angular), 1.0)
        
    def test_modal_dissimilarity_p_norm(self):
        """Test the modal_dissimilarity with different p norms."""
        sys = create_identity_system()
        
        d1 = modal_dissimilarity(self.c_maj_tuple, self.f_maj_tuple, sys, p=1.0)
        d2 = modal_dissimilarity(self.c_maj_tuple, self.f_maj_tuple, sys, p=2.0)
        d_inf = modal_dissimilarity(self.c_maj_tuple, self.f_maj_tuple, sys, p=float('inf'))
        
        self.assertGreaterEqual(d1, d2)
        self.assertGreaterEqual(d2, d_inf)
    
    def test_reinterpret_chord(self):
        """Test chord reinterpretation functionality."""
        # Test basic reinterpretation (reinterpreting C major chord with different roots)
        old_root = 0  # C
        new_root = 2  # D
        reinterpreted = reinterpret_chord(self.c_maj_kind, old_root, new_root)
        
        # Should return a valid chord kind vector
        self.assertIsInstance(reinterpreted, np.ndarray)
        
        # Should have same length as original
        self.assertEqual(len(reinterpreted), len(self.c_maj_kind))
        
        # Test with different chord types
        reinterpreted_min = reinterpret_chord(self.a_min_kind, 9, 0)
        self.assertIsInstance(reinterpreted_min, np.ndarray)
    
    def test_create_identity_system(self):
        """Test identity system creation."""
        identity_system = create_identity_system()
        
        # Should return some system representation
        self.assertIsNotNone(identity_system)
        
        # Should be a numpy array
        self.assertIsInstance(identity_system, np.ndarray)
    
    def test_create_tonal_system(self):
        """Test tonal system creation."""
        tonal_system = create_tonal_system()
        
        # Should return some system representation
        self.assertIsNotNone(tonal_system)
        
        # Should be a numpy array
        self.assertIsInstance(tonal_system, np.ndarray)
        
        # Might be different from identity system
        identity_system = create_identity_system()
        # They might be equal or different depending on implementation
        self.assertEqual(type(tonal_system), type(identity_system))
    
    def test_dissimilarity_properties(self):
        """Test mathematical properties of dissimilarity measures."""
        test_chords = [
            self.c_maj_tuple, self.f_maj_tuple, 
            self.a_min_tuple, self.g_dom7_tuple
        ]
        
        for i, chord1 in enumerate(test_chords):
            for j, chord2 in enumerate(test_chords):
                simple_dist = simple_dissimilarity(chord1, chord2)
                tonal_dist = tonal_dissimilarity(chord1, chord2)
                
                # Non-negativity
                self.assertGreaterEqual(simple_dist, 0.0)
                self.assertGreaterEqual(tonal_dist, 0.0)
                
                # Identity
                if i == j:
                    self.assertEqual(simple_dist, 0.0)
                    self.assertEqual(tonal_dist, 0.0)
                
                # Symmetry
                simple_dist_rev = simple_dissimilarity(chord2, chord1)
                tonal_dist_rev = tonal_dissimilarity(chord2, chord1)
                self.assertEqual(simple_dist, simple_dist_rev)
                self.assertEqual(tonal_dist, tonal_dist_rev)
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with identical chords
        same_chord_dissim = simple_dissimilarity(self.c_maj_tuple, self.c_maj_tuple)
        self.assertEqual(same_chord_dissim, 0.0)
        
        # Test with minimal chord tuples
        try:
            root = 0
            minimal_kind = np.zeros(11)  # No intervals, just root
            minimal_chord = (root, minimal_kind)
            minimal_dissim = simple_dissimilarity(minimal_chord, self.c_maj_tuple)
            self.assertGreaterEqual(minimal_dissim, 0.0)
        except (ValueError, TypeError, IndexError):
            pass  # Acceptable to raise error for edge case


if __name__ == '__main__':
    unittest.main()


class TestModalProfile(unittest.TestCase):
    """The power-mean reading of a chord kind, over its order p."""

    def setUp(self):
        from leadsheetanalyser.constants import W_DIATONIC, W_MESSIAEN
        self.W = np.vstack([np.asarray(W_DIATONIC, float),
                            np.asarray(W_MESSIAEN, float)[:2]])
        self.dom7 = self._kind(4, 7, 10)
        self.maj7 = self._kind(4, 7, 11)
        self.dim7 = self._kind(3, 6, 9)

    @staticmethod
    def _kind(*semitones):
        v = np.zeros(11, dtype=int)
        for s in semitones:
            v[s - 1] = 1
        return v

    def test_is_a_distribution(self):
        for p in (1.0, 0.5, 0.15, 0.0, -1.0):
            profile = modal_profile(self.dom7, self.W, p)
            self.assertAlmostEqual(float(profile.sum()), 1.0, places=12)
            self.assertTrue((profile >= 0).all())

    def test_order_one_is_the_normalised_coverage(self):
        """At p = 1 the mean is arithmetic: the weight the mode puts in the chord."""
        expected = self.W @ self.dom7
        expected = expected / expected.sum()
        np.testing.assert_allclose(modal_profile(self.dom7, self.W, 1.0),
                                   expected, atol=1e-12)

    def test_order_zero_is_the_geometric_mean(self):
        """At p = 0 a mode missing one interval of the chord is annihilated."""
        idx = np.flatnonzero(self.dim7)
        geometric = np.prod(self.W[:, idx], axis=1) ** (1.0 / len(idx))
        expected = geometric / geometric.sum()
        np.testing.assert_allclose(modal_profile(self.dim7, self.W, 0.0),
                                   expected, atol=1e-12)

    def test_half_order_ranks_like_the_hellinger_affinity(self):
        """M_{1/2} is the square of the Hellinger affinity: same order, not same value."""
        for kind in (self.dom7, self.maj7, self.dim7):
            hellinger = np.sqrt(self.W) @ kind
            np.testing.assert_array_equal(
                np.argsort(modal_profile(kind, self.W, 0.5)),
                np.argsort(hellinger))

    def test_sharpens_as_the_order_falls(self):
        tops = [modal_profile(self.dim7, self.W, p).max()
                for p in (1.0, 0.5, 0.2, 0.05)]
        self.assertEqual(tops, sorted(tops))

    def test_small_order_does_not_overflow(self):
        """The exponent 1/p reaches 33 at p = 0.03: the direct form would overflow."""
        profile = modal_profile(self.dom7, self.W, 0.03)
        self.assertTrue(np.isfinite(profile).all())
        self.assertAlmostEqual(float(profile.sum()), 1.0, places=12)

    def test_kind_without_intervals_has_no_profile(self):
        self.assertIsNone(modal_profile(np.zeros(11, dtype=int), self.W))

    def test_uncontained_kind_has_no_profile_at_order_zero(self):
        """Both sevenths at once: no mode of the system contains that kind."""
        both_sevenths = self._kind(4, 7, 10, 11)
        self.assertIsNone(modal_profile(both_sevenths, self.W, 0.0))
        self.assertIsNotNone(modal_profile(both_sevenths, self.W, 0.15))

    def test_batch_matches_one_by_one(self):
        kinds = np.array([self.dom7, self.maj7, self.dim7])
        batch = modal_profile(kinds, self.W, 0.15)
        self.assertEqual(batch.shape, (3, self.W.shape[0]))
        for row, kind in zip(batch, kinds):
            np.testing.assert_allclose(row, modal_profile(kind, self.W, 0.15),
                                       atol=1e-12)

    def test_batch_marks_unreadable_kinds_with_nan(self):
        kinds = np.array([self.dom7, np.zeros(11, dtype=int)])
        batch = modal_profile(kinds, self.W, 0.15)
        self.assertFalse(np.isnan(batch[0]).any())
        self.assertTrue(np.isnan(batch[1]).all())
