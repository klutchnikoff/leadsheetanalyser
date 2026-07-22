# Package Architecture & API Reference

This document provides detailed technical documentation for the leadsheetanalyser package architecture and API.

## Package Structure

```
leadsheetanalyser/
├── __init__.py              # Main package initialization and API
├── constants.py             # All musical constants and data structures
├── chords.py               # Core chord processing and manipulation
├── scales.py               # Scale and mode analysis functions
├── chord_dissimilarities.py # Advanced chord relationship analysis
└── data_processing.py      # Musical data loading and processing utilities
```

**Note**: All legacy modules have been removed. The package now follows a clean, purpose-driven architecture.

## Module Organization

### 1. `constants.py` 
**Purpose**: Central repository for all musical constants and data structures
- **Note Mappings**: `NOTE_TO_PC`, `PC_TO_NOTE_FLAT`, `PC_TO_NOTE_SHARP` (17-17 note mappings)
- **Chord Definitions**: `CHORD_SHORTHANDS` (19 types), `SIMPLIFIED_CHORD_NAMES` (55 mappings)
- **Modal Systems**: `W_DIATONIC` (7 modes), `W_MESSIAEN` (15 modes)
- **Utility Constants**: `CHORD_NAME_CLEANUP_STRINGS`, mode name lists

### 2. `chords.py` 
**Purpose**: Comprehensive chord processing and manipulation
- **Core Parsing**: `map_root()`, `map_chord()`, `map_kind()` - Convert Harte notation to internal representation
- **Enhanced Parsing**: `parse_shorthand_chord()` - Handle shorthand notation (Am, C7, etc.)
- **Conversion Utilities**: `chord_to_pitch_classes()`, `pitch_classes_to_chord()`, `chord_name_to_tuple()`
- **Naming & Display**: `chord_nice_name()`, `to_note_list()` - Human-readable chord representation
- **Transformation**: `transpose_chord()`, `transpose_to_c()` - Chord transposition
- **Utilities**: `closest_fraction()`, `key_retriever()` - Support functions

### 3. `scales.py`
**Purpose**: Advanced scale and mode analysis
- **Core Analysis**: `compute_transposition_number()`, `analyze_mode_properties()`
- **Symmetry Analysis**: `get_scale_symmetry_axis()` - Find scale symmetries
- **Scale Construction**: `scale_from_intervals()`, `generate_mode_variants()`
- **Classification**: `identify_mode()` - Recognize common scales and modes

### 4. `chord_dissimilarities.py`
**Purpose**: Advanced harmonic relationship analysis
- **Core Dissimilarity**: `dissimilarities()`, `simple_dissimilarity()`, `tonal_dissimilarity()`
- **Chord Manipulation**: `reinterpret_chord()` - Change chord root perspective
- **Musical Systems**: `create_identity_system()`, `create_tonal_system()` - Weight matrix creation
- **Validation**: `validate_chord_kind()`, `validate_musical_system()`, `validate_root()`
- **Utilities**: Shared pitch class and chord conversion functions

### 5. `data_processing.py`
**Purpose**: Musical dataset loading, processing, and analysis
- **Data Loading**: `load_and_process_dataset()`, `process_song_data()` - JAMS format support
- **Filtering**: `filter_songs_by_criteria()` - Dataset curation
- **Statistics**: `extract_chord_statistics()`, `create_chord_transition_matrix()` - Analysis tools

## Development Guidelines

### For New Development
1. **Follow module organization** - Add functions to the appropriate module by domain
2. **Use modern Python practices** - Type hints, comprehensive docstrings, clean code
3. **Maintain API consistency** - Follow existing patterns for function naming and structure
4. **Test thoroughly** - Each new function should have corresponding tests

### Code Organization Principles
1. **Single Responsibility** - Each module handles one musical domain
2. **Clean Dependencies** - Constants → Chords → Scales/Dissimilarities → Data Processing
3. **Public API Clarity** - Important functions exported at package level
4. **Documentation First** - Clear docstrings with examples and type information

## Package Statistics

- **5 Core Modules**: Each with focused responsibility
- **38 Total Functions**: Distributed logically across domains (not counting constants module)
- **10 Constant Collections**: 190+ musical constants and mappings  
- **44 Public API Symbols**: Available at package level for convenience
- **Zero Legacy Code**: Clean, modern architecture with no backward compatibility overhead

### Detailed Function Distribution:
- **chords.py**: 15 functions (chord processing, parsing, transformation)
- **scales.py**: 6 functions (scale analysis, mode identification)
- **chord_dissimilarities.py**: 12 functions (harmonic relationship analysis)
- **data_processing.py**: 5 functions (dataset loading and processing)
- **constants.py**: 10 major constant collections

## Future Roadmap

1. **Performance Optimization**: Profile and optimize critical paths
2. **Extended Functionality**: Add rhythm analysis, voice leading, harmonic progression analysis
3. **Enhanced Data Support**: Support for additional musical formats (MusicXML, MIDI)
4. **Machine Learning Integration**: Chord prediction, style analysis capabilities
5. **Visualization Tools**: Interactive chord and scale visualization utilities
