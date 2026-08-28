"""Key estimation from parsed chord successions."""

from collections.abc import Iterable, Sequence
from typing import Optional

import numpy as np
from music21 import chord as m21chord
from music21 import stream

from .chords import chord_to_pitch_classes


KeyEstimate = tuple[int, str, float]


def _root_and_kind(chord) -> Optional[tuple[int, np.ndarray]]:
    """Normalise supported chord representations, or reject a malformed one."""
    if chord is None:
        return None
    try:
        if len(chord) == 2 and len(chord[1]) == 11:
            root, kind = chord[0], chord[1]
        elif len(chord) >= 12:
            root, kind = chord[0], chord[1:12]
        else:
            return None
    except (TypeError, IndexError):
        return None

    if root is None or any(bit is None for bit in kind):
        return None
    try:
        root = int(root)
        kind = np.asarray(kind, dtype=int)
    except (TypeError, ValueError):
        return None
    if not 0 <= root <= 11 or kind.shape != (11,) or not np.isin(kind, (0, 1)).all():
        return None
    return root, kind


def estimate_key_from_chords(
    chords: Iterable[Sequence],
    minimum_chords: int = 3,
) -> Optional[KeyEstimate]:
    """Estimate a global key with music21's default key-analysis method.

    Each item may be either ``(root, kind_vector)`` or the flat representation
    ``[root, *kind_vector]`` returned by :func:`leadsheetanalyser.chords.map_chord`.
    Malformed items are ignored, matching the package's corpus-processing
    policy.  Chords are unweighted: repeated chord events remain repeated.

    Returns ``(tonic_pitch_class, mode, correlation)`` or ``None`` when fewer
    than ``minimum_chords`` valid events remain.
    """
    if minimum_chords < 1:
        raise ValueError("minimum_chords must be positive")

    succession = stream.Stream()
    for item in chords:
        parsed = _root_and_kind(item)
        if parsed is None:
            continue
        root, kind = parsed
        succession.append(m21chord.Chord(sorted(chord_to_pitch_classes(root, kind))))

    if len(succession) < minimum_chords:
        return None
    estimate = succession.analyze("key")
    return (
        int(estimate.tonic.pitchClass),
        str(estimate.mode),
        float(estimate.correlationCoefficient),
    )
