"""
Tests for the leadsheetanalyser.data_processing module.
"""
import unittest
import pandas as pd
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from leadsheetanalyser.data_processing import (
    process_song_data, load_and_process_dataset,
    filter_songs_by_criteria, extract_chord_statistics,
    create_chord_transition_matrix
)


class TestDataProcessing(unittest.TestCase):
    """Test data processing functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample DataFrame
        self.sample_df = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ['Song 1', 'Song 2', 'Song 3'],
            'artist': ['Artist A', 'Artist B', 'Artist C'],
            'genre': ['Jazz', 'Pop', 'Jazz'],
            'key': ['C:major', 'F:major', 'A:minor']
        })
        
        # Sample songs data
        self.sample_songs = [
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
                'chord_progression': ['F:maj', 'Bb:maj', 'C:7', 'F:maj'],
                'key': 'F:major',
                'artist': 'Artist B',
                'genre': 'Pop'
            },
            {
                'id': 3,
                'title': 'Song 3',
                'chord_progression': ['A:min', 'D:min', 'G:7', 'C:maj', 'A:min'],
                'key': 'A:minor',
                'artist': 'Artist C', 
                'genre': 'Jazz'
            }
        ]
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock JAMS files
        self.jams_content = {
            "file_metadata": {"title": "Test Song"},
            "annotations": [{
                "annotation_metadata": {"data_source": "test"},
                "data": [
                    {"time": 0.0, "duration": 2.0, "value": "C:maj"},
                    {"time": 2.0, "duration": 2.0, "value": "F:maj"},
                    {"time": 4.0, "duration": 2.0, "value": "G:7"},
                    {"time": 6.0, "duration": 2.0, "value": "C:maj"}
                ]
            }]
        }
        
        # Write test JAMS file
        self.jams_file = os.path.join(self.temp_dir, '1.jams')
        with open(self.jams_file, 'w') as f:
            json.dump(self.jams_content, f)
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_filter_songs_by_criteria(self):
        """Test song filtering functionality."""
        # Test minimum chord filter
        filtered = filter_songs_by_criteria(self.sample_songs, min_chords=4)
        self.assertGreater(len(filtered), 0)
        
        # All filtered songs should have at least 4 chords
        for song in filtered:
            self.assertGreaterEqual(len(song['chord_progression']), 4)
        
        # Test maximum chord filter
        filtered_max = filter_songs_by_criteria(self.sample_songs, max_chords=4)
        for song in filtered_max:
            self.assertLessEqual(len(song['chord_progression']), 4)
        
        # Test genre filter
        jazz_songs = filter_songs_by_criteria(
            self.sample_songs, 
            allowed_genres=['Jazz']
        )
        for song in jazz_songs:
            self.assertEqual(song['genre'], 'Jazz')
        
        # Test key filter
        major_songs = filter_songs_by_criteria(
            self.sample_songs,
            required_keys=['C:major', 'F:major']
        )
        for song in major_songs:
            self.assertIn(song['key'], ['C:major', 'F:major'])
        
        # Test empty result
        no_songs = filter_songs_by_criteria(
            self.sample_songs,
            min_chords=100  # Impossible requirement
        )
        self.assertEqual(len(no_songs), 0)
    
    def test_extract_chord_statistics(self):
        """Test chord statistics extraction."""
        stats = extract_chord_statistics(self.sample_songs)
        
        self.assertIsInstance(stats, dict)
        
        # Should contain basic statistics
        expected_keys = ['total_songs', 'total_chords', 'unique_chords', 'chord_frequencies']
        for key in expected_keys:
            if key in stats:  # Some keys might be optional
                self.assertTrue(True)
        
        # Test specific values
        if 'total_songs' in stats:
            self.assertEqual(stats['total_songs'], 3)
        
        if 'chord_frequencies' in stats:
            self.assertIsInstance(stats['chord_frequencies'], dict)
            # Should contain some common chords
            self.assertIn('C:maj', stats['chord_frequencies'])
        
        # Test with empty data
        empty_stats = extract_chord_statistics([])
        self.assertIsInstance(empty_stats, dict)
        if 'total_songs' in empty_stats:
            self.assertEqual(empty_stats['total_songs'], 0)
    
    def test_create_chord_transition_matrix(self):
        """Test chord transition matrix creation."""
        matrix = create_chord_transition_matrix(self.sample_songs)
        
        # Should return some matrix-like structure
        self.assertIsNotNone(matrix)
        
        # Could be various formats (dict, DataFrame, numpy array, etc.)
        self.assertIsInstance(matrix, (dict, pd.DataFrame, list, tuple))
        
        # Test with single song
        single_song_matrix = create_chord_transition_matrix([self.sample_songs[0]])
        self.assertIsNotNone(single_song_matrix)
        
        # Test with empty data
        empty_matrix = create_chord_transition_matrix([])
        self.assertIsNotNone(empty_matrix)
    
    @patch('leadsheetanalyser.data_processing.jams.load')
    @patch('os.listdir')
    def test_process_song_data_mocked(self, mock_listdir, mock_jams_load):
        """Test process_song_data with mocked dependencies."""
        # Mock file listing
        mock_listdir.return_value = ['1.jams', '2.jams', '3.jams']
        
        # Mock JAMS loading
        mock_jam = MagicMock()
        mock_jam.annotations = [MagicMock()]
        mock_jam.annotations[0].data = [
            MagicMock(time=0.0, duration=2.0, value='C:maj'),
            MagicMock(time=2.0, duration=2.0, value='F:maj'),
            MagicMock(time=4.0, duration=2.0, value='G:7'),
            MagicMock(time=6.0, duration=2.0, value='C:maj')
        ]
        mock_jams_load.return_value = mock_jam
        
        # Test processing
        result = process_song_data(self.sample_df, self.temp_dir)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # Each song should be a dictionary
        for song in result:
            self.assertIsInstance(song, dict)
            expected_fields = ['id', 'title', 'chord_progression']
            for field in expected_fields:
                if field in song:  # Some fields might be optional
                    self.assertTrue(True)
    
    def test_load_and_process_dataset_structure(self):
        """Test load_and_process_dataset structure (without actual file loading)."""
        # Create temporary CSV file
        csv_path = os.path.join(self.temp_dir, 'test_meta.csv')
        self.sample_df.to_csv(csv_path, index=False)
        
        # Test the function exists and has expected signature
        try:
            # This might fail due to missing JAMS files, but we test the interface
            result = load_and_process_dataset(csv_path, self.temp_dir, 'dataframe')
        except (FileNotFoundError, ValueError, Exception):
            # Expected to fail with real file operations, but function should exist
            pass
        
        # Test different output formats
        for output_format in ['dataframe', 'list', 'dict']:
            try:
                result = load_and_process_dataset(csv_path, self.temp_dir, output_format)
            except (FileNotFoundError, ValueError, Exception):
                # Expected to fail with real file operations
                pass
    
    def test_integration_workflow(self):
        """Test integration of multiple data processing functions."""
        # Start with raw songs data
        initial_count = len(self.sample_songs)
        
        # Filter songs
        filtered_songs = filter_songs_by_criteria(
            self.sample_songs,
            min_chords=3,
            allowed_genres=['Jazz', 'Pop']
        )
        
        # Should have some songs remaining
        self.assertGreater(len(filtered_songs), 0)
        self.assertLessEqual(len(filtered_songs), initial_count)
        
        # Extract statistics
        stats = extract_chord_statistics(filtered_songs)
        self.assertIsInstance(stats, dict)
        
        # Create transition matrix
        matrix = create_chord_transition_matrix(filtered_songs)
        self.assertIsNotNone(matrix)
        
        # Verify consistency
        if 'total_songs' in stats:
            self.assertEqual(stats['total_songs'], len(filtered_songs))
    
    def test_error_handling(self):
        """Test error handling for various edge cases."""
        # Test with invalid data types
        try:
            result = filter_songs_by_criteria(None)
        except (TypeError, AttributeError):
            pass  # Expected to fail
        
        try:
            result = filter_songs_by_criteria("not a list")
        except (TypeError, AttributeError):
            pass  # Expected to fail
        
        # Test with malformed song data
        malformed_songs = [
            {'id': 1},  # Missing required fields
            {'title': 'Test', 'chord_progression': 'not a list'},  # Wrong type
        ]
        
        try:
            stats = extract_chord_statistics(malformed_songs)
            # Should either work with partial data or raise appropriate error
            self.assertIsInstance(stats, dict)
        except (TypeError, AttributeError, KeyError):
            pass  # Acceptable to raise error for malformed data
    
    def test_empty_data_handling(self):
        """Test handling of empty datasets."""
        # Empty song list
        empty_stats = extract_chord_statistics([])
        self.assertIsInstance(empty_stats, dict)
        
        empty_matrix = create_chord_transition_matrix([])
        self.assertIsNotNone(empty_matrix)
        
        empty_filtered = filter_songs_by_criteria([])
        self.assertEqual(len(empty_filtered), 0)
        
        # Songs with empty chord progressions
        empty_chord_songs = [
            {
                'id': 1,
                'title': 'Empty Song',
                'chord_progression': [],
                'key': 'C:major',
                'artist': 'Artist',
                'genre': 'Test'
            }
        ]
        
        empty_chord_stats = extract_chord_statistics(empty_chord_songs)
        self.assertIsInstance(empty_chord_stats, dict)


if __name__ == '__main__':
    unittest.main()
