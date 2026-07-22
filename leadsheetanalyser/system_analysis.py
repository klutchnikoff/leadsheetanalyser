"""
High-level analysis functions using the musical systems framework.

This module provides convenient functions for comparative analysis across
multiple musical systems.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple
from scipy.cluster import hierarchy
from .musical_systems import MusicalSystem, create_predefined_systems

def comparative_analysis(chord_kinds: Dict[str, List], 
                        systems: Optional[Dict[str, MusicalSystem]] = None,
                        clustering_method: str = 'single') -> Dict[str, pd.DataFrame]:
    """
    Perform comparative analysis across multiple musical systems.
    
    Parameters:
    -----------
    chord_kinds : Dict[str, List]
        Dictionary mapping chord names to pitch class lists
    systems : Dict[str, MusicalSystem], optional
        Musical systems to analyze. If None, uses predefined systems.
    clustering_method : str
        Method for hierarchical clustering
        
    Returns:
    --------
    Dict[str, pd.DataFrame]
        Representations for each musical system
    """
    if systems is None:
        systems = create_predefined_systems()
    
    representations = {}
    
    for system_name, system in systems.items():
        print(f"\n🎼 {system.name} System Analysis:")
        print(f"Description: {system.description}")
        
        # Create representation
        repr_df = system.represent_kinds(chord_kinds)
        representations[system_name] = repr_df
        
        # Summary stats
        stats = system.summary_stats(repr_df)
        print(f"Modal dimensions: {stats['modal_dimensions']}")
        print(f"Chord types analyzed: {stats['chord_types_analyzed']}")
        
    return representations

def plot_comparative_clustering(representations: Dict[str, pd.DataFrame],
                               systems: Optional[Dict[str, MusicalSystem]] = None,
                               figsize: Tuple[int, int] = (16, 6)) -> plt.Figure:
    """
    Create side-by-side clustering plots for multiple systems.
    
    Parameters:
    -----------
    representations : Dict[str, pd.DataFrame]
        Representations from comparative_analysis()
    systems : Dict[str, MusicalSystem], optional
        Musical systems (for styling)
    figsize : Tuple[int, int]
        Figure size
        
    Returns:
    --------
    plt.Figure
        Matplotlib figure with subplots
    """
    if systems is None:
        systems = create_predefined_systems()
    
    n_systems = len(representations)
    fig, axes = plt.subplots(1, n_systems, figsize=figsize)
    
    if n_systems == 1:
        axes = [axes]
    
    for i, (system_name, repr_df) in enumerate(representations.items()):
        system = systems.get(system_name)
        
        # Perform clustering for this system
        if system:
            # Use the system's clustering method but plot on subplot
            plt.sca(axes[i])
            Z, _ = system.hierarchical_clustering(repr_df, figsize=(1, 1))  # Small fig, we'll use subplot
            plt.close()  # Close the individual figure
            
            # Recreate on subplot
            plt.sca(axes[i])
            hierarchy.dendrogram(
                Z,
                labels=repr_df.index,
                leaf_rotation=45,
                leaf_font_size=8
            )
            axes[i].set_title(f'{system.name} System', fontweight='bold')
            axes[i].set_ylabel('Distance' if i == 0 else '')
            axes[i].set_xlabel('Chord Types')
    
    plt.tight_layout()
    return fig

def create_system_comparison_table(representations: Dict[str, pd.DataFrame],
                                  systems: Optional[Dict[str, MusicalSystem]] = None) -> pd.DataFrame:
    """
    Create a comparison table of different musical systems.
    
    Parameters:
    -----------
    representations : Dict[str, pd.DataFrame]
        Representations from comparative_analysis()
    systems : Dict[str, MusicalSystem], optional
        Musical systems
        
    Returns:
    --------
    pd.DataFrame
        Comparison table
    """
    if systems is None:
        systems = create_predefined_systems()
    
    comparison_data = []
    
    for system_name, repr_df in representations.items():
        system = systems.get(system_name)
        if system:
            stats = system.summary_stats(repr_df)
            comparison_data.append({
                'System': system.name,
                'Modal Dimensions': stats['modal_dimensions'],
                'Chord Types': stats['chord_types_analyzed'],
                'Description': stats['description'][:50] + "..." if len(stats['description']) > 50 else stats['description']
            })
    
    return pd.DataFrame(comparison_data)

def analyze_system_correlations(representations: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Analyze correlations between different musical systems.
    
    Parameters:
    -----------
    representations : Dict[str, pd.DataFrame]
        Representations from comparative_analysis()
        
    Returns:
    --------
    pd.DataFrame
        Correlation matrix between systems
    """
    # For correlation analysis, we need to ensure all systems analyze the same chords
    common_chords = None
    for repr_df in representations.values():
        if common_chords is None:
            common_chords = set(repr_df.index)
        else:
            common_chords = common_chords.intersection(set(repr_df.index))
    
    if not common_chords:
        raise ValueError("No common chords found across systems")
    
    common_chords = sorted(list(common_chords))
    
    # Create flattened representations for correlation
    flat_representations = {}
    for system_name, repr_df in representations.items():
        # Select common chords and flatten
        common_repr = repr_df.loc[common_chords]
        flat_representations[system_name] = common_repr.values.flatten()
    
    # Create correlation matrix
    correlation_df = pd.DataFrame(flat_representations).corr()
    
    return correlation_df

# Example usage function
def example_custom_system():
    """
    Example of how to create a custom musical system.
    """
    # Example: Simple major/minor system
    # This is a simplified example - you would define your own matrix
    custom_matrix = np.array([
        [1, 0],  # Major quality
        [0, 1],  # Minor quality
    ])
    
    custom_system = MusicalSystem(
        matrix=custom_matrix,
        mode_names=['Major_Component', 'Minor_Component'],
        name='Major-Minor',
        description='Simple major/minor harmonic analysis'
    )
    
    return custom_system
