# Data Management Guide

This document explains how to handle the ChoCo dataset for this project.

## 📊 Dataset Information

- **Source**: ChoCo (Chord Corpus) - https://github.com/smashub/choco
- **Size**: ~2000+ JAMS files (chord annotations)
- **Location**: `data/jams_files/`

## 🏗️ Data Setup

**Prerequisites**: Make sure you've already cloned this repository and installed dependencies (`pip install -e .`).

### Automatic Setup (Recommended)

```bash
# One command to download and set up data (from GitHub releases)
python scripts/download_data.py

# Verify setup
ls data/jams_files/ | wc -l
# Should show 1000+ files
```

### Manual Setup Options

```bash
# Option 1: Download from specific release
python scripts/download_data.py --method release --release data-v0.1.0

# Option 2: Clone ChoCo repository directly (full repository)
python scripts/download_data.py --method clone

# Option 3: Symlink to existing ChoCo (if you already have it)
python scripts/download_data.py --method symlink --choco-path /path/to/your/choco

# Option 4: Manual git operations (for full control)
mkdir -p data
cd data/
git clone https://github.com/smashub/choco.git
ln -s choco/partitions/ireal-pro/jams jams_files
cd ..
```

## 🧱 Build the processed corpus

`download_data.py` fetches the JAMS annotations.  The analysis scripts read
processed pickles, which are **not** distributed: they are gitignored and absent
from the wheel.  Build them once the JAMS are in place.

```bash
# The corpus the article studies: the Real Book partition
python scripts/build_corpus.py

# Check a rebuild against the pickle already on disk, without overwriting it
python scripts/build_corpus.py --verify

# Any other ChoCo partition
python scripts/build_corpus.py --partition ireal-pro
```

Expected output for the default partition:

```
  2846 metadata rows for real-book
  2846 songs processed
  172802 chord tokens
```

Only the *Real Book* side needs a pickle.  The common-practice side of the
article (`when-in-rome`) is read straight from `data/jams_files`, so no build
step applies to it.

Note on `--verify`: it compares values, not storage.  pandas 3 infers the `str`
dtype for text columns that earlier versions left as `object`, so a faithful
rebuild would otherwise fail against a pickle written before that change.

## 📋 Data Management Best Practices

### 1. Working with the Data

```python
# Example: Loading JAMS files
import os
import jams

# Data should be in this location
jams_folder = "data/jams_files"

# Verify data is available
if not os.path.exists(jams_folder):
    print("⚠️  JAMS data not found. Please follow setup instructions in DATA.md")
    
# Process JAMS files
for filename in os.listdir(jams_folder):
    if filename.endswith('.jams'):
        filepath = os.path.join(jams_folder, filename)
        jam = jams.load(filepath)
        # Your processing code here...
```

### 2. Testing with Limited Data

For development and testing, you can work with a subset:

```python
# Use only first 10 files for quick testing
test_files = [f for f in os.listdir("data/jams_files") if f.endswith('.jams')][:10]
```

## 🚀 GitLab CI/CD Considerations

### Pipeline Configuration

For GitLab CI/CD, you can set up data downloading in your pipeline:

```yaml
# .gitlab-ci.yml example
stages:
  - setup
  - test

setup_data:
  stage: setup
  script:
    - python scripts/download_data.py  # Uses release method by default
  cache:
    paths:
      - data/jams_files/  # Cache the downloaded files
  artifacts:
    paths:
      - data/jams_files/
    expire_in: 1 hour

test:
  stage: test
  dependencies:
    - setup_data
  script:
    - pip install -e .
    - python -m pytest tests/
```

## 📁 Directory Structure

```
data/
├── meta.csv                 # Metadata (small files)
├── music.pkl               # Processed data (small files)
├── jams_files/             # JAMS files (from release download or symlink)
│   ├── ireal-pro_0.jams
│   ├── ireal-pro_1.jams
│   └── ...
└── choco/                  # Full ChoCo repository (only with --method clone)
    ├── README.md
    ├── partitions/
    │   └── ireal-pro/
    │       └── jams/       # Original JAMS files
    └── ...
```

## 🚀 Quick Start Examples

### Method 1: Release Download (Recommended)
```bash
# Automatic setup - downloads only data files from GitHub releases
python scripts/download_data.py

# Download from specific release
python scripts/download_data.py --method release --release data-v0.1.0

# Verify setup
ls data/jams_files/ | wc -l
# Should show 1000+ files
```

### Method 2: Full Repository Clone
```bash
# Download full ChoCo repository (larger download)
python scripts/download_data.py --method clone

# Update existing repository
python scripts/download_data.py --method clone --update
```

### Method 3: Symlink to Existing ChoCo
```bash
# If you already have ChoCo cloned elsewhere
python scripts/download_data.py --method symlink --choco-path /path/to/your/choco
```

## 🔄 Updating Data

### For Release Downloads (Default Method)
```bash
# Re-download latest data
python scripts/download_data.py

# Download specific release
python scripts/download_data.py --method release --release v1.0.0
```

### For Repository Clone Method
```bash
# Update existing ChoCo repository
python scripts/download_data.py --method clone --update

# Or manually
cd data/choco
git pull origin main
cd ../..
```

### Verify Updates
```bash
# Check for new files
ls data/jams_files/ | wc -l
```

## ⚠️ Important Notes

1. **Default Method**: Downloads data files from GitHub releases (fast, efficient)
2. **Data Location**: Data files are stored directly in `data/jams_files/`
3. **No Git Required**: Default method works without git installation
4. **Updates**: Re-run the script to get the latest data
5. **Alternative Methods**: Full repository clone available for advanced users

## 🆘 Troubleshooting

### Data Not Found?

```bash
# Check if data directory exists
ls -la data/

# Check if JAMS files exist
ls -la data/jams_files/

# Re-run download script
python scripts/download_data.py

# Try specific release if default fails
python scripts/download_data.py --method release --release data-v0.1.0
```

### Download Issues?

```bash
# Check internet connection and try again
python scripts/download_data.py

# Use clone method as fallback
python scripts/download_data.py --method clone
```

### For Clone Method - Symlink Issues?

```bash
# Remove broken symlink
rm data/jams_files

# Recreate symlink
cd data
ln -s choco/partitions/ireal-pro/jams jams_files
cd ..
```

## 📞 Support

If you encounter issues with data access:
1. Verify the download script runs successfully
2. Check that the ChoCo repository is accessible
3. Ensure symlinks are created properly
4. Consider using alternative data distribution methods if needed
