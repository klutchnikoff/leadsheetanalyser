"""
Chord Progression Analysis Module

This module provides functions for analyzing chord progressions and extracting
probability distributions based on chord frequencies and patterns.
"""

from typing import List, Tuple, Dict, Set, Union
from collections import Counter
import numpy as np


def analyze_chord_progression_probabilities(
    chord_progression: List[Tuple[int, Union[np.ndarray, List[int]]]]
) -> Dict[str, Union[Set[Tuple[int, tuple]], Dict[Tuple[int, tuple], float]]]:
    """
    Analyze a chord progression and return probability information.
    
    Args:
        chord_progression: List of (root, kind) tuples where:
                          - root: int in {0, 1, ..., 11} (pitch class)
                          - kind: array/list of 11 binary values {0,1}^11 (one-hot encoding)
    
    Returns:
        Dictionary containing:
        - 'atoms': Set of unique (root, kind) tuples representing the probability atoms
        - 'weights': Dictionary mapping (root, kind) to normalized frequencies
        - 'raw_counts': Dictionary mapping (root, kind) to raw occurrence counts
        - 'total_chords': Total number of chords in the progression
    """
    
    # Convert all chords to (root, kind_tuple) format for hashability
    chord_tuples = []
    
    for chord in chord_progression:
        if isinstance(chord, tuple) and len(chord) == 2:
            root, kind = chord
            
            # Validate root
            if not isinstance(root, int) or not (0 <= root <= 11):
                print(f"Warning: Invalid root {root}, must be int in [0,11]")
                continue
            
            # Validate and convert kind to tuple
            if isinstance(kind, np.ndarray):
                kind_array = kind
            elif isinstance(kind, (list, tuple)):
                kind_array = np.array(kind)
            else:
                print(f"Warning: Invalid kind format {type(kind)}")
                continue
            
            # Validate kind dimensions and values
            if kind_array.shape != (11,) or not all(x in [0, 1] for x in kind_array):
                print(f"Warning: Kind must be 11-dim binary vector, got shape {kind_array.shape}")
                continue
            
            kind_tuple = tuple(kind_array)
            chord_tuples.append((root, kind_tuple))
        else:
            print(f"Warning: Chord must be (root, kind) tuple, got {type(chord)}")
            continue
    
    if not chord_tuples:
        return {
            'atoms': set(),
            'weights': {},
            'raw_counts': {},
            'total_chords': 0
        }
    
    # Count occurrences of each (root, kind) pair
    chord_counts = Counter(chord_tuples)
    total_chords = len(chord_tuples)
    
    # Create probability atoms (unique chord types)
    atoms = set(chord_counts.keys())
    
    # Calculate normalized weights (probabilities)
    weights = {chord: count / total_chords for chord, count in chord_counts.items()}
    
    return {
        'atoms': atoms,
        'weights': weights,
        'raw_counts': dict(chord_counts),
        'total_chords': total_chords
    }


def chord_progression_entropy(
    chord_progression: List[Tuple[int, Union[np.ndarray, List[int]]]]
) -> float:
    """
    Calculate the Shannon entropy of a chord progression.
    
    Args:
        chord_progression: List of (root, kind) tuples
        
    Returns:
        Shannon entropy value (higher = more diverse/unpredictable)
    """
    prob_info = analyze_chord_progression_probabilities(chord_progression)
    weights = prob_info['weights']
    
    if not weights:
        return 0.0
    
    # Calculate Shannon entropy: H = -Σ p(x) * log2(p(x))
    entropy = 0.0
    for prob in weights.values():
        if prob > 0:
            entropy -= prob * np.log2(prob)
    
    return entropy


def chord_progression_diversity(
    chord_progression: List[Tuple[int, Union[np.ndarray, List[int]]]]
) -> Dict[str, float]:
    """
    Calculate various diversity metrics for a chord progression.
    
    Args:
        chord_progression: List of chords
        
    Returns:
        Dictionary with diversity metrics:
        - 'unique_chords': Number of unique chord types
        - 'diversity_ratio': Ratio of unique chords to total chords
        - 'entropy': Shannon entropy
        - 'max_entropy': Maximum possible entropy (log2 of unique chords)
        - 'normalized_entropy': Entropy normalized by maximum possible entropy
    """
    prob_info = analyze_chord_progression_probabilities(chord_progression)
    
    unique_chords = len(prob_info['atoms'])
    total_chords = prob_info['total_chords']
    
    if total_chords == 0:
        return {
            'unique_chords': 0,
            'diversity_ratio': 0.0,
            'entropy': 0.0,
            'max_entropy': 0.0,
            'normalized_entropy': 0.0
        }
    
    diversity_ratio = unique_chords / total_chords
    entropy = chord_progression_entropy(chord_progression)
    max_entropy = np.log2(unique_chords) if unique_chords > 1 else 0.0
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
    
    return {
        'unique_chords': unique_chords,
        'diversity_ratio': diversity_ratio,
        'entropy': entropy,
        'max_entropy': max_entropy,
        'normalized_entropy': normalized_entropy
    }


def compare_chord_progressions(
    progression1: List[Tuple[int, Union[np.ndarray, List[int]]]],
    progression2: List[Tuple[int, Union[np.ndarray, List[int]]]]
) -> Dict[str, Union[float, Set]]:
    """
    Compare two chord progressions based on their probability distributions.
    
    Args:
        progression1: First chord progression
        progression2: Second chord progression
        
    Returns:
        Dictionary with comparison metrics:
        - 'jaccard_similarity': Jaccard similarity of chord sets
        - 'common_chords': Set of chords present in both progressions
        - 'unique_to_first': Set of chords unique to first progression
        - 'unique_to_second': Set of chords unique to second progression
        - 'kullback_leibler_div': KL divergence (if applicable)
    """
    prob1 = analyze_chord_progression_probabilities(progression1)
    prob2 = analyze_chord_progression_probabilities(progression2)
    
    atoms1 = prob1['atoms']
    atoms2 = prob2['atoms']
    
    # Jaccard similarity
    intersection = atoms1.intersection(atoms2)
    union = atoms1.union(atoms2)
    jaccard_similarity = len(intersection) / len(union) if union else 0.0
    
    # Set differences
    common_chords = intersection
    unique_to_first = atoms1 - atoms2
    unique_to_second = atoms2 - atoms1
    
    # KL divergence (only for chords present in both)
    kl_divergence = None
    if common_chords:
        try:
            kl_div = 0.0
            for chord in common_chords:
                p1 = prob1['weights'].get(chord, 0)
                p2 = prob2['weights'].get(chord, 0)
                if p1 > 0 and p2 > 0:
                    kl_div += p1 * np.log(p1 / p2)
            kl_divergence = kl_div
        except Exception:
            kl_divergence = None
    
    return {
        'jaccard_similarity': jaccard_similarity,
        'common_chords': common_chords,
        'unique_to_first': unique_to_first,
        'unique_to_second': unique_to_second,
        'kullback_leibler_div': kl_divergence
    }


def chord_transition_probabilities(
    chord_progression: List[Tuple[int, Union[np.ndarray, List[int]]]]
) -> Dict[Tuple[Tuple[int, tuple], Tuple[int, tuple]], float]:
    """
    Calculate transition probabilities between consecutive chords.
    
    Args:
        chord_progression: List of (root, kind) tuples
        
    Returns:
        Dictionary mapping (chord1, chord2) pairs to transition probabilities
    """
    # Convert to (root, kind) format with validation
    chord_tuples = []
    
    for chord in chord_progression:
        if isinstance(chord, tuple) and len(chord) == 2:
            root, kind = chord
            
            # Validate root
            if not isinstance(root, int) or not (0 <= root <= 11):
                continue
            
            # Convert kind to tuple
            if isinstance(kind, np.ndarray):
                kind_array = kind
            elif isinstance(kind, (list, tuple)):
                kind_array = np.array(kind)
            else:
                continue
            
            # Validate kind
            if kind_array.shape != (11,) or not all(x in [0, 1] for x in kind_array):
                continue
            
            kind_tuple = tuple(kind_array)
            chord_tuples.append((root, kind_tuple))
    
    # Count transitions
    transition_counts = Counter()
    for i in range(len(chord_tuples) - 1):
        transition = (chord_tuples[i], chord_tuples[i + 1])
        transition_counts[transition] += 1
    
    # Calculate probabilities
    total_transitions = len(chord_tuples) - 1
    transition_probs = {
        transition: count / total_transitions 
        for transition, count in transition_counts.items()
    }
    
    return transition_probs


def print_progression_analysis(
    chord_progression: List[Tuple[int, Union[np.ndarray, List[int]]]],
    progression_name: str = "Chord Progression"
) -> None:
    """
    Print a comprehensive analysis of a chord progression.
    
    Args:
        chord_progression: List of (root, kind) tuples to analyze
        progression_name: Name for the progression (for display)
    """
    print(f"\n=== {progression_name} Analysis ===")
    
    # Basic probability analysis
    prob_info = analyze_chord_progression_probabilities(chord_progression)
    print(f"Total chords: {prob_info['total_chords']}")
    print(f"Unique chord types: {len(prob_info['atoms'])}")
    
    # Diversity metrics
    diversity = chord_progression_diversity(chord_progression)
    print(f"Diversity ratio: {diversity['diversity_ratio']:.3f}")
    print(f"Shannon entropy: {diversity['entropy']:.3f}")
    print(f"Normalized entropy: {diversity['normalized_entropy']:.3f}")
    
    # Most common chords
    print("\nChord frequencies:")
    sorted_chords = sorted(prob_info['weights'].items(), key=lambda x: x[1], reverse=True)
    for (root, kind), weight in sorted_chords[:5]:  # Top 5
        print(f"  Root {root}, Kind {kind[:3]}...: {weight:.3f} ({prob_info['raw_counts'][(root, kind)]} times)")
    
    # Transition analysis
    transitions = chord_transition_probabilities(chord_progression)
    if transitions:
        print(f"\nMost common transitions:")
        sorted_transitions = sorted(transitions.items(), key=lambda x: x[1], reverse=True)
        for (chord1, chord2), prob in sorted_transitions[:3]:  # Top 3
            print(f"  {chord1} -> {chord2}: {prob:.3f}")


# Example usage and testing
if __name__ == "__main__":
    # Example chord progression using leadsheetanalyser format
    # (root, 11-dim binary kind vector)
    
    # D:min7 = (2, [0,0,1,0,0,0,1,0,0,1,0])
    # G:7    = (7, [0,0,0,1,0,0,1,0,0,1,0]) 
    # C:maj7 = (0, [0,0,0,1,0,0,1,0,0,0,1])
    
    example_progression = [
        (2, [0,0,1,0,0,0,1,0,0,1,0]),  # D:min7
        (7, [0,0,0,1,0,0,1,0,0,1,0]),  # G:7
        (0, [0,0,0,1,0,0,1,0,0,0,1]),  # C:maj7
        (0, [0,0,0,1,0,0,1,0,0,0,1]),  # C:maj7
    ]
    
    print("Example Analysis:")
    print_progression_analysis(example_progression, "ii-V-I in C (leadsheetanalyser format)")
    
    # Test with numpy arrays
    jazz_progression = [
        (0, np.array([0,0,0,1,0,0,1,0,0,0,1])),  # C:maj7
        (9, np.array([0,0,1,0,0,0,1,0,0,1,0])),  # A:min7
        (2, np.array([0,0,1,0,0,0,1,0,0,1,0])),  # D:min7
        (7, np.array([0,0,0,1,0,0,1,0,0,1,0])),  # G:7
    ]
    print_progression_analysis(jazz_progression, "Jazz Progression (with numpy arrays)")
