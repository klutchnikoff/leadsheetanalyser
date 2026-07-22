"""
Chord Dissimilarity Analysis for the leadsheetanalyser package.

This module provides functions for computing dissimilarities between chords
using various musical systems and weight matrices. It includes chord 
reinterpretation, validation functions, and different dissimilarity metrics.
"""

from typing import Tuple, Union, List
import numpy as np
from .constants import *
from .chords import chord_name_to_tuple
from .chords import chord_to_pitch_classes, pitch_classes_to_chord


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_chord_kind(kind_vec: np.ndarray) -> None:
    """
    Validate that a chord kind vector is properly formatted.
    
    Parameters:
    - kind_vec: binary vector representing chord intervals
    
    Raises:
    - ValueError: if the vector is not properly formatted
    """
    if not isinstance(kind_vec, np.ndarray):
        raise ValueError("Chord kind must be a numpy array")
    
    if len(kind_vec) != 11:
        raise ValueError("Chord kind vector must have length 11")
    
    if not all(x in [0, 1] for x in kind_vec):
        raise ValueError("Chord kind vector must be binary (0s and 1s only)")


def validate_musical_system(W: np.ndarray) -> None:
    """
    Validate that a musical system weight matrix is properly formatted.
    
    Parameters:
    - W: weight matrix for musical system
    
    Raises:
    - ValueError: if the matrix is not properly formatted
    """
    if not isinstance(W, np.ndarray):
        raise ValueError("Musical system must be a numpy array")
    
    if len(W.shape) != 2:
        raise ValueError("Musical system must be a 2D matrix")
    
    if W.shape[1] != 11:
        raise ValueError("Musical system must have 11 columns (for 11 intervals)")
    
    if not np.all(W >= 0):
        raise ValueError("Musical system weights must be non-negative")


def validate_root(root: int) -> None:
    """
    Validate that a root note is in the valid range.
    
    Parameters:
    - root: root note as pitch class (0-11)
    
    Raises:
    - ValueError: if root is not in valid range
    """
    if not isinstance(root, int):
        raise ValueError("Root must be an integer")
    
    if not (0 <= root <= 11):
        raise ValueError("Root must be in range 0-11")


# =============================================================================
# CHORD MANIPULATION FUNCTIONS
# =============================================================================

def reinterpret_chord(kind_vec: np.ndarray, old_root: int, new_root: int) -> np.ndarray:
    """
    Reinterpret a chord kind relative to a new root.

    This function takes a chord defined relative to one root and recomputes
    its interval structure relative to a different root. This is essential
    for comparing chords that may have different roots but similar harmonic
    content.

    Parameters:
    - kind_vec: binary vector of length 11 representing a chord kind
    - old_root: original root (0–11)
    - new_root: new root for reinterpretation (0–11)

    Returns:
    - reinterpreted kind vector (binary vector of length 11)
    
    Example:
    >>> # C major chord (C-E-G) reinterpreted with E as root
    >>> c_maj = np.array([0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])  # intervals 4, 7
    >>> reinterpret_chord(c_maj, 0, 4)  # C to E
    array([0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0])  # intervals 8, 10 (Am6)
    """
    validate_chord_kind(kind_vec)
    validate_root(old_root)
    validate_root(new_root)
    
    # Construct pitch class set (including root)
    pitch_classes = {(old_root + i) % 12 for i in [0] + [j for j, v in enumerate(kind_vec, 1) if v == 1]}

    # Compute new kind vector relative to new_root
    new_kind = np.zeros(11, dtype=int)
    for j in range(1, 12):
        if (new_root + j) % 12 in pitch_classes:
            new_kind[j - 1] = 1
    return new_kind


def pitch_classes_to_chord(pitch_classes: set, root: int) -> np.ndarray:
    """
    Convert a set of pitch classes to a chord kind vector relative to a root.
    
    Parameters:
    - pitch_classes: set of pitch classes
    - root: root note to use as reference (0-11)
    
    Returns:
    - binary vector of length 11 representing the chord kind
    """
    validate_root(root)
    
    kind_vec = np.zeros(11, dtype=int)
    for pc in pitch_classes:
        if pc != root:  # Don't include the root in the kind vector
            interval = (pc - root) % 12
            if 1 <= interval <= 11:  # Valid interval range
                kind_vec[interval - 1] = 1
    
    return kind_vec


def modal_embedding(kind_vec: np.ndarray, W: np.ndarray, mode: str = "linear") -> np.ndarray:
    """
    Compute the modal embedding Phi_W(k) of a chord kind.
    
    Parameters:
    - kind_vec: binary vector of length 11 representing a chord kind
    - W: system matrix of shape (m, 11) representing musical weights
    - mode: "linear" for standard embedding Wk (default), or "angular" to 
            return the L2-normalized profile Wk / ||Wk||_2.
    
    Returns:
    - np.ndarray: the modal profile of the chord in the system W
    """
    validate_chord_kind(kind_vec)
    validate_musical_system(W)
    
    emb = W @ kind_vec
    if mode == "angular":
        norm = np.linalg.norm(emb)
        if norm > 1e-12:
            emb = emb / norm
        else:
            emb = np.zeros_like(emb)
    elif mode != "linear":
        raise ValueError(f"Unknown embedding mode: {mode}")
        
    return emb


# =============================================================================
# DISSIMILARITY FUNCTIONS
# =============================================================================

def modal_dissimilarity(chord1: Tuple[int, np.ndarray], chord2: Tuple[int, np.ndarray], W: np.ndarray, p: float = 1.0) -> float:
    """
    Compute dissimilarity between two chords using a musical system W.

    This function computes the dissimilarity by reinterpreting each chord in the 
    root of the other and measuring the Euclidean distance in the weight space 
    defined by W. The two directional discrepancies are then aggregated using 
    an l_p norm.

    Parameters:
    - chord1, chord2: tuples (root, kind_vec), where root ∈ {0,…,11}
    - W: system matrix of shape (m, 11) representing musical weights
    - p: the norm to aggregate the two directional discrepancies (default 1.0 for sum)

    Returns:
    - float: the modal dissimilarity between the two chords
        
    Example:
    >>> # Compare C major and G major chords
    >>> c_maj = (0, np.array([0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]))
    >>> g_maj = (7, np.array([0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]))
    >>> W = np.eye(11)  # Identity matrix
    >>> d = modal_dissimilarity(c_maj, g_maj, W, p=1.0)
    """
    validate_musical_system(W)
    r1, k1 = chord1
    r2, k2 = chord2
    validate_root(r1)
    validate_root(r2)
    validate_chord_kind(k1)
    validate_chord_kind(k2)

    # Reinterpret each chord in the root of the other
    k1_r2 = reinterpret_chord(k1, r1, r2)
    k2_r1 = reinterpret_chord(k2, r2, r1)

    # Compute dissimilarities using Euclidean norm in W-space
    # We use modal_embedding directly for code clarity (this is the fallback path)
    d1 = np.linalg.norm(modal_embedding(k1_r2, W) - modal_embedding(k2, W))
    d2 = np.linalg.norm(modal_embedding(k2_r1, W) - modal_embedding(k1, W))

    if p == 1.0:
        return float(d1 + d2)
    elif p == float('inf'):
        return float(max(d1, d2))
    else:
        return float((d1**p + d2**p)**(1/p))


def simple_dissimilarity(chord1: Tuple[int, np.ndarray], chord2: Tuple[int, np.ndarray]) -> float:
    """
    Compute simple dissimilarity between two chords using Hamming distance.
    
    This is a simpler measure that just counts the number of different
    pitch classes between two chords.
    
    Parameters:
    - chord1, chord2: tuples (root, kind_vec)
    
    Returns:
    - float: Hamming distance between the pitch class sets
    """
    r1, k1 = chord1
    r2, k2 = chord2
    
    pc1 = chord_to_pitch_classes(r1, k1)
    pc2 = chord_to_pitch_classes(r2, k2)
    
    # Symmetric difference gives us the number of different pitch classes
    return len(pc1.symmetric_difference(pc2))


def tonal_dissimilarity(chord1: Tuple[int, np.ndarray], chord2: Tuple[int, np.ndarray]) -> float:
    """
    Compute tonal dissimilarity based on common tones and root distance.
    
    This measure considers both the harmonic content (common tones) and
    the root progression distance in the circle of fifths.
    
    Parameters:
    - chord1, chord2: tuples (root, kind_vec)
    
    Returns:
    - float: tonal dissimilarity measure
    """
    r1, k1 = chord1
    r2, k2 = chord2
    
    pc1 = chord_to_pitch_classes(r1, k1)
    pc2 = chord_to_pitch_classes(r2, k2)
    
    # Common tones
    common_tones = len(pc1.intersection(pc2))
    total_tones = len(pc1.union(pc2))
    
    # Harmonic dissimilarity (fewer common tones = higher dissimilarity)
    harmonic_dissim = 1 - (common_tones / total_tones if total_tones > 0 else 0)
    
    # Root distance in circle of fifths
    # Convert to circle of fifths positions (C=0, G=1, D=2, etc.)
    circle_of_fifths = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]
    fifth_pos1 = circle_of_fifths.index(r1)
    fifth_pos2 = circle_of_fifths.index(r2)
    
    # Minimum distance around the circle
    fifth_distance = min(abs(fifth_pos1 - fifth_pos2), 12 - abs(fifth_pos1 - fifth_pos2))
    root_dissim = fifth_distance / 6  # Normalize to [0, 1]
    
    # Combine harmonic and root dissimilarity
    return 0.7 * harmonic_dissim + 0.3 * root_dissim


def create_identity_system() -> np.ndarray:
    """
    Create an identity musical system (all intervals weighted equally).
    
    Returns:
    - 11x11 identity matrix
    """
    return np.eye(11)


def create_tonal_system() -> np.ndarray:
    """
    Create a tonal musical system that weights intervals by their tonal importance.
    
    Returns:
    - 11x11 diagonal matrix with tonal weights
    """
    # Weights based on tonal hierarchy: perfect 5th, major 3rd, minor 3rd, etc.
    tonal_weights = np.array([
        0.5,   # minor 2nd
        0.8,   # major 2nd  
        1.0,   # minor 3rd
        1.0,   # major 3rd
        0.6,   # perfect 4th
        0.4,   # tritone
        1.2,   # perfect 5th
        0.7,   # minor 6th
        0.8,   # major 6th
        0.9,   # minor 7th
        0.9,   # major 7th
    ])
    
    return np.diag(tonal_weights)


def create_consonance_system() -> np.ndarray:
    """
    Create a diagonal system that weights each interval by its consonance.

    The weight of interval ``i`` (1..11 semitones) is ``1 / log2(a * b)``, where
    ``a:b`` is the interval's just-intonation frequency ratio. ``log2(a * b)`` is
    the Tenney height, a standard measure of interval complexity, so simpler
    (more consonant) intervals receive larger weights. This is a principled,
    parameter-free counterpart to ``create_tonal_system``.

    Returns:
    - 11x11 diagonal matrix of consonance weights
    """
    # just-intonation ratios for intervals 1..11 semitones (minor 2nd .. major 7th)
    ratios = [(16, 15), (9, 8), (6, 5), (5, 4), (4, 3), (45, 32),
              (3, 2), (8, 5), (5, 3), (16, 9), (15, 8)]
    weights = np.array([1.0 / np.log2(a * b) for a, b in ratios])
    return np.diag(weights)