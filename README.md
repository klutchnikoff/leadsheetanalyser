# LeadSheet Analyser 🎵

A specialized Python package for leadsheet analysis using chord dissimilarity metrics.

## Features

- **🎼 Chord Processing**: Parse both Harte notation (`A:min`) and shorthand (`Am`)
- **📐 Modal Embeddings**: Map chords into continuous geometric spaces using musical systems (e.g. Pythagorean, Messiaen)
- **🧮 Optimal Transport**: Compute alignment and distance between entire chord progressions
- **💾 Data Processing**: Tools for musical datasets (JAMS format support)
- **📚 Rich Constants**: Comprehensive musical constants and predefined systems

## Quick Start

```python
import leadsheetanalyser

# Parse chords (supports multiple formats)
chord = leadsheetanalyser.map_chord("Am")  # Shorthand
chord = leadsheetanalyser.map_chord("A:min")  # Harte notation

# Analyze chord relationships in a musical system
from leadsheetanalyser.chord_dissimilarities import modal_dissimilarity, create_identity_system
c_maj = leadsheetanalyser.chord_name_to_tuple("C:maj")
f_maj = leadsheetanalyser.chord_name_to_tuple("F:maj")
system = create_identity_system()
dissimilarity = modal_dissimilarity(c_maj, f_maj, system, p=1.0)

# Compute Optimal Transport distance between two songs
from leadsheetanalyser.song_distance import song_distance
song1 = [c_maj, f_maj, c_maj]
song2 = [c_maj, leadsheetanalyser.chord_name_to_tuple("G:7"), c_maj]
dist = song_distance(song1, song2, W=system, p=1.0)
```

## Package Structure

```
leadsheetanalyser/
├── chords.py                # Chord processing and parsing
├── chord_dissimilarities.py # Modal embeddings and chord distances
├── song_distance.py         # Optimal transport between progressions
├── musical_systems.py       # Musical system definitions (W matrix)
├── system_analysis.py       # Comparative analysis and clustering
├── scales.py                # Scale analysis and properties
├── constants.py             # Predefined systems and mappings
└── data_processing.py       # Dataset tools (JAMS)
```

## Installation & Setup

```bash
# Install from PyPI
pip install leadsheetanalyser

# Or install from source for development
git clone https://github.com/USERNAME/leadsheetanalyser.git
cd leadsheetanalyser
pip install -e .

# Set up datasets (downloads from GitHub releases - fast & efficient)
python scripts/download_data.py
```

For complete data setup instructions, see **[DATA.md](DATA.md)**.

## Testing

```bash
# Run all tests
python -m pytest tests/

# Or use the provided script
python tests/run_tests.py
```

## Dependencies

Core dependencies (automatically installed with `pip install -e .`):
- `numpy`, `scipy` - Scientific computing and clustering
- `pandas` - Data manipulation
- `pot` - Python Optimal Transport
- `jams` - Musical annotation format
- `music21`, `harte-library` - Music and chord processing
- `matplotlib`, `seaborn` - Visualization

## Documentation

- **[DATA.md](DATA.md)** - Complete data setup and management guide
- **[ORGANIZATION.md](ORGANIZATION.md)** - Package architecture and API reference

## License

MIT License - see [LICENSE](LICENSE) for details.
