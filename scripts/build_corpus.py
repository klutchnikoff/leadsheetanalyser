#!/usr/bin/env python3
"""Build the processed corpus pickles from meta.csv and the ChoCo JAMS files.

This is the step between `download_data.py`, which fetches the JAMS, and the
analysis scripts, which read the pickles.  It was previously done by hand and
never committed: `music_realbook.pkl` appeared in `.gitignore` and nowhere else
in the repository, so the published pipeline had a hole in the middle and a
reader could not rebuild the corpus the article studies.

Usage
-----
    python scripts/build_corpus.py                    # real-book (the article's corpus)
    python scripts/build_corpus.py --partition ireal-pro
    python scripts/build_corpus.py --verify           # rebuild and diff against the
                                                      # pickle already on disk

Only the *Real Book* side needs a pickle.  The common-practice side of the
article reads `when-in-rome` JAMS directly from `data/jams_files`, so nothing
here has to be built for it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from leadsheetanalyser.data_access import get_package_data_path, load_metadata
from leadsheetanalyser.data_processing import process_song_data


# A partition's pickle is named for the article that uses it, not for the
# partition, which is why the mapping is explicit rather than derived.
DEFAULT_OUTPUT = {
    "real-book": "music_realbook.pkl",
    "ireal-pro": "music.pkl",
}


def build(partition: str, jams_folder: Path) -> pd.DataFrame:
    """Process every song of `partition` that has metadata and a JAMS file.

    Rows are kept in the order `meta.csv` gives them.  Sorting numerically on
    the id suffix would be tidier but would silently change the row order of a
    pickle other scripts already index by position.
    """
    meta = load_metadata()
    subset = meta[meta["id"].astype(str).str.startswith(partition)].reset_index(drop=True)
    if subset.empty:
        sys.exit(f"no metadata rows for partition {partition!r} in meta.csv")

    print(f"  {len(subset)} metadata rows for {partition}")

    # process_song_data skips a song whose JAMS lacks a chord_harte or key_mode
    # annotation, so the output can be shorter than the input.  Report the gap
    # rather than let it pass unnoticed.
    frame = process_song_data(subset, jams_folder=str(jams_folder))
    dropped = len(subset) - len(frame)
    print(f"  {len(frame)} songs processed" + (f", {dropped} skipped" if dropped else ""))
    return frame


def describe(frame: pd.DataFrame) -> None:
    """Print the few totals the article quotes, so a rebuild can be checked."""
    tokens = sum(len(p) for p in frame["chord_progression"] if p is not None)
    durations = sum(
        1 for d in frame["duration_progression"] if d is not None and len(d)
    )
    print(f"  {tokens} chord tokens")
    print(f"  {durations}/{len(frame)} songs carry durations")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--partition", default="real-book",
                        help="ChoCo partition prefix (default: real-book)")
    parser.add_argument("--out", default=None,
                        help="output pickle name, relative to data/")
    parser.add_argument("--verify", action="store_true",
                        help="compare against the existing pickle instead of overwriting")
    args = parser.parse_args()

    data_dir = get_package_data_path()
    jams_folder = data_dir / "jams_files"
    if not jams_folder.is_dir():
        sys.exit(
            f"{jams_folder} not found.\n"
            "Fetch the JAMS first:  python scripts/download_data.py\n"
            "See DATA.md for the alternatives."
        )

    name = args.out or DEFAULT_OUTPUT.get(args.partition)
    if name is None:
        sys.exit(f"no default output name for {args.partition!r}; pass --out")
    target = data_dir / name

    print(f"building {target.name} from {args.partition}")
    frame = build(args.partition, jams_folder)
    describe(frame)

    if args.verify:
        if not target.exists():
            sys.exit(f"nothing to verify against: {target} does not exist")
        reference = pd.read_pickle(target)
        same_shape = frame.shape == reference.shape
        same_columns = list(frame.columns) == list(reference.columns)
        # Compare values, not storage.  pandas 3 infers the `str` dtype for text
        # columns that older versions left as `object`, so a faithful rebuild
        # fails a plain .equals() against a pickle written before that change.
        same_content = (
            same_shape and same_columns
            and frame.astype(object).equals(reference.astype(object))
        )
        drifted = [c for c in frame.columns if frame[c].dtype != reference[c].dtype]
        print(f"\nverify against {target.name}")
        print(f"  shape    {frame.shape} vs {reference.shape} -> {same_shape}")
        print(f"  columns  {same_columns}")
        print(f"  content  {same_content}")
        if drifted:
            print("  dtype    differs on " + ", ".join(drifted)
                  + f" (pandas {pd.__version__}; values unaffected)")
        sys.exit(0 if same_content else 1)

    target.parent.mkdir(parents=True, exist_ok=True)
    frame.to_pickle(target)
    print(f"\nwrote {target}")


if __name__ == "__main__":
    main()
