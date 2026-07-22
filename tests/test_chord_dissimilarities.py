"""
Tests for the leadsheetanalyser.chord_dissimilarities module.
"""
import unittest
import numpy as np
from leadsheetanalyser.chord_dissimilarities import (
    reinterpret_chord, modal_dissimilarity, simple_dissimilarity,
    tonal_dissimilarity, chord_name_to_tuple, modal_embedding,
    create_identity_system, create_tonal_system
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
