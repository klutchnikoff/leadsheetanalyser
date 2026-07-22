"""
Song-level dissimilarity via optimal transport.

A song is modelled as an empirical distribution over its (rooted) chords,
following the paper *A Probabilistic Approach to Jazz Harmony*. The distance
between two songs is the optimal transport (Wasserstein / earth-mover) cost
between these empirical measures, using a chord-level dissimilarity as the
ground cost.

The ground cost can be:
  * the modal dissimilarity induced by a
    musical system ``W`` and aggregated with an l_p norm (see :func:`chord_dissimilarities.modal_dissimilarity`), or
  * any callable ``cost_fn(chord1, chord2) -> float`` (e.g. the
    ``simple_dissimilarity`` / ``tonal_dissimilarity`` baselines).

A chord is a pair ``(root, kind)`` with ``root`` an int in 0..11 and ``kind`` a
length-11 binary vector.
"""
from collections import Counter
from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np
import ot

from .chord_dissimilarities import modal_dissimilarity

Chord = Tuple[int, np.ndarray]


def song_to_measure(chords: Sequence[Chord]) -> Tuple[List[Chord], np.ndarray]:
    """Aggregate a song's chords into a weighted empirical measure.

    Repeated chords are merged; the returned weights sum to one and are
    proportional to the number of occurrences of each distinct chord.
    """
    counts = Counter((int(r), tuple(int(x) for x in k)) for r, k in chords)
    uniq = list(counts)
    weights = np.array([counts[u] for u in uniq], dtype=float)
    weights /= weights.sum()
    chord_objs = [(r, np.array(k, dtype=int)) for (r, k) in uniq]
    return chord_objs, weights


def _reinterpretations(chords: Sequence[Chord]) -> np.ndarray:
    """R[i, r] = the 11-vector of chord i heard as rooted on r."""
    R = np.zeros((len(chords), 12, 11), dtype=np.int8)
    for i, (root, kind) in enumerate(chords):
        pcs = {(root + j) % 12 for j in [0] + [j for j, v in enumerate(kind, 1) if v]}
        for rp in range(12):
            for j in range(1, 12):
                if (rp + j) % 12 in pcs:
                    R[i, rp, j - 1] = 1
    return R


def _embed(V: np.ndarray, W: np.ndarray, mode: str = "linear") -> np.ndarray:
    """V: (..., 11) -> (..., m). 'angular' keeps only the profile's direction."""
    P = V @ W.T
    if mode == "linear":
        return P
    norms = np.linalg.norm(P, axis=-1, keepdims=True)
    return np.divide(P, norms, out=np.zeros_like(P), where=norms > 1e-12)


def ground_cost_matrix(
    chords_a: Sequence[Chord],
    chords_b: Sequence[Chord],
    W: Optional[np.ndarray] = None,
    p: float = 1.0,
    cost_fn: Optional[Callable[[Chord, Chord], float]] = None,
    embedding: str = "linear",
) -> np.ndarray:
    """Pairwise ground-cost matrix between two lists of chords."""
    if cost_fn is None:
        if W is None:
            raise ValueError("Provide a musical system W, or a cost_fn.")
        
        # Fast vectorized path
        if len(chords_a) == 0 or len(chords_b) == 0:
            return np.zeros((len(chords_a), len(chords_b)))
        
        roots_a = np.array([r for r, _ in chords_a])
        roots_b = np.array([r for r, _ in chords_b])
        
        A = _embed(_reinterpretations(chords_a).astype(float), W, mode=embedding)
        B = _embed(_reinterpretations(chords_b).astype(float), W, mode=embedding)
        own_a = A[np.arange(len(chords_a)), roots_a]
        own_b = B[np.arange(len(chords_b)), roots_b]
        
        M = np.zeros((len(chords_a), len(chords_b)))
        block = 256
        for s in range(0, len(chords_a), block):
            e = min(s + block, len(chords_a))
            first = np.linalg.norm(A[s:e][:, roots_b, :] - own_b[None, :, :], axis=2)
            second = np.linalg.norm(
                B[:, roots_a[s:e], :].transpose(1, 0, 2) - own_a[s:e][:, None, :], axis=2)
            
            if p == 1.0:
                M[s:e] = first + second
            elif p == float('inf'):
                M[s:e] = np.maximum(first, second)
            else:
                M[s:e] = (first**p + second**p)**(1/p)
        return M
    else:
        cost = cost_fn

    M = np.zeros((len(chords_a), len(chords_b)))
    for i, a in enumerate(chords_a):
        for j, b in enumerate(chords_b):
            M[i, j] = cost(a, b)
    return M


def song_distance(
    song_a: Sequence[Chord],
    song_b: Sequence[Chord],
    W: Optional[np.ndarray] = None,
    p: float = 1.0,
    cost_fn: Optional[Callable[[Chord, Chord], float]] = None,
    embedding: str = "linear",
) -> float:
    """Optimal-transport distance between two songs.

    Parameters
    ----------
    song_a, song_b : sequences of chords ``(root, kind)``.
    W : musical system matrix used for the modal ground cost (ignored if
        ``cost_fn`` is given).
    p : the p-norm to aggregate the two directional discrepancies (default 1.0 for sum).
    cost_fn : optional callable overriding the ground cost.
    embedding : optional string "linear" or "angular" (default "linear").
    """
    chords_a, wa = song_to_measure(song_a)
    chords_b, wb = song_to_measure(song_b)
    M = ground_cost_matrix(chords_a, chords_b, W=W, p=p, cost_fn=cost_fn, embedding=embedding)
    return float(ot.emd2(wa, wb, M))
