"""
LeadSheet Analyser Package
A specialized package for leadsheet analysis using chord dissimilarity metrics.

This package provides tools for:
- Chord processing and analysis
- Scale and mode analysis
- Chord dissimilarity computation
- Musical data processing
- Musical constants and utilities
"""

# =============================================================================
# MODULE IMPORTS
# =============================================================================

# Import main modules to make them available at package level
from . import constants
from . import chords
from . import scales
from . import chord_dissimilarities
from . import data_processing
from . import data_access
from . import musical_systems
from . import system_analysis

# =============================================================================
# CORE FUNCTIONS - Make key functions available directly
# =============================================================================

# Chord processing functions
from .chords import (
    map_kind,
    map_root,
    map_chord,
    chord_nice_name,
    to_note_list,
    key_retriever,
    chord_to_pitch_classes,
    pitch_classes_to_chord,
    transpose_chord,
    transpose_to_c,
    closest_fraction,
    chord_name_to_tuple,
)

# Scale analysis functions
from .scales import (
    compute_transposition_number,
    get_scale_symmetry_axis,
    analyze_mode_properties,
    scale_from_intervals,
    identify_mode,
    generate_mode_variants,
)

# Chord dissimilarity functions
from .chord_dissimilarities import (
    reinterpret_chord,
    modal_embedding,
    modal_dissimilarity,
    simple_dissimilarity,
    tonal_dissimilarity,
    chord_name_to_tuple,
    create_identity_system,
    create_tonal_system,
)

# Data processing functions
from .data_processing import (
    process_song_data,
    load_and_process_dataset,
    filter_songs_by_criteria,
    extract_chord_statistics,
    create_chord_transition_matrix,
)

# Data access functions
from .data_access import (
    load_music_data,
    load_metadata,
    get_jams_files,
    check_data_availability,
    print_data_summary,
    get_sample_data,
)

# Musical Systems Analysis
from .musical_systems import (
    MusicalSystem,
    create_predefined_systems,
)

from .system_analysis import (
    comparative_analysis,
    plot_comparative_clustering,
    create_system_comparison_table,
    analyze_system_correlations,
    example_custom_system,
)

# Constants
from .constants import (
    NOTE_TO_PC,
    PC_TO_NOTE_FLAT,
    PC_TO_NOTE_SHARP,
    CHORD_SHORTHANDS,
    SIMPLIFIED_CHORD_NAMES,
    CHORD_NAME_CLEANUP_STRINGS,
    W_DIATONIC,
    DIATONIC_MODE_NAMES,
    W_MESSIAEN,
    MESSIAEN_MODE_NAMES,
    BASIC_CHORD_KINDS,
)

__version__ = "0.2.0"
__all__ = [
    # =============================================================================
    # MODULES
    # =============================================================================
    "constants",
    "chords", 
    "scales",
    "chord_dissimilarities",
    "data_processing",
    
    # =============================================================================
    # CHORD PROCESSING FUNCTIONS
    # =============================================================================
    "map_kind",
    "map_root", 
    "map_chord",
    "chord_nice_name",
    "to_note_list",
    "key_retriever",
    "chord_to_pitch_classes",
    "pitch_classes_to_chord",
    "transpose_chord",
    "transpose_to_c",
    "closest_fraction",
    "chord_name_to_tuple",
    
    # =============================================================================
    # SCALE ANALYSIS FUNCTIONS
    # =============================================================================
    "compute_transposition_number",
    "get_scale_symmetry_axis",
    "analyze_mode_properties",
    "scale_from_intervals",
    "identify_mode",
    "generate_mode_variants",
    
    # =============================================================================
    # CHORD DISSIMILARITY FUNCTIONS
    # =============================================================================
    "reinterpret_chord",
    "modal_embedding",
    "modal_dissimilarity",
    "simple_dissimilarity", 
    "tonal_dissimilarity",
    "chord_name_to_tuple",
    "create_identity_system",
    "create_tonal_system",
    
    # =============================================================================
    # DATA PROCESSING FUNCTIONS
    # =============================================================================
    "process_song_data",
    "load_and_process_dataset",
    "filter_songs_by_criteria",
    "extract_chord_statistics",
    "create_chord_transition_matrix",
    
    # =============================================================================
    # CONSTANTS
    # =============================================================================
    "NOTE_TO_PC",
    "PC_TO_NOTE_FLAT",
    "PC_TO_NOTE_SHARP",
    "CHORD_SHORTHANDS",
    "SIMPLIFIED_CHORD_NAMES",
    "CHORD_NAME_CLEANUP_STRINGS",
    "W_DIATONIC",
    "DIATONIC_MODE_NAMES", 
    "W_MESSIAEN",
    "MESSIAEN_MODE_NAMES",
]