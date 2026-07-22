"""
Core chord processing functions for the leadsheetanalyser package.

This module consolidates all basic chord manipulation, parsing, and 
representation functions in one place.
"""

from music21 import *
import fractions
import numpy as np
from harte.interval import HarteInterval
from typing import Union, List, Tuple

# Import constants from dedicated constants module
from .constants import (
    NOTE_TO_PC,
    PC_TO_NOTE_FLAT,
    PC_TO_NOTE_SHARP,
    CHORD_SHORTHANDS,
    SIMPLIFIED_CHORD_NAMES,
    CHORD_NAME_CLEANUP_STRINGS
)


# =============================================================================
# CORE FUNCTIONS - Root and key mapping
# =============================================================================

def map_root(root_str: str) -> int:
    """
    Map the root in a string representation into a number between 0 and 11.
    Supports natural notes and sharps/flats like "C", "Ab", "D#", etc.

    Args:
        root_str (str): string representation of a root note

    Returns:
        int: number between 0 and 11 representing the root note
    """
    return NOTE_TO_PC.get(root_str, None)


def key_retriever(key: str) -> int:
    """
    Retrieve the key in integer as the root of the major mode

    Args:
        key (str): string description in the form X:major or Y:minor

    Returns:
        int: value of the major mode root
    """
    key_splitted = key.split(":")
    root = map_root(key_splitted[0])
    return root


# =============================================================================
# CHORD PROCESSING FUNCTIONS
# =============================================================================

def addings(interval_H: str) -> int:
    """
    Return the interval in integers with the Harte notation

    Args:
        interval_H (str): Harte name for the interval

    Returns:
        int: number of semitones of the interval
    """
    if "*" in interval_H:
        # the symbol "*" means without
        return -((int(HarteInterval(interval_H).semitones) + 12) % 12)
    else:
        return (int(HarteInterval(interval_H).semitones) + 12) % 12

def map_kind(kind_str: str) -> list[int]:
    """
    Transform the Harte notation into a binary vector that contain 1 if the interval is in the chord

    Args:
        kind_str (str): kind description in string

    Returns:
        list[int]: kind description in the form of a binary vector
    """
    no_bass = kind_str.split("/")
    bass = []
    if len(no_bass) > 1:
        bass.append(no_bass[1])
    no_bass = no_bass[0]

    low_up = no_bass.split("(")
    res = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    if len(low_up) < 2:
        if len(bass) > 0:
            int_list = list(CHORD_SHORTHANDS[low_up[0]]) + [addings(bass[0])]
        else:
            int_list = list(CHORD_SHORTHANDS[low_up[0]])

        for i in range(11):
            if i + 1 in int_list and (-(i + 1)) not in int_list:
                res[i] = 1
    else:
        if len(low_up) == 2:
            if len(bass) > 0:
                int_list = ([i for i in CHORD_SHORTHANDS[low_up[0]]] + 
                           [addings(a) for a in low_up[1][:-1].split(",")] + 
                           [addings(bass[0])])
            else:
                int_list = ([i for i in CHORD_SHORTHANDS[low_up[0]]] + 
                           [addings(a) for a in low_up[1][:-1].split(",")])
            
            for i in range(11):
                if i + 1 in int_list and (-(i + 1)) not in int_list:
                    # check for the negative value to
                    # not add the interval if it is not played
                    res[i] = 1
    return res

def to_note_list(c: tuple[int]) -> list[int]:
    """
    Convert the chord tuple of the "value" column into a list of notes that the chord contain

    Args:
        c (tuple[int]): tuple which first element in the root and the 11 others are the kind

    Returns:
        list[int]: list that contains the notes of the chord
    """
    n_list = []
    root = c[0]
    n_list.append(root)
    for i in range(1, 12):
        if c[i] == 1:
            n_list.append((root + i) % 12)
    return n_list


def map_chord(chord_str: str):
    """
    Final mapping that, given a chord in the Harte notation, return a chord in our notation
    
    Args:
        chord_str (str): chord in Harte notation (e.g., "C:maj7", "D:min") or 
                        shorthand notation (e.g., "Am", "C7", "Dm7")
        
    Returns:
        list: chord representation as [root] + kind_vector
    """
    if chord_str == "N":
        return [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    # Handle both full Harte notation and common shorthands
    if ":" in chord_str:
        # Full Harte notation: "A:min", "C:maj7"
        root = chord_str.split(":")[0]
        kind = chord_str.split(":")[1]
    else:
        # Shorthand notation: "Am", "C7", "Dm7", etc.
        # Parse root and kind from shorthand
        root, kind = parse_shorthand_chord(chord_str)
    
    return [map_root(root)] + map_kind(kind)


def parse_shorthand_chord(chord_str: str) -> tuple[str, str]:
    """
    Parse shorthand chord notation to extract root and kind.
    
    Examples:
    - "Am" -> ("A", "min")
    - "C7" -> ("C", "7") 
    - "Dm7" -> ("D", "min7")
    - "F#maj7" -> ("F#", "maj7")
    """
    # Handle flat/sharp in root (e.g., "Bb", "F#")
    if len(chord_str) >= 2 and chord_str[1] in ['b', '#']:
        root = chord_str[:2]
        suffix = chord_str[2:]
    else:
        root = chord_str[0]
        suffix = chord_str[1:]
    
    # Convert common shorthand suffixes to Harte notation
    shorthand_to_harte = {
        'm': 'min',
        'min': 'min',
        'maj': 'maj',
        '': 'maj',  # No suffix = major
        '7': '7',
        'maj7': 'maj7',
        'm7': 'min7',
        'min7': 'min7',
        'dim': 'dim',
        'aug': 'aug',
        'sus2': 'sus2',
        'sus4': 'sus4',
    }
    
    # Get the Harte kind, default to major if unknown
    kind = shorthand_to_harte.get(suffix, 'maj')
    
    return root, kind


# =============================================================================
# CHORD NAMING FUNCTIONS
# =============================================================================

def chord_nice_name(c: tuple[int]) -> str:
    """
    String representation of chords that return a "nice name"

    Args:
        c (tuple[int]): tuple which first element in the root and the 11 others are the kind

    Returns:
        str: nice name representation of the chord
    """
    p_classes = to_note_list(c)
    root = PC_TO_NOTE_FLAT[c[0]]
    c_name = chord.Chord([PC_TO_NOTE_FLAT[i] for i in p_classes])
    c_name.root(root)
    k_name = str(c_name.commonName)
    
    # Clean up chord name
    for s in CHORD_NAME_CLEANUP_STRINGS:
        if s in k_name:
            k_name = k_name.replace(s, "")

    # Simplify chord name if possible
    for key in SIMPLIFIED_CHORD_NAMES.keys():
        if k_name.split(" ")[0] == key:
            k_name = SIMPLIFIED_CHORD_NAMES[key]
    
    return root + " " + str(k_name)


# =============================================================================
# CHORD CONVERSION FUNCTIONS
# =============================================================================

def chord_to_pitch_classes(root: int, kind_vec: Union[np.ndarray, list]) -> set:
    """
    Convert a chord (root + kind vector) to a set of pitch classes.
    
    Parameters:
    - root: root note (0-11)
    - kind_vec: binary vector of length 11 representing intervals
    
    Returns:
    - set of pitch classes contained in the chord
    """
    pitch_classes = {root}  # Start with root
    for i, has_interval in enumerate(kind_vec):
        if has_interval:
            pitch_classes.add((root + i + 1) % 12)
    
    return pitch_classes


def pitch_classes_to_chord(pitch_classes: set, root: int) -> np.ndarray:
    """
    Convert a set of pitch classes to a chord kind vector relative to a root.
    
    Parameters:
    - pitch_classes: set of pitch classes
    - root: root note to use as reference (0-11)
    
    Returns:
    - binary vector of length 11 representing the chord kind
    """
    kind_vec = np.zeros(11, dtype=int)
    for pc in pitch_classes:
        if pc != root:  # Don't include the root in the kind vector
            interval = (pc - root) % 12
            if 1 <= interval <= 11:  # Valid interval range
                kind_vec[interval - 1] = 1
    
    return kind_vec


# =============================================================================
# CHORD TRANSFORMATION FUNCTIONS
# =============================================================================

def transpose_chord(chord: Union[list, tuple], semitones: int) -> list:
    """
    Transpose a chord by a given number of semitones.
    
    Args:
        chord: chord representation as [root] + kind_vector
        semitones: number of semitones to transpose (positive = up, negative = down)
    
    Returns:
        list: transposed chord
    """
    if len(chord) == 0:
        return chord
    
    transposed = list(chord)  # Create a copy
    if isinstance(transposed[0], int) and transposed[0] >= 0:
        transposed[0] = (transposed[0] + semitones) % 12
    
    return transposed


def transpose_to_c(chord_progression: List, key_name: int) -> List:
    """
    Transpose a chord progression to C major/minor
    
    Args:
        chord_progression: List of chords (each chord is a list where first element is root note)
        key_name: Current key as integer (0=C, 1=Db/C#, 2=D, etc.)
    
    Returns:
        List of transposed chords
    """
    if key_name is None or key_name == 0:
        # Already in C, no transposition needed
        return chord_progression
    
    transposed = []
    for chord in chord_progression:
        if isinstance(chord, list) and len(chord) > 0:
            transposed_chord = transpose_chord(chord, -key_name)
            transposed.append(transposed_chord)
        else:
            # Handle edge cases (empty chords, etc.)
            transposed.append(chord)
    
    return transposed


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def chord_name_to_tuple(chord_name: str) -> Tuple[int, np.ndarray]:
    """
    Convert a chord name to (root, kind_vec) tuple.
    
    Parameters:
    - chord_name: chord name like "C:maj7", "Dm", "G7", etc.
    
    Returns:
    - tuple (root, kind_vec)
    
    Examples:
    >>> chord_name_to_tuple("C:maj7")
    (0, array([0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1]))
    >>> chord_name_to_tuple("Am")  
    (9, array([0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]))
    """
    chord_data = map_chord(chord_name)
    if len(chord_data) == 12:
        root = chord_data[0]
        kind_vec = np.array(chord_data[1:])
        return root, kind_vec
    else:
        raise ValueError(f"Invalid chord format: {chord_name}")


def closest_fraction(number):
    """
    Routine to return the closest fraction having denominators between 1 and 4,
    used for rhythmic simplification
    
    Args:
        number: The number to approximate as a fraction
        
    Returns:
        fractions.Fraction: The closest fraction with denominator 1-4
    """
    closest = fractions.Fraction(0, 1)
    min_diff = float('inf')
    
    for denominator in range(1, 5):
        fraction = fractions.Fraction(round(number * denominator), denominator)
        diff = (number - fraction) ** 2
        if diff < min_diff:
            min_diff = diff
            closest = fraction
    
    return closest
