"""
Data access utilities for the leadsheetanalyser package.

This module provides convenient functions to access package data.
"""

import os
import pandas as pd
import pickle
from pathlib import Path
from typing import Optional, List

def get_package_data_path() -> Path:
    """Get the path to the package data directory."""
    # Get the directory where this module is located
    package_dir = Path(__file__).parent.parent
    data_dir = package_dir / "data"
    return data_dir

def load_music_data() -> pd.DataFrame:
    """Load the main processed music dataset."""
    data_path = get_package_data_path() / "music.pkl"
    if not data_path.exists():
        raise FileNotFoundError(
            f"Music data not found at {data_path}. "
            "Please ensure the data has been properly set up."
        )
    return pd.read_pickle(data_path)

def load_metadata() -> pd.DataFrame:
    """Load the metadata CSV file."""
    data_path = get_package_data_path() / "meta.csv"
    if not data_path.exists():
        raise FileNotFoundError(
            f"Metadata not found at {data_path}. "
            "Please ensure the data has been properly set up."
        )
    return pd.read_csv(data_path)

def get_jams_files(limit: Optional[int] = None) -> List[Path]:
    """
    Get list of available JAMS files.
    
    Parameters:
    -----------
    limit : int, optional
        Maximum number of files to return. Useful for testing.
        
    Returns:
    --------
    List[Path]
        List of paths to JAMS files
    """
    jams_dir = get_package_data_path() / "jams_files"
    if not jams_dir.exists():
        raise FileNotFoundError(
            f"JAMS directory not found at {jams_dir}. "
            "Please run the data setup script first."
        )
    
    jams_files = list(jams_dir.glob("*.jams"))
    
    if limit is not None:
        jams_files = jams_files[:limit]
        
    return jams_files

def check_data_availability() -> dict:
    """
    Check which data files are available.
    
    Returns:
    --------
    dict
        Dictionary indicating availability of different data types
    """
    data_dir = get_package_data_path()
    
    availability = {
        "music_pkl": (data_dir / "music.pkl").exists(),
        "metadata_csv": (data_dir / "meta.csv").exists(),
        "jams_files": (data_dir / "jams_files").exists(),
        "jams_count": 0
    }
    
    if availability["jams_files"]:
        jams_files = list((data_dir / "jams_files").glob("*.jams"))
        availability["jams_count"] = len(jams_files)
    
    return availability

# Example usage functions
def get_sample_data(n_songs: int = 10) -> pd.DataFrame:
    """Get a sample of the music data for testing."""
    music = load_music_data()
    return music.head(n_songs)

def print_data_summary():
    """Print a summary of available data."""
    availability = check_data_availability()
    
    print("📊 LeadSheet Analyser Data Summary")
    print("=" * 40)
    print(f"✅ Music dataset: {'Available' if availability['music_pkl'] else '❌ Missing'}")
    print(f"✅ Metadata: {'Available' if availability['metadata_csv'] else '❌ Missing'}")
    print(f"✅ JAMS files: {availability['jams_count']} files available")
    
    if availability['music_pkl']:
        try:
            music = load_music_data()
            print(f"📈 Dataset size: {len(music)} songs")
            print(f"🎭 Genres: {music['genre'].nunique()} unique genres")
            print(f"🎵 Artists: {music['artist'].nunique()} unique artists")
        except Exception as e:
            print(f"⚠️  Error loading music data: {e}")
