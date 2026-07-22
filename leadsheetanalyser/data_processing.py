"""
Data processing functions for the leadsheetanalyser package.

This module handles loading, processing, and transforming musical data
from various sources including JAMS files and other formats.
"""

import os
import jams
import pandas as pd
from typing import List, Dict, Any, Optional


def _annotation_by_namespace(jam, namespace: str):
    """First annotation of the given JAMS namespace, or None."""
    for annotation in jam.annotations:
        if annotation.namespace == namespace:
            return annotation
    return None


def process_song_data(
    ir_pro_df: pd.DataFrame,
    jams_folder: str = "",
    return_format: str = 'dataframe'
) -> Any:
    """
    Process iReal-Pro songs and create a comprehensive dataset.
    
    Args:
        ir_pro_df: DataFrame containing iReal-Pro song metadata
        jams_folder: Path to folder containing JAMS files
        return_format: 'dataframe' (default), 'list', or 'dict'
    
    Returns:
        DataFrame by default, or List/Dict of song data including:
        - id, title, chord_progression, duration_progression, key, artist, genre

    ``duration_progression`` records the notated duration of each chord, aligned
    index by index with ``chord_progression``.  Song-level measures weighted by
    the time a chord actually occupies -- rather than by how many times it is
    written -- depend on it, and it also makes corpora annotated at different
    rhythmic granularities comparable.
    """
    from .chords import map_chord  # Import from reorganized module

    songs_data = []

    # Get list of available JAMS files
    available_files = {f[:-5]: f for f in os.listdir(jams_folder) if f.endswith('.jams')}

    for _, row in ir_pro_df.iterrows():
        song_id = row['id']

        # Check if JAMS file exists for this song
        if str(song_id) in available_files:
            try:
                # Load JAMS file
                jams_file = os.path.join(jams_folder, available_files[str(song_id)])
                audio_jams = jams.load(jams_file, validate=False)

                # Select annotations by namespace rather than by position: the
                # ordering inside a JAMS file is not guaranteed, and reading a
                # timesig annotation as if it were the key would pass silently.
                chord_ann = _annotation_by_namespace(audio_jams, 'chord_harte')
                key_ann = _annotation_by_namespace(audio_jams, 'key_mode')
                if chord_ann is None or key_ann is None:
                    continue

                # Extract chord progression
                song_key = [obs.value for obs in key_ann.data]
                chord_progression = [map_chord(obs.value) for obs in chord_ann.data]
                duration_progression = [obs.duration for obs in chord_ann.data]
                root_progression = [obs.value.split(":", 1)[0] for obs in chord_ann.data]
                kind_progression = [obs.value.split(":", 1)[1] if ":" in obs.value else "" for obs in chord_ann.data]

                # Get title from metadata
                title = audio_jams.file_metadata.title

                songs_data.append({
                    'id': song_id,
                    'title': title,
                    'chord_progression': chord_progression,
                    'duration_progression': duration_progression,
                    'root_progression': root_progression,
                    'kind_progression': kind_progression,
                    'key': song_key,
                    'artist': row['artist'],
                    'genre': row['genre'] if 'genre' in row else None
                })

            except Exception as e:
                print(f"Error processing song {song_id}: {e}")
                continue
    
    # Return in requested format
    if return_format == 'dataframe':
        return pd.DataFrame(songs_data)
    elif return_format == 'list':
        return songs_data
    elif return_format == 'dict':
        return {song['id']: song for song in songs_data}
    else:
        raise ValueError("return_format must be 'dataframe', 'list', or 'dict'")


def load_and_process_dataset(
    metadata_path: str, 
    jams_folder: str,
    output_format: str = 'dataframe'
) -> Any:
    """
    Load and process a complete musical dataset.
    
    Args:
        metadata_path: Path to metadata CSV file
        jams_folder: Path to JAMS files folder
        output_format: 'dataframe', 'list', or 'dict'
    
    Returns:
        Processed dataset in requested format
    """
    # Load metadata
    metadata_df = pd.read_csv(metadata_path)
    
    # Process songs
    songs_data = process_song_data(metadata_df, jams_folder)
    
    if output_format == 'dataframe':
        return pd.DataFrame(songs_data)
    elif output_format == 'list':
        return songs_data
    elif output_format == 'dict':
        return {song['id']: song for song in songs_data}
    else:
        raise ValueError("output_format must be 'dataframe', 'list', or 'dict'")


def filter_songs_by_criteria(
    songs_data: List[Dict[str, Any]], 
    min_chords: int = 5,
    max_chords: Optional[int] = None,
    allowed_genres: Optional[List[str]] = None,
    required_keys: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Filter songs based on various criteria.
    
    Args:
        songs_data: List of song dictionaries
        min_chords: Minimum number of chords required
        max_chords: Maximum number of chords allowed (None for no limit)
        allowed_genres: List of allowed genres (None for all)
        required_keys: List of required keys (None for all)
    
    Returns:
        Filtered list of songs
    """
    filtered = []
    
    for song in songs_data:
        # Check chord count
        chord_count = len(song.get('chord_progression', []))
        if chord_count < min_chords:
            continue
        if max_chords and chord_count > max_chords:
            continue
        
        # Check genre
        if allowed_genres and song.get('genre') not in allowed_genres:
            continue
        
        # Check key
        if required_keys:
            song_keys = song.get('key', [])
            if not any(key in required_keys for key in song_keys):
                continue
        
        filtered.append(song)
    
    return filtered


def extract_chord_statistics(songs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract statistical information about chords in the dataset.
    
    Args:
        songs_data: List of song dictionaries
    
    Returns:
        Dictionary with chord statistics
    """
    from collections import Counter
    
    all_chords = []
    all_roots = []
    all_kinds = []
    progression_lengths = []
    
    for song in songs_data:
        chord_prog = song.get('chord_progression', [])
        root_prog = song.get('root_progression', [])
        kind_prog = song.get('kind_progression', [])
        
        progression_lengths.append(len(chord_prog))
        all_chords.extend(chord_prog)
        all_roots.extend(root_prog)
        all_kinds.extend(kind_prog)
    
    return {
        'total_songs': len(songs_data),
        'total_chords': len(all_chords),
        'avg_progression_length': sum(progression_lengths) / len(progression_lengths) if progression_lengths else 0,
        'most_common_roots': Counter(all_roots).most_common(12),
        'most_common_kinds': Counter(all_kinds).most_common(20),
        'chord_distribution': Counter(str(chord) for chord in all_chords).most_common(50)
    }


def create_chord_transition_matrix(songs_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Create a chord transition matrix from the dataset.
    
    Args:
        songs_data: List of song dictionaries
    
    Returns:
        DataFrame representing chord transition probabilities
    """
    from collections import defaultdict, Counter
    
    transitions = defaultdict(Counter)
    
    for song in songs_data:
        chord_prog = song.get('chord_progression', [])
        
        for i in range(len(chord_prog) - 1):
            current_chord = str(chord_prog[i])
            next_chord = str(chord_prog[i + 1])
            transitions[current_chord][next_chord] += 1
    
    # Convert to DataFrame
    all_chords = set()
    for current in transitions:
        all_chords.add(current)
        for next_chord in transitions[current]:
            all_chords.add(next_chord)
    
    all_chords = sorted(list(all_chords))
    
    # Create transition matrix
    matrix = pd.DataFrame(0, index=all_chords, columns=all_chords)
    
    for current in transitions:
        total_transitions = sum(transitions[current].values())
        for next_chord, count in transitions[current].items():
            matrix.loc[current, next_chord] = count / total_transitions
    
    return matrix
