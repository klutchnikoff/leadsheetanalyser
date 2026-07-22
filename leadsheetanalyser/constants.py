"""
Constants for the leadsheetanalyser package.

This module contains all the musical constants used throughout the package,
including note mappings, chord definitions, and naming conventions.
"""

from typing import List
import numpy as np

# =============================================================================
# NOTE MAPPINGS
# =============================================================================

# Note name to pitch class mapping
NOTE_TO_PC = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11,
    # Double sharps (raise by 2 semitones)
    'C##': 2, 'D##': 4, 'E##': 6, 'F##': 8, 'G##': 10, 'A##': 0, 'B##': 1,
    # Double flats (lower by 2 semitones)
    'Cbb': 10, 'Dbb': 0, 'Ebb': 2, 'Fbb': 3, 'Gbb': 5, 'Abb': 7, 'Bbb': 9
}

# Reverse mapping: pitch class to note name (using flats)
PC_TO_NOTE_FLAT = {
    0: 'C', 1: 'Db', 2: 'D', 3: 'Eb', 4: 'E', 5: 'F',
    6: 'Gb', 7: 'G', 8: 'Ab', 9: 'A', 10: 'Bb', 11: 'B'
}

# Reverse mapping: pitch class to note name (using sharps)
PC_TO_NOTE_SHARP = {
    0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F',
    6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'
}

# =============================================================================
# CHORD DEFINITIONS
# =============================================================================

# Dictionary of chord shorthands in Harte notation
CHORD_SHORTHANDS = {
    ""        : (),
    "maj"     : (4, 7),
    "min"     : (3, 7),
    "dim"     : (3, 6),
    "aug"     : (4, 8),
    "maj7"    : (4, 7, 11),
    "min7"    : (3, 7, 10),
    "7"       : (4, 7, 10),
    "dim7"    : (3, 6, 9),
    "hdim"    : (3, 6, 10),
    "hdim7"   : (3, 6, 10),
    "minmaj7" : (3, 7, 11),
    "6"       : (4, 7, 9),
    "maj6"    : (4, 7, 9),
    "min6"    : (3, 7, 9),
    "9"       : (2, 4, 7, 10),
    "maj9"    : (2, 4, 7, 11),
    "min9"    : (2, 3, 7, 10),
    "sus4"    : (5, 7)
}

# =============================================================================
# CHORD NAME SIMPLIFICATION
# =============================================================================

# Simplified chord names mapping
SIMPLIFIED_CHORD_NAMES = {
    'flat-ninth': '7b9',
    'major-ninth': 'maj9',
    "Stravinsky's": '7#11',
    'half-diminished': 'min7b5',
    'dominant-ninth': '9',
    'Hirajoshi': 'maj7#11',
    'augmented-eleventh': '7#11',
    'Balinese': 'maj7/4',
    'combinatorial': '7 alt.',
    'augmented-diminished': '7aug',
    'dominant': '7',
    'all-interval': 'maj/#4',
    'augmented': 'aug',
    'major': 'maj',
    'Neapolitan': '7#9',
    'Kumoi': '7/4',
    'phrygian': 'maj9/#4',
    'Guidonian': 'min11',
    "Messiaen's": '7b5',
    'minor-augmented': 'minmaj7',
    'major-diminished': 'maj/b9',
    'minor': 'min',
    'major-minor': 'maj/min',
    'harmonic': '7b9/11',
    'quartal': '7sus4',
    'diminished-major': 'min7b5b9',
    'Lebanese': 'maj7/b6',
    'tritone-fourth': '(5)/b9',
    'melodic': "7 alt.",
    'diminished': 'dim7',
    'whole-tone': "9 (#/b)5",
    'minor-ninth': 'min9',
    'minor-major': 'minmaj9',
    'forte': "7#9",
    'Javanese': '7b5#9',
    'sus4': 'sus4',
    'major-second': "maj add9",
    'enigmatic': '7+#9',
    'minor-second': 'sus4/b9',
    'French': "7b5",
    'perfect-fourth': "add 4",
    'major-third': 'sus2 aug. maj7',
    'minor-diminished': "maj9 b5 (no3rd)",
    'center-cluster': 'min7b9',
    'diminished-augmented': "7aug b9",
    'Perfect': "5",
    'Spanish': '13/b9',
    'incomplete': "maj7 (no 3rd)",
    'augmented-sixth': "7b5b9",
    'dorian': "min11",
    'note': 'N',
    'Augmented': 'aug',
    'melodic-minor': "minmaj6/9",
    'Neapolitan-major': '7(9,#11,b13)',
    'dominant-eleventh': "7(9,11)"
}

# Strings to remove from chord names for simplification
CHORD_NAME_CLEANUP_STRINGS = [
    "enharmonic to ", 
    "enharmonic equivalent to ", 
    " chord", 
    " triad"
]

# =============================================================================
# DIATONIC MODES (CHURCH MODES)
# =============================================================================

# Diatonic modes (church modes) with weighted priorities
W_DIATONIC = np.array([
    [0, 1, 0, 2, 2, 0, 2, 0, 1, 0, 2],  # Ionian (C major)
    [0, 1, 3, 0, 1, 0, 2, 0, 2, 1, 0],  # Dorian (D)
    [2, 0, 2, 0, 1, 0, 3, 1, 0, 1, 0],  # Phrygian (E)
    [0, 1, 0, 2, 0, 3, 2, 0, 1, 0, 1],  # Lydian (F)
    [0, 1, 0, 3, 1, 0, 2, 0, 1, 2, 0],  # Mixolydian (G)
    [0, 2, 2, 0, 1, 0, 2, 2, 0, 1, 0],  # Aeolian (A natural minor)
    [1, 0, 2, 0, 1, 4, 0, 1, 0, 1, 0],  # Locrian (B)
], dtype=float)

# Normalize to probability vectors
W_DIATONIC = W_DIATONIC / W_DIATONIC.sum(axis=1, keepdims=True)

DIATONIC_MODE_NAMES = [
    "Ionian", 
    "Dorian", 
    "Phrygian", 
    "Lydian", 
    "Mixolydian", 
    "Aeolian", 
    "Locrian"
]

# =============================================================================
# MESSIAEN MODES OF LIMITED TRANSPOSITION
# =============================================================================

def _messiaen_modes():
    """The 15 modes of limited transposition (invariant under a nonzero
    transposition), Messiaen's seven named modes first (in his order), then
    the remaining eight by size. Returns (W, names): W is 15x11, each row the
    interval indicator of a mode over the intervals 1..11 above the root,
    uniformly weighted (rows sum to 1).

    Built by enumeration, replacing a hand-typed matrix whose rows used an
    inconsistent indexing convention and were not, in fact, of limited
    transposition.
    """
    from itertools import combinations

    named = {1: {0, 2, 4, 6, 8, 10}, 2: {0, 1, 3, 4, 6, 7, 9, 10},
             3: {0, 2, 3, 4, 6, 7, 8, 10, 11}, 4: {0, 1, 2, 5, 6, 7, 8, 11},
             5: {0, 1, 5, 6, 7, 11}, 6: {0, 2, 4, 5, 6, 8, 10, 11},
             7: {0, 1, 2, 3, 5, 6, 7, 8, 9, 11}}

    def period(S):
        return min((t for t in range(1, 12) if {(x + t) % 12 for x in S} == S), default=12)

    def canon(S):
        return min(tuple(sorted((x - t) % 12 for x in S)) for t in range(12))

    def number(S):
        return next((k for k, M in named.items() if canon(S) == canon(M)), None)

    extra = {(0, 6): "Tritone", (0, 4, 8): "Augmented triad",
             (0, 3, 6, 9): "Diminished seventh", (0, 1, 4, 5, 8, 9): "Hexatonic (augmented) scale"}

    classes = {}
    for size in range(2, 12):
        for c in combinations(range(12), size):
            S = set(c)
            if 0 in S and period(S) < 12:
                classes.setdefault(canon(S), S)
    modes = sorted(classes.values(),
                   key=lambda S: (0, number(S)) if number(S) else (1, len(S), canon(S)))

    rows, names = [], []
    for S in modes:
        ell = np.array([1.0 if i in S else 0.0 for i in range(1, 12)])
        rows.append(ell / ell.sum())
        k = number(S)
        if k:
            names.append(f"Mode {k}" + {1: " (whole-tone)", 2: " (octatonic)"}.get(k, ""))
        else:
            names.append(extra.get(tuple(sorted(S)), f"Symmetric set ({len(S)} notes)"))
    return np.array(rows), names


W_MESSIAEN, MESSIAEN_MODE_NAMES = _messiaen_modes()

BASIC_CHORD_KINDS = {#-  D  E  F  -  G  -  A  -  B  -
    # suspended kinds
    "7sus4":         [0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0],
    "7sus2":         [0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0],
    "7sus2sus4":     [0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0],
    # minor kinds
    "min69":         [0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0],
    "min9":          [0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0],
    "min7":          [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
    "min6":          [0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0],
    "min":           [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    # major kinds
    "9":             [0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0],
    "7":             [0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
    "maj9":          [0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    "maj69":         [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0],
    "maj7":          [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    "maj":           [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
    "maj6":          [0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0],
    # diminished kinds
    "dim7":          [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
    "dim":           [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "min7b5":        [0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0],
}