"""
Test configuration and common utilities for leadsheetanalyser tests.
"""
import os
import sys

# Add the parent directory to the Python path so we can import leadsheetanalyser
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Common test data
TEST_CHORDS = [
    "C:maj", "A:min", "D:min", "G:7", "F:maj7",
    "Am", "C7", "Dm7", "F#maj7", "Bb"
]

TEST_SCALES = [
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],  # Major scale
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],  # Minor scale
    [1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],  # Chromatic portions
]

# Expected pitch classes for common chords
EXPECTED_CHORD_PITCH_CLASSES = {
    "C:maj": [0, 4, 7],
    "A:min": [9, 0, 4],
    "D:min": [2, 5, 9],
    "G:7": [7, 11, 2, 5],
    "F:maj7": [5, 9, 0, 4]
}
