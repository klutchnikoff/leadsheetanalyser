"""
Scale and mode analysis functions for the leadsheetanalyser package.

This module contains functions for analyzing scales, modes, and their
mathematical properties including transposition analysis.
"""

from typing import List, Union
import numpy as np


# =============================================================================
# SCALE ANALYSIS FUNCTIONS
# =============================================================================

def compute_transposition_number(scale: Union[List[int], np.ndarray]) -> int:
    """
    Compute the transposition number of a scale in {0,1}^12.
    
    The transposition number is the number of distinct transpositions
    of a given scale or mode. This is particularly useful for analyzing
    Messiaen's modes of limited transposition.
    
    For example:
    - A whole-tone scale has 2 distinct transpositions
    - An octatonic scale has 3 distinct transpositions
    - A chromatic scale has 1 distinct transposition
    - A major scale has 12 distinct transpositions
    
    Args:
        scale (List[int] or np.ndarray): Binary vector of length 12 representing
                                        the scale, where 1 indicates the presence
                                        of a pitch class and 0 indicates absence.
    
    Returns:
        int: The number of distinct transpositions of the scale.
        
    Examples:
        >>> # Whole-tone scale (C, D, E, F#, G#, A#)
        >>> whole_tone = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        >>> compute_transposition_number(whole_tone)
        2
        
        >>> # Octatonic scale
        >>> octatonic = [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1]
        >>> compute_transposition_number(octatonic)
        3
        
        >>> # Major scale (C major)
        >>> major = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        >>> compute_transposition_number(major)
        12
    """
    # Convert to numpy array if it's a list
    if isinstance(scale, list):
        scale = np.array(scale)
    
    # Ensure we have a binary vector of length 12
    if len(scale) != 12:
        raise ValueError("Scale must be a vector of length 12")
    
    if not all(x in [0, 1] for x in scale):
        raise ValueError("Scale must be a binary vector containing only 0s and 1s")
    
    # Generate all possible transpositions
    transpositions = set()
    
    for i in range(12):
        # Transpose the scale by i semitones (circular shift)
        transposed = tuple(np.roll(scale, i))
        transpositions.add(transposed)
    
    # Return the number of distinct transpositions
    return len(transpositions)


def get_scale_symmetry_axis(scale: Union[List[int], np.ndarray]) -> List[int]:
    """
    Find the symmetry axes of a scale.
    
    A symmetry axis is a transposition that maps the scale onto itself.
    This is useful for understanding the internal structure of modes
    of limited transposition.
    
    Args:
        scale (List[int] or np.ndarray): Binary vector representing the scale.
    
    Returns:
        List[int]: List of transposition intervals (in semitones) that map
                  the scale onto itself.
    """
    if isinstance(scale, list):
        scale = np.array(scale)
    
    if len(scale) != 12:
        raise ValueError("Scale must be a vector of length 12")
    
    symmetry_axes = []
    
    for i in range(12):
        # Check if transposing by i semitones gives the same scale
        transposed = np.roll(scale, i)
        if np.array_equal(scale, transposed):
            symmetry_axes.append(i)
    
    return symmetry_axes


def analyze_mode_properties(scale: Union[List[int], np.ndarray]) -> dict:
    """
    Analyze various properties of a musical mode or scale.
    
    Args:
        scale (List[int] or np.ndarray): Binary vector representing the scale.
    
    Returns:
        dict: Dictionary containing various properties:
            - 'transposition_number': Number of distinct transpositions
            - 'symmetry_axes': List of symmetry transposition intervals
            - 'cardinality': Number of pitch classes in the scale
            - 'is_limited_transposition': Whether it's a mode of limited transposition
    """
    if isinstance(scale, list):
        scale = np.array(scale)
    
    transposition_num = compute_transposition_number(scale)
    symmetry_axes = get_scale_symmetry_axis(scale)
    cardinality = int(np.sum(scale))
    
    # A mode of limited transposition has fewer than 12 distinct transpositions
    is_limited = transposition_num < 12
    
    return {
        'transposition_number': transposition_num,
        'symmetry_axes': symmetry_axes,
        'cardinality': cardinality,
        'is_limited_transposition': is_limited,
        'period': 12 // transposition_num  # The period of repetition
    }


def scale_from_intervals(intervals: List[int], start_note: int = 0) -> List[int]:
    """
    Create a scale binary vector from a list of intervals.
    
    Args:
        intervals (List[int]): List of intervals in semitones from the root.
        start_note (int): Starting pitch class (0-11, default is 0 for C).
    
    Returns:
        List[int]: Binary vector representing the scale.
        
    Example:
        >>> # Major scale intervals: 0, 2, 4, 5, 7, 9, 11
        >>> major_intervals = [0, 2, 4, 5, 7, 9, 11]
        >>> scale_from_intervals(major_intervals)
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
    """
    scale = [0] * 12
    
    for interval in intervals:
        pitch_class = (start_note + interval) % 12
        scale[pitch_class] = 1
    
    return scale


# =============================================================================
# MODE CLASSIFICATION FUNCTIONS
# =============================================================================

def identify_mode(scale: Union[List[int], np.ndarray]) -> dict:
    """
    Attempt to identify a scale/mode from common musical systems.
    
    Args:
        scale: Binary vector representing the scale
        
    Returns:
        dict: Information about potential mode matches
    """
    from .constants import W_DIATONIC, DIATONIC_MODE_NAMES, W_MESSIAEN, MESSIAEN_MODE_NAMES
    
    if isinstance(scale, list):
        scale = np.array(scale)
    
    # Check against Diatonic modes
    diatonic_matches = []
    for i, mode_weights in enumerate(W_DIATONIC):
        mode_binary = (mode_weights > 0).astype(int)
        if np.array_equal(scale[1:], mode_binary):  # Compare intervals (skip root)
            diatonic_matches.append(DIATONIC_MODE_NAMES[i])
    
    # Check against Messiaen modes
    messiaen_matches = []
    for i, mode_weights in enumerate(W_MESSIAEN):
        mode_binary = (mode_weights > 0).astype(int)
        if np.array_equal(scale[1:], mode_binary):  # Compare intervals (skip root)
            messiaen_matches.append(MESSIAEN_MODE_NAMES[i])
    
    properties = analyze_mode_properties(scale)
    
    return {
        'diatonic_matches': diatonic_matches,
        'messiaen_matches': messiaen_matches,
        'properties': properties
    }


def generate_mode_variants(base_scale: Union[List[int], np.ndarray]) -> List[List[int]]:
    """
    Generate all transpositions of a given scale/mode.
    
    Args:
        base_scale: Binary vector representing the base scale
        
    Returns:
        List of all distinct transpositions
    """
    if isinstance(base_scale, list):
        base_scale = np.array(base_scale)
    
    variants = []
    seen = set()
    
    for i in range(12):
        transposed = tuple(np.roll(base_scale, i))
        if transposed not in seen:
            seen.add(transposed)
            variants.append(list(transposed))
    
    return variants
