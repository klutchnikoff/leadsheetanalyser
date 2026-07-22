"""
Musical System Analysis Framework for the leadsheetanalyser package.

This module provides a general framework for analyzing chord types within
different musical systems characterized by transformation matrices.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
from scipy.cluster import hierarchy

class MusicalSystem:
    """
    A class representing a musical system for chord analysis.
    
    A musical system is defined by:
    - A transformation matrix W that projects chord types onto modal dimensions
    - Names for each modal dimension
    - Optional metadata about the system
    """
    
    def __init__(self, 
                 matrix: np.ndarray, 
                 mode_names: List[str], 
                 name: str,
                 description: Optional[str] = None):
        """
        Initialize a musical system.
        
        Parameters:
        -----------
        matrix : np.ndarray
            Transformation matrix W where W @ chord_kind gives modal representation
        mode_names : List[str]
            Names of the modal dimensions (columns of the resulting representation)
        name : str
            Name of the musical system (e.g., "Diatonic", "Messiaen")
        description : str, optional
            Description of the theoretical background
        """
        self.matrix = matrix
        self.mode_names = mode_names
        self.name = name
        self.description = description
        
        # Validate dimensions
        if matrix.shape[0] != len(mode_names):
            raise ValueError(f"Matrix has {matrix.shape[0]} lines but {len(mode_names)} mode names provided")
    
    def represent_kinds(self, 
                       chord_kinds: Dict[str, List], 
                       chord_names: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Project chord kinds onto this musical system's modal space.
        
        Parameters:
        -----------
        chord_kinds : Dict[str, List] or List
            Dictionary mapping chord names to pitch class lists, or list of pitch class lists
        chord_names : List[str], optional
            Names for the chord kinds if chord_kinds is a list
            
        Returns:
        --------
        pd.DataFrame
            Representation of chord kinds in this musical system's modal space
        """
        if isinstance(chord_kinds, dict):
            kinds_list = [tuple(k) for k in chord_kinds.values()]
            names_list = list(chord_kinds.keys())
        else:
            kinds_list = [tuple(k) for k in chord_kinds]
            names_list = chord_names or [f"Chord_{i}" for i in range(len(chord_kinds))]
        
        # Project each chord kind onto the modal space
        representations = [self.matrix @ np.array(k) for k in kinds_list]
        
        return pd.DataFrame(
            data=representations,
            columns=self.mode_names,
            index=names_list
        )
    
    def hierarchical_clustering(self, 
                               representation: pd.DataFrame,
                               method: str = 'single',
                               color_threshold: Optional[float] = None,
                               figsize: Tuple[int, int] = (14, 8),
                               colors: Optional[List[str]] = None) -> Tuple[np.ndarray, plt.Figure]:
        """
        Perform hierarchical clustering on the modal representation.
        
        Parameters:
        -----------
        representation : pd.DataFrame
            Result from represent_kinds()
        method : str
            Linkage method for clustering
        color_threshold : float, optional
            Threshold for coloring clusters
        figsize : Tuple[int, int]
            Figure size for the dendrogram
        colors : List[str], optional
            Color palette for the dendrogram
            
        Returns:
        --------
        Tuple[np.ndarray, plt.Figure]
            Linkage matrix and matplotlib figure
        """
        # Default colors for different systems
        if colors is None:
            color_schemes = {
                'Diatonic': ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'],
                'Messiaen': ['#6A994E', '#BC4749', '#F2CC8F', '#81B29A'],
                'default': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            }
            colors = color_schemes.get(self.name, color_schemes['default'])
        
        # Create figure
        fig = plt.figure(figsize=figsize)
        hierarchy.set_link_color_palette(colors)
        
        # Perform clustering
        Z = hierarchy.linkage(representation, method=method)
        
        # Create dendrogram
        hierarchy.dendrogram(
            Z,
            labels=representation.index,
            color_threshold=color_threshold,
            above_threshold_color='grey',
            leaf_rotation=45,
            leaf_font_size=10
        )
        
        # Add threshold line if specified
        if color_threshold is not None:
            plt.axhline(y=color_threshold, color='grey', linestyle='--', alpha=0.7, linewidth=1)
        
        # Styling
        plt.title(f'Hierarchical Clustering: {self.name} Mode Representation', 
                  fontsize=16, fontweight='bold', pad=20)
        plt.ylabel('Distance', fontsize=12)
        plt.xlabel('Chord Types', fontsize=12)
        plt.tight_layout()
        
        return Z, fig
    
    def compare_with_dataset(self, 
                            dataset_kinds: pd.Series, 
                            representation: pd.DataFrame) -> Dict[str, float]:
        """
        Compare the musical system representation with empirical data.
        
        Parameters:
        -----------
        dataset_kinds : pd.Series
            Chord kinds from actual musical data
        representation : pd.DataFrame
            Result from represent_kinds()
            
        Returns:
        --------
        Dict[str, float]
            Coverage statistics
        """
        system_kinds = pd.Series([tuple(k) for k in representation.index])
        
        coverage_pct = (dataset_kinds.isin(system_kinds).sum() / len(dataset_kinds) * 100)
        representation_pct = (system_kinds.isin(dataset_kinds).sum() / len(system_kinds) * 100)
        
        return {
            'dataset_coverage': coverage_pct,
            'system_representation': representation_pct,
            'dataset_unique_kinds': len(dataset_kinds.unique()),
            'system_kinds': len(system_kinds)
        }
    
    def summary_stats(self, representation: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for the representation.
        
        Parameters:
        -----------
        representation : pd.DataFrame
            Result from represent_kinds()
            
        Returns:
        --------
        Dict
            Summary statistics
        """
        return {
            'system_name': self.name,
            'modal_dimensions': len(self.mode_names),
            'chord_types_analyzed': len(representation),
            'representation_shape': representation.shape,
            'mode_names': self.mode_names,
            'description': self.description
        }

# Predefined systems factory
def create_predefined_systems():
    """
    Create the standard musical systems included in leadsheetanalyser.
    
    Returns:
    --------
    Dict[str, MusicalSystem]
        Dictionary of predefined musical systems
    """
    from leadsheetanalyser.constants import (
        W_DIATONIC, DIATONIC_MODE_NAMES,
        W_MESSIAEN, MESSIAEN_MODE_NAMES
    )
    
    systems = {}
    
    # Diatonic system
    systems['diatonic'] = MusicalSystem(
        matrix=W_DIATONIC,
        mode_names=DIATONIC_MODE_NAMES,
        name="Diatonic",
        description="Traditional church modes for analyzing conventional harmonic relationships"
    )
    
    # Messiaen system
    systems['messiaen'] = MusicalSystem(
        matrix=W_MESSIAEN,
        mode_names=MESSIAEN_MODE_NAMES,
        name="Messiaen",
        description="Modes of limited transposition for analyzing symmetrical harmonic structures"
    )
    
    return systems
