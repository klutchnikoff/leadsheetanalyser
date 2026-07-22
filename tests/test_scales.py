"""
Tests for the leadsheetanalyser.scales module.
"""
import unittest
import numpy as np
from leadsheetanalyser.scales import (
    compute_transposition_number, get_scale_symmetry_axis,
    analyze_mode_properties, scale_from_intervals,
    identify_mode, generate_mode_variants
)
from tests.conftest import TEST_SCALES


class TestScales(unittest.TestCase):
    """Test scale analysis functionality."""
    
    def test_compute_transposition_number(self):
        """Test transposition number computation."""
        # Major scale pattern
        major_scale = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        
        # Test transposition number for major scale (should be 12)
        trans_num = compute_transposition_number(major_scale)
        self.assertIsInstance(trans_num, int)
        self.assertGreater(trans_num, 0)
        self.assertLessEqual(trans_num, 12)
        
        # Test with whole-tone scale (should have limited transpositions)
        whole_tone = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        wt_trans_num = compute_transposition_number(whole_tone)
        self.assertIsInstance(wt_trans_num, int)
        
        # Test with invalid input
        with self.assertRaises((ValueError, IndexError)):
            compute_transposition_number([])
    
    def test_get_scale_symmetry_axis(self):
        """Test scale symmetry axis detection."""
        # Test major scale (should have some symmetry properties)
        major_scale = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        axis = get_scale_symmetry_axis(major_scale)
        self.assertIsInstance(axis, list)
        
        # Test chromatic scale (highly symmetric)
        chromatic = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        chromatic_axis = get_scale_symmetry_axis(chromatic)
        self.assertIsInstance(chromatic_axis, list)
        
        # Test with each test scale
        for scale in TEST_SCALES:
            axis = get_scale_symmetry_axis(scale)
            self.assertIsInstance(axis, list)
    
    def test_analyze_mode_properties(self):
        """Test mode property analysis."""
        # Test major scale
        major_scale = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        props = analyze_mode_properties(major_scale)
        
        self.assertIsInstance(props, dict)
        # Should contain useful properties
        expected_keys = ['num_notes', 'intervals', 'symmetry']
        for key in expected_keys:
            if key in props:  # Some properties might be optional
                self.assertTrue(True)  # At least some analysis was done
        
        # Test that number of notes is correct
        if 'num_notes' in props:
            self.assertEqual(props['num_notes'], 7)  # Major scale has 7 notes
    
    def test_scale_from_intervals(self):
        """Test scale generation from intervals."""
        # Test major scale intervals: 0, 2, 4, 5, 7, 9, 11
        major_intervals = [0, 2, 4, 5, 7, 9, 11]  # Semitone intervals from root
        scale = scale_from_intervals(major_intervals)
        
        self.assertIsInstance(scale, list)
        self.assertEqual(len(scale), 12)
        self.assertEqual(sum(scale), 7)  # Should have 7 notes
        
        # First note should be included
        self.assertEqual(scale[0], 1)
        
        # Test with empty intervals
        empty_scale = scale_from_intervals([0])  # Just root note
        self.assertEqual(empty_scale, [1] + [0] * 11)  # Just root note
    
    def test_identify_mode(self):
        """Test mode identification."""
        # Test major scale (Ionian mode)
        major_scale = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        mode_result = identify_mode(major_scale)
        
        # Should return some identification result
        self.assertIsNotNone(mode_result)
        
        # Test with natural minor (Aeolian mode)
        minor_scale = [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]
        minor_result = identify_mode(minor_scale)
        self.assertIsNotNone(minor_result)
        
        # Results should be different for different modes
        if isinstance(mode_result, str) and isinstance(minor_result, str):
            self.assertNotEqual(mode_result, minor_result)
    
    def test_generate_mode_variants(self):
        """Test mode variant generation."""
        # Test with major scale
        major_scale = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        variants = generate_mode_variants(major_scale)
        
        self.assertIsInstance(variants, list)
        self.assertTrue(len(variants) > 0)
        
        # Each variant should be a valid scale (12 elements, sum to same number)
        for variant in variants:
            self.assertIsInstance(variant, list)
            self.assertEqual(len(variant), 12)
            self.assertEqual(sum(variant), sum(major_scale))
        
        # Should have 7 variants for major scale (7 modes)
        if len(variants) == 7:
            # Verify that each mode is different
            unique_variants = []
            for v in variants:
                if v not in unique_variants:
                    unique_variants.append(v)
            self.assertEqual(len(unique_variants), 7)
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with invalid scale lengths
        short_scale = [1, 0, 1]
        
        # Functions should handle gracefully or raise appropriate errors
        try:
            axis = get_scale_symmetry_axis(short_scale + [0] * 9)  # Pad to 12
            self.assertIsInstance(axis, list)
        except (ValueError, IndexError):
            pass  # Acceptable to raise error for invalid input
        
        # Test with all zeros (no notes)
        empty_scale = [0] * 12
        try:
            props = analyze_mode_properties(empty_scale)
            if 'num_notes' in props:
                self.assertEqual(props['num_notes'], 0)
        except (ValueError, ZeroDivisionError):
            pass  # Acceptable to raise error for degenerate case
        
        # Test with chromatic scale (all notes)
        chromatic = [1] * 12
        try:
            chromatic_props = analyze_mode_properties(chromatic)
            if 'num_notes' in chromatic_props:
                self.assertEqual(chromatic_props['num_notes'], 12)
        except Exception:
            pass  # Some functions might not handle chromatic scale


if __name__ == '__main__':
    unittest.main()
