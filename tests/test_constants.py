"""
Tests for the leadsheetanalyser.constants module.
"""
import unittest
from leadsheetanalyser.constants import (
    NOTE_TO_PC, PC_TO_NOTE_FLAT, PC_TO_NOTE_SHARP,
    CHORD_SHORTHANDS, SIMPLIFIED_CHORD_NAMES,
    W_DIATONIC, DIATONIC_MODE_NAMES,
    W_MESSIAEN, MESSIAEN_MODE_NAMES
)


class TestConstants(unittest.TestCase):
    """Test constants module functionality."""
    
    def test_note_to_pc_mapping(self):
        """Test NOTE_TO_PC constant mappings."""
        # Test basic notes
        self.assertEqual(NOTE_TO_PC['C'], 0)
        self.assertEqual(NOTE_TO_PC['D'], 2)
        self.assertEqual(NOTE_TO_PC['E'], 4)
        self.assertEqual(NOTE_TO_PC['F'], 5)
        self.assertEqual(NOTE_TO_PC['G'], 7)
        self.assertEqual(NOTE_TO_PC['A'], 9)
        self.assertEqual(NOTE_TO_PC['B'], 11)
        
        # Test sharps
        self.assertEqual(NOTE_TO_PC['C#'], 1)
        self.assertEqual(NOTE_TO_PC['F#'], 6)
        
        # Test flats
        self.assertEqual(NOTE_TO_PC['Bb'], 10)
        self.assertEqual(NOTE_TO_PC['Ab'], 8)
    
    def test_pc_to_note_mappings(self):
        """Test PC_TO_NOTE mappings."""
        # Test flat notation
        self.assertEqual(PC_TO_NOTE_FLAT[0], 'C')
        self.assertEqual(PC_TO_NOTE_FLAT[1], 'Db')
        self.assertEqual(PC_TO_NOTE_FLAT[11], 'B')
        
        # Test sharp notation
        self.assertEqual(PC_TO_NOTE_SHARP[0], 'C')
        self.assertEqual(PC_TO_NOTE_SHARP[1], 'C#')
        self.assertEqual(PC_TO_NOTE_SHARP[11], 'B')
    
    def test_chord_shorthands(self):
        """Test chord shorthand mappings."""
        # These are interval tuples, not string mappings
        self.assertIn('maj', CHORD_SHORTHANDS)
        self.assertIn('min', CHORD_SHORTHANDS) 
        self.assertIn('7', CHORD_SHORTHANDS)
        self.assertIn('maj7', CHORD_SHORTHANDS)
        
        # Test that chord types map to interval tuples
        self.assertEqual(CHORD_SHORTHANDS['maj'], (4, 7))
        self.assertEqual(CHORD_SHORTHANDS['min'], (3, 7))
        self.assertEqual(CHORD_SHORTHANDS['7'], (4, 7, 10))
        self.assertEqual(CHORD_SHORTHANDS['maj7'], (4, 7, 11))
    
    def test_diatonic_constants(self):
        """Test Diatonic mode constants."""
        # W_DIATONIC should be a list of 7 elements
        self.assertEqual(len(W_DIATONIC), 7)
        # Elements are numpy arrays with fractions
        self.assertTrue(all(hasattr(x, '__len__') for x in W_DIATONIC))
        
        # DIATONIC_MODE_NAMES should have 7 names
        self.assertEqual(len(DIATONIC_MODE_NAMES), 7)
        self.assertIn('Ionian', DIATONIC_MODE_NAMES)
        self.assertIn('Dorian', DIATONIC_MODE_NAMES)
    
    def test_messiaen_constants(self):
        """Test Messiaen mode constants."""
        # W_MESSIAEN should be a numpy array with 15 elements (modes)
        self.assertEqual(len(W_MESSIAEN), 15)
        self.assertTrue(all(hasattr(mode, '__len__') for mode in W_MESSIAEN))
        
        # MESSIAEN_MODE_NAMES should have 15 names  
        self.assertEqual(len(MESSIAEN_MODE_NAMES), 15)
        self.assertIn('Mode 1 (whole-tone)', MESSIAEN_MODE_NAMES)


if __name__ == '__main__':
    unittest.main()
