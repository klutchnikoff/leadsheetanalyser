"""
Tests for the leadsheetanalyser.chords module.
"""
import unittest
import fractions
import numpy as np
from leadsheetanalyser.chords import (
    map_root, map_kind, map_chord, chord_nice_name,
    chord_name_to_tuple, chord_to_pitch_classes,
    pitch_classes_to_chord, transpose_chord, transpose_to_c,
    parse_shorthand_chord, to_note_list, key_retriever,
    closest_fraction
)
from tests.conftest import TEST_CHORDS, EXPECTED_CHORD_PITCH_CLASSES


class TestChords(unittest.TestCase):
    """Test chord processing functionality."""
    
    def test_map_root(self):
        """Test root note mapping."""
        self.assertEqual(map_root('C'), 0)
        self.assertEqual(map_root('D'), 2)
        self.assertEqual(map_root('F#'), 6)
        self.assertEqual(map_root('Bb'), 10)
        self.assertIsNone(map_root('Invalid'))
    
    def test_map_kind(self):
        """Test chord kind mapping."""
        # Test basic major chord
        maj_result = map_kind('maj')
        self.assertIsInstance(maj_result, list)
        self.assertEqual(len(maj_result), 11)
        
        # Test minor chord
        min_result = map_kind('min')
        self.assertIsInstance(min_result, list)
        self.assertEqual(len(min_result), 11)
        
        # Results should be different
        self.assertNotEqual(maj_result, min_result)
    
    def test_map_chord_harte_notation(self):
        """Test chord mapping with Harte notation."""
        # Test C major
        c_maj = map_chord('C:maj')
        self.assertIsInstance(c_maj, list)
        self.assertEqual(len(c_maj), 12)  # root + 11 interval values
        self.assertEqual(c_maj[0], 0)  # Root should be C (0)
        
        # Test A minor
        a_min = map_chord('A:min')
        self.assertEqual(a_min[0], 9)  # Root should be A (9)
    
    def test_map_chord_shorthand_notation(self):
        """Test chord mapping with shorthand notation."""
        # Test shorthand parsing
        am_shorthand = map_chord('Am')
        am_harte = map_chord('A:min')
        self.assertEqual(am_shorthand, am_harte)
        
        # Test C7
        c7_shorthand = map_chord('C7')
        c7_harte = map_chord('C:7')
        self.assertEqual(c7_shorthand, c7_harte)
    
    def test_parse_shorthand_chord(self):
        """Test shorthand chord parsing."""
        self.assertEqual(parse_shorthand_chord('Am'), ('A', 'min'))
        self.assertEqual(parse_shorthand_chord('C7'), ('C', '7'))
        self.assertEqual(parse_shorthand_chord('Dmaj7'), ('D', 'maj7'))
        self.assertEqual(parse_shorthand_chord('F#m'), ('F#', 'min'))
        
        # Test non-shorthand - function handles it by parsing root and kind
        result = parse_shorthand_chord('C:maj')
        self.assertEqual(result, ('C', 'maj'))  # Parses the colon as part of kind
    
    def test_chord_name_to_tuple(self):
        """Test chord name to tuple conversion."""
        # Test with Harte notation
        root, kind_vec = chord_name_to_tuple('C:maj')
        self.assertEqual(root, 0)
        self.assertIsInstance(kind_vec, np.ndarray)
        self.assertEqual(len(kind_vec), 11)
        
        # Test with shorthand
        root_short, kind_vec_short = chord_name_to_tuple('Am')
        self.assertEqual(root_short, 9)
        self.assertEqual(len(kind_vec_short), 11)
    
    def test_chord_to_pitch_classes(self):
        """Test chord to pitch classes conversion."""
        # Test C major chord (intervals: 3rd and 5th = positions 3 and 6 in 0-indexed)
        c_maj_kind = [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]  # Major 3rd and perfect 5th
        c_maj_pcs = chord_to_pitch_classes(0, c_maj_kind)
        expected_c_maj = {0, 4, 7}  # C, E, G
        self.assertEqual(c_maj_pcs, expected_c_maj)
        
        # Test with actual chord data from chord_name_to_tuple
        root, kind_vec = chord_name_to_tuple('C:maj')
        pcs = chord_to_pitch_classes(root, kind_vec)
        self.assertIsInstance(pcs, set)
        self.assertIn(0, pcs)  # Should contain root (C)
    
    def test_transpose_chord(self):
        """Test chord transposition."""
        # Test C major to D major (transpose by 2)
        c_maj = map_chord('C:maj')
        d_maj_expected = map_chord('D:maj')
        d_maj_transposed = transpose_chord(c_maj, 2)
        
        # Root should be transposed
        self.assertEqual(d_maj_transposed[0], 2)  # D
        self.assertEqual(d_maj_expected[0], 2)
        
        # Kind vector should be the same
        self.assertEqual(d_maj_transposed[1:], d_maj_expected[1:])
    
    def test_transpose_to_c(self):
        """Test transposing chords to C."""
        # Test with D major (need a list of chords and key)
        d_maj = map_chord('D:maj')
        chord_progression = [d_maj]
        key_name = 2  # D major
        
        c_maj_from_d = transpose_to_c(chord_progression, key_name)
        c_maj_direct = map_chord('C:maj')
        
        # Should be equivalent to C major
        self.assertEqual(c_maj_from_d[0][1:], c_maj_direct[1:])  # Kind vectors should match
        self.assertEqual(c_maj_from_d[0][0], 0)  # Root should be C
    
    def test_chord_nice_name(self):
        """Test chord nice name generation."""
        c_maj = map_chord('C:maj')
        nice_name = chord_nice_name(tuple(c_maj))
        self.assertIsInstance(nice_name, str)
        self.assertTrue(len(nice_name) > 0)
    
    def test_key_retriever(self):
        """Test key retrieval from key signatures."""
        # Test major keys
        self.assertEqual(key_retriever('C:major'), 0)
        self.assertEqual(key_retriever('D:major'), 2)
        
        # Test minor keys (returns the root note, not relative major)
        self.assertEqual(key_retriever('A:minor'), 9)  # A minor -> A (9)
        self.assertEqual(key_retriever('B:minor'), 11)  # B minor -> B (11)
    
    def test_to_note_list(self):
        """Test conversion to note list."""
        # Test with simple chord
        c_maj = map_chord('C:maj')
        note_list = to_note_list(c_maj)
        self.assertIsInstance(note_list, list)
        self.assertTrue(len(note_list) >= 3)  # At least 3 notes for major triad
        
        # Check that all elements are integers (pitch classes, not note names)
        for note in note_list:
            self.assertIsInstance(note, int)
            self.assertGreaterEqual(note, 0)
            self.assertLessEqual(note, 11)
    
    def test_closest_fraction(self):
        """Test closest fraction approximation."""
        # Test simple cases (function only takes one argument)
        result = closest_fraction(0.5)
        self.assertIsInstance(result, fractions.Fraction)
        self.assertEqual(result, fractions.Fraction(1, 2))
        
        result = closest_fraction(0.33333)
        self.assertIsInstance(result, fractions.Fraction)
        self.assertEqual(result, fractions.Fraction(1, 3))
        
        result = closest_fraction(0.75)
        self.assertIsInstance(result, fractions.Fraction)
        self.assertEqual(result, fractions.Fraction(3, 4))
    
    def test_pitch_classes_to_chord(self):
        """Test converting pitch classes back to chord representation."""
        # Test with known pitch classes
        c_maj_pcs = {0, 4, 7}  # C, E, G
        root = 0  # C
        chord_rep = pitch_classes_to_chord(c_maj_pcs, root)
        self.assertIsInstance(chord_rep, np.ndarray)
        self.assertEqual(len(chord_rep), 11)
        
        # Should have 1s in positions corresponding to intervals (3rd and 5th)
        # Interval 4 (major 3rd) should be at index 3, interval 7 (perfect 5th) at index 6
        self.assertEqual(chord_rep[3], 1)  # Major 3rd
        self.assertEqual(chord_rep[6], 1)  # Perfect 5th


if __name__ == '__main__':
    unittest.main()
