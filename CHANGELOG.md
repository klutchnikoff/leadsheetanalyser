# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-08-04

### Added
- 🎼 **Core Chord Processing**: Complete chord parsing and analysis system
  - Support for both Harte notation (`A:min`) and shorthand (`Am`)
  - Chord to pitch class conversion
  - Transposition utilities
  
- 📊 **Musical Systems Framework**: Extensible harmonic analysis system
  - Pythagorean modes representation
  - Messiaen modes of limited transposition
  - Hierarchical clustering with custom systems
  - Comparative analysis tools
  
- 🎵 **Scale Analysis**: Comprehensive scale and mode analysis
  - Mode property analysis
  - Symmetry detection
  - Scale relationship metrics
  
- 📈 **Chord Dissimilarity Metrics**: Advanced harmonic relationship analysis
  - Simple dissimilarity measures
  - Custom distance functions
  - Harmonic clustering capabilities
  
- 💾 **Data Processing**: Tools for musical datasets
  - JAMS format support
  - Data loading utilities with error handling
  - Statistical extraction tools
  
- 📚 **Rich Musical Constants**: Comprehensive musical data
  - Basic chord kinds definitions
  - Scale mappings
  - Musical intervals and relationships
  
- 📖 **Documentation & Examples**:
  - Comprehensive Quarto notebooks
  - Data import workflows
  - Harmonic analysis examples
  - Package usage demonstrations

### Package Structure
```
leadsheetanalyser/
├── __init__.py
├── constants.py             # Musical constants and mappings
├── chords.py               # Chord processing (15+ functions)
├── scales.py               # Scale analysis (6+ functions)
├── chord_dissimilarities.py # Harmonic analysis (12+ functions)
├── data_processing.py      # Dataset tools (5+ functions)
├── musical_systems.py     # Musical Systems framework
├── system_analysis.py     # Comparative analysis tools
└── data_access.py         # Data loading utilities
```

### Dependencies
- pandas>=1.3.0
- jams>=0.3.4
- music21>=6.0.0
- numpy>=1.20.0
- scipy>=1.7.0
- matplotlib>=3.3.0
- seaborn>=0.11.0

### Python Support
- Python 3.7+
- Tested on Python 3.8, 3.9, 3.10, 3.11

---

**Note**: This is the initial release of leadsheetanalyser. Future versions will expand functionality while maintaining backward compatibility where possible.
