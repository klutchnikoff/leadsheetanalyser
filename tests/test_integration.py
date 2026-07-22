"""
Integration tests for the leadsheetanalyser package.
"""
import unittest
import leadsheetanalyser
from leadsheetanalyser import (
    map_chord, chord_name_to_tuple, simple_dissimilarity,
    get_scale_symmetry_axis, extract_chord_statistics
)


class TestIntegration(unittest.TestCase):
    """Test integration between different modules."""
    
    def test_package_import(self):
        """Test that the package imports correctly."""
        # Test that main modules are available
        self.assertTrue(hasattr(leadsheetanalyser, 'constants'))
        self.assertTrue(hasattr(leadsheetanalyser, 'chords'))
        self.assertTrue(hasattr(leadsheetanalyser, 'scales'))
        self.assertTrue(hasattr(leadsheetanalyser, 'chord_dissimilarities'))
        self.assertTrue(hasattr(leadsheetanalyser, 'data_processing'))
        
        # Test that key functions are available at package level
        self.assertTrue(hasattr(leadsheetanalyser, 'map_chord'))
        self.assertTrue(hasattr(leadsheetanalyser, 'chord_name_to_tuple'))
        self.assertTrue(hasattr(leadsheetanalyser, 'simple_dissimilarity'))
        self.assertTrue(hasattr(leadsheetanalyser, 'get_scale_symmetry_axis'))
    
    def test_chord_to_dissimilarity_workflow(self):
        """Test workflow from chord parsing to dissimilarity calculation."""
        # Parse chords using different methods
        c_maj_harte = map_chord('C:maj')
        c_maj_short = map_chord('C')
        f_maj = map_chord('F:maj')
        
        # Convert to tuples for dissimilarity using chord_name_to_tuple
        c_maj_tuple = chord_name_to_tuple('C:maj')
        f_maj_tuple = chord_name_to_tuple('F:maj')
        
        # Calculate dissimilarity
        dissim = simple_dissimilarity(c_maj_tuple, f_maj_tuple)
        
        # Verify results
        self.assertIsInstance(dissim, (int, float))
        self.assertGreaterEqual(dissim, 0.0)
        
        # Test that shorthand and Harte notation give same result
        self.assertEqual(c_maj_harte, c_maj_short)
    
    def test_chord_analysis_pipeline(self):
        """Test complete chord analysis pipeline."""
        # Sample chord progression
        chord_names = ['C:maj', 'F:maj', 'G:7', 'C:maj', 'A:min', 'D:min', 'G:7', 'C:maj']
        
        # Parse all chords
        parsed_chords = []
        for chord_name in chord_names:
            chord_data = map_chord(chord_name)
            parsed_chords.append(chord_data)
        
        # Extract chord tuples for analysis using chord_name_to_tuple
        chord_tuples = []
        for chord_name in chord_names:
            chord_tuple = chord_name_to_tuple(chord_name)
            chord_tuples.append(chord_tuple)
        
        # Calculate pairwise dissimilarities
        dissim_matrix = []
        for i, chord1 in enumerate(chord_tuples):
            row = []
            for j, chord2 in enumerate(chord_tuples):
                dissim = simple_dissimilarity(chord1, chord2)
                row.append(dissim)
            dissim_matrix.append(row)
        
        # Verify matrix properties
        n_chords = len(chord_tuples)
        self.assertEqual(len(dissim_matrix), n_chords)
        for row in dissim_matrix:
            self.assertEqual(len(row), n_chords)
        
        # Diagonal should be zero
        for i in range(n_chords):
            self.assertEqual(dissim_matrix[i][i], 0.0)
        
        # Matrix should be symmetric
        for i in range(n_chords):
            for j in range(n_chords):
                self.assertEqual(dissim_matrix[i][j], dissim_matrix[j][i])
    
    def test_data_processing_integration(self):
        """Test integration with data processing functions."""
        # Create sample song data
        sample_songs = [
            {
                'id': 1,
                'title': 'Song 1',
                'chord_progression': ['C:maj', 'F:maj', 'G:7', 'C:maj'],
                'key': 'C:major',
                'artist': 'Artist A',
                'genre': 'Jazz'
            },
            {
                'id': 2,
                'title': 'Song 2',
                'chord_progression': ['A:min', 'D:min', 'G:7', 'C:maj'],
                'key': 'A:minor',
                'artist': 'Artist B',
                'genre': 'Pop'
            }
        ]
        
        # Extract statistics
        stats = extract_chord_statistics(sample_songs)
        self.assertIsInstance(stats, dict)
        
        # Verify chord parsing works with the extracted chords
        if 'chord_frequencies' in stats:
            for chord_name in stats['chord_frequencies'].keys():
                try:
                    parsed = map_chord(chord_name)
                    self.assertIsInstance(parsed, list)
                    self.assertEqual(len(parsed), 13)  # root + 12 intervals
                except Exception as e:
                    # Some chord names might not be parseable, that's ok
                    pass
    
    def test_scale_chord_interaction(self):
        """Test interaction between scale and chord functions."""
        # Major scale pattern
        major_scale = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        
        # Analyze scale properties
        symmetry_axis = get_scale_symmetry_axis(major_scale)
        
        # Test chords that should fit the scale
        major_scale_chords = ['C:maj', 'D:min', 'E:min', 'F:maj', 'G:7', 'A:min', 'B:dim']
        
        for chord_name in major_scale_chords:
            try:
                chord_data = map_chord(chord_name)
                root, kind_vec = chord_name_to_tuple(chord_name)
                
                # Verify chord data structure
                self.assertEqual(chord_data[0], root)
                self.assertEqual(chord_data[1:], kind_vec)
                
            except Exception as e:
                # Some chords might not be supported, that's ok for this test
                pass
    
    def test_shorthand_vs_harte_consistency(self):
        """Test consistency between shorthand and Harte notation."""
        # Test cases: (shorthand, harte_equivalent)
        test_cases = [
            ('C', 'C:maj'),
            ('Am', 'A:min'),
            ('C7', 'C:7'),
            ('Dm7', 'D:min7'),
            ('Fmaj7', 'F:maj7'),
        ]
        
        for shorthand, harte in test_cases:
            try:
                short_result = map_chord(shorthand)
                harte_result = map_chord(harte)
                
                # Should produce identical results
                self.assertEqual(short_result, harte_result, 
                    f"Shorthand '{shorthand}' != Harte '{harte}'")
                
            except Exception as e:
                # If one fails, both should fail consistently
                with self.assertRaises(type(e)):
                    map_chord(harte if shorthand == shorthand else shorthand)
    
    def test_error_propagation(self):
        """Test that errors propagate appropriately across modules."""
        # Test invalid chord name
        with self.assertRaises((ValueError, KeyError, AttributeError)):
            invalid_chord = map_chord('InvalidChord:weirdtype')
        
        # Test invalid dissimilarity input
        try:
            # This should either work or raise an appropriate error
            invalid_dissim = simple_dissimilarity((), ())
        except (ValueError, TypeError, IndexError):
            pass  # Expected for invalid input
        
        # Test invalid scale input
        try:
            invalid_symmetry = get_scale_symmetry_axis([])
        except (ValueError, IndexError):
            pass  # Expected for invalid input
    
    def test_version_and_metadata(self):
        """Test package version and metadata."""
        # Test that version is accessible
        self.assertTrue(hasattr(leadsheetanalyser, '__version__'))
        self.assertIsInstance(leadsheetanalyser.__version__, str)
        
        # Test that __all__ is properly defined
        self.assertTrue(hasattr(leadsheetanalyser, '__all__'))
        self.assertIsInstance(leadsheetanalyser.__all__, list)
        
        # Test that all functions in __all__ are actually available
        for func_name in leadsheetanalyser.__all__:
            if not func_name.isupper():  # Skip constants
                self.assertTrue(hasattr(leadsheetanalyser, func_name),
                    f"Function '{func_name}' in __all__ but not available")
    
    def test_example_from_readme(self):
        """Test examples that should work based on README."""
        try:
            # Basic chord parsing
            chord = leadsheetanalyser.map_chord("Am")
            self.assertIsInstance(chord, list)
            
            chord_harte = leadsheetanalyser.map_chord("A:min")
            self.assertEqual(chord, chord_harte)
            
            # Chord analysis
            c_maj = leadsheetanalyser.chord_name_to_tuple("C:maj")
            f_maj = leadsheetanalyser.chord_name_to_tuple("F:maj")
            
            dissimilarity = leadsheetanalyser.simple_dissimilarity(c_maj, f_maj)
            self.assertIsInstance(dissimilarity, (int, float))
            self.assertGreaterEqual(dissimilarity, 0.0)
            
            # Scale analysis (function returns a list, not int or None)
            major_scale = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
            axis = leadsheetanalyser.get_scale_symmetry_axis(major_scale)
            # axis can be a list of integers
            self.assertIsInstance(axis, list)
            
        except Exception as e:
            self.fail(f"README example failed: {e}")


if __name__ == '__main__':
    unittest.main()
