#!/usr/bin/env python3
"""
Data Download Script for LeadSheet Analyser

This script downloads and sets up the ChoCo dataset for the leadsheetanalyser package.
It provides multiple methods for obtaining the data:
1. Clone ChoCo repository directly (default)
2. Create symlink to existing ChoCo repository
3. Update existing data

Usage:
    python scripts/download_data.py                                    # Default: clone ChoCo
    python scripts/download_data.py --method symlink --choco-path /path/to/choco
    python scripts/download_data.py --update                           # Update existing data
"""

import argparse
import os
import subprocess
import sys
import urllib.request
import zipfile
import tempfile
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            check=check, 
            capture_output=True, 
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_git_available():
    """Check if git is available on the system."""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: git is not available. Please install git first.")
        return False


def download_from_release(data_dir, release_tag="v1.0.0"):
    """
    Download ChoCo data directly from GitHub releases.
    
    Args:
        data_dir: Path to data directory
        release_tag: GitHub release tag to download from
    """
    print(f"Downloading ChoCo data from release {release_tag}...")
    
    # GitHub release URL for ChoCo data
    release_urls = {
        "v1.0.0": "https://github.com/smashub/choco/releases/download/v1.0.0/v1.0.0.zip",
        "data-v0.1.0": "https://github.com/smashub/choco/releases/download/data-v0.1.0/choco-data.zip"
    }
    
    if release_tag not in release_urls:
        print(f"Error: Unknown release tag '{release_tag}'")
        print(f"Available releases: {list(release_urls.keys())}")
        sys.exit(1)
    
    download_url = release_urls[release_tag]
    
    # Create temporary directory for download
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_file = temp_path / "choco-data.zip"
        
        print(f"Downloading from {download_url}...")
        try:
            urllib.request.urlretrieve(download_url, zip_file)
            print(f"Downloaded {zip_file.stat().st_size / (1024*1024):.1f} MB")
        except Exception as e:
            print(f"Error downloading file: {e}")
            sys.exit(1)
        
        # Extract the zip file
        print("Extracting data...")
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
        except Exception as e:
            print(f"Error extracting zip file: {e}")
            sys.exit(1)
        
        # Find the JAMS folder in extracted content
        extracted_jams = None
        for root, dirs, files in os.walk(temp_path):
            if 'jams' in dirs:
                extracted_jams = Path(root) / 'jams'
                break
        
        if not extracted_jams or not extracted_jams.exists():
            print("Error: Could not find 'jams' folder in downloaded data")
            sys.exit(1)
        
        # Move JAMS files to destination
        jams_dest = data_dir / "jams_files"
        
        # Remove existing directory if it exists
        if jams_dest.exists():
            print(f"Removing existing {jams_dest}")
            if jams_dest.is_symlink():
                jams_dest.unlink()
            elif jams_dest.is_dir():
                import shutil
                shutil.rmtree(jams_dest)
            else:
                jams_dest.unlink()
        
        # Copy JAMS files
        print(f"Copying JAMS files to {jams_dest}")
        import shutil
        shutil.copytree(extracted_jams, jams_dest)
        
        # Also copy meta.csv if it exists
        meta_file = None
        for root, dirs, files in os.walk(temp_path):
            if 'meta.csv' in files:
                meta_file = Path(root) / 'meta.csv'
                break
        
        if meta_file and meta_file.exists():
            meta_dest = data_dir / "meta.csv"
            if not meta_dest.exists():  # Don't overwrite existing meta.csv
                print(f"Copying metadata to {meta_dest}")
                shutil.copy2(meta_file, meta_dest)
            else:
                print(f"Metadata file already exists at {meta_dest}, skipping")
    
    print("✅ Successfully downloaded and extracted ChoCo data from release")
    return jams_dest


def setup_data_directory():
    """Create data directory if it doesn't exist."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    return data_dir


def clone_choco_repository(data_dir):
    """Clone the ChoCo repository into data/choco."""
    choco_dir = data_dir / "choco"
    
    if choco_dir.exists():
        print(f"ChoCo repository already exists at {choco_dir}")
        return choco_dir
    
    print("Cloning ChoCo repository...")
    choco_url = "https://github.com/smashub/choco.git"
    run_command(f"git clone {choco_url}", cwd=data_dir)
    
    if not choco_dir.exists():
        print("Error: Failed to clone ChoCo repository")
        sys.exit(1)
        
    print(f"Successfully cloned ChoCo repository to {choco_dir}")
    return choco_dir


def create_jams_symlink(data_dir, choco_path=None):
    """Create symlink from data/jams_files to ChoCo JAMS directory."""
    if choco_path:
        # Use provided path to existing ChoCo repository
        choco_dir = Path(choco_path)
        if not choco_dir.exists():
            print(f"Error: ChoCo path does not exist: {choco_path}")
            sys.exit(1)
    else:
        # Use local ChoCo repository
        choco_dir = data_dir / "choco"
        if not choco_dir.exists():
            print("Error: ChoCo repository not found. Run without --method symlink first.")
            sys.exit(1)
    
    # Try to find the JAMS directory in different possible locations
    possible_jams_paths = [
        choco_dir / "partitions" / "ireal-pro" / "jams",  # Standard repository structure
        choco_dir / "jams",  # Direct jams folder (release structure)
        choco_dir / "data" / "jams",  # Alternative structure
        choco_dir / "partitions" / "ireal-pro" / "choco" / "playlists" / "jams-converted",  # Nested structure
    ]
    
    jams_source = None
    for path in possible_jams_paths:
        if path.exists() and path.is_dir():
            # Verify it contains JAMS files
            jams_files = list(path.glob("*.jams"))
            if jams_files:
                jams_source = path
                print(f"Found JAMS directory at: {jams_source}")
                break
    
    if not jams_source:
        print("Error: JAMS directory not found in ChoCo repository")
        print("Searched in the following locations:")
        for path in possible_jams_paths:
            print(f"  - {path}")
        print("The ChoCo repository structure might have changed.")
        sys.exit(1)
    
    # Create symlink
    jams_link = data_dir / "jams_files"
    
    # Remove existing symlink or directory if it exists
    if jams_link.exists() or jams_link.is_symlink():
        print(f"Removing existing {jams_link}")
        if jams_link.is_symlink():
            jams_link.unlink()
        elif jams_link.is_dir():
            import shutil
            shutil.rmtree(jams_link)
        else:
            jams_link.unlink()
    
    # Create new symlink
    if choco_path:
        # Use absolute path for external ChoCo
        jams_link.symlink_to(jams_source.resolve())
    else:
        # Use relative path to local ChoCo - calculate relative path
        relative_path = jams_source.relative_to(data_dir)
        jams_link.symlink_to(relative_path)
    
    print(f"Created symlink: {jams_link} -> {jams_source}")
    return jams_link


def verify_setup(data_dir):
    """Verify that the data setup is working correctly."""
    jams_path = data_dir / "jams_files"
    
    if not jams_path.exists():
        print("Error: jams_files directory/symlink does not exist")
        return False
    
    # Check if it's a symlink or directory
    if jams_path.is_symlink():
        print(f"✓ jams_files is a symlink pointing to: {jams_path.resolve()}")
    elif jams_path.is_dir():
        print("✓ jams_files is a directory (from release download)")
    else:
        print("Warning: jams_files exists but is neither a directory nor symlink")
    
    # Count JAMS files
    try:
        jams_files = list(jams_path.glob("*.jams"))
        num_files = len(jams_files)
        print(f"Found {num_files} JAMS files in {jams_path}")
        
        if num_files == 0:
            print("❌ No JAMS files found")
            return False
        elif num_files < 100:
            print(f"⚠️  Found {num_files} JAMS files (expected 1000+, but this might be a subset)")
            # Don't fail for small numbers - might be a test subset
            return True
        else:
            print("✅ Data setup appears successful!")
            
        return True
        
    except Exception as e:
        print(f"Error verifying setup: {e}")
        return False


def update_data(data_dir):
    """Update existing ChoCo repository."""
    choco_dir = data_dir / "choco"
    
    if not choco_dir.exists():
        print("Error: No existing ChoCo repository found to update")
        print("Run without --update to set up data first")
        sys.exit(1)
    
    print("Updating ChoCo repository...")
    run_command("git pull origin main", cwd=choco_dir)
    print("ChoCo repository updated successfully")


def main():
    parser = argparse.ArgumentParser(
        description="Download and set up ChoCo dataset for leadsheetanalyser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/download_data.py                                    # Download from latest release (default)
  python scripts/download_data.py --method release --release data-v0.1.0
  python scripts/download_data.py --method clone                     # Clone full ChoCo repository
  python scripts/download_data.py --method symlink --choco-path /path/to/existing/choco
  python scripts/download_data.py --method clone --update            # Update existing ChoCo repository
        """
    )
    
    parser.add_argument(
        "--method", 
        choices=["clone", "release", "symlink"], 
        default="release",
        help="Method for obtaining data: download from release (default), clone ChoCo repository, or symlink to existing one"
    )
    
    parser.add_argument(
        "--release", 
        type=str,
        default="v1.0.0",
        help="GitHub release tag to download (used with --method release)"
    )
    
    parser.add_argument(
        "--choco-path", 
        type=str,
        help="Path to existing ChoCo repository (required when using --method symlink)"
    )
    
    parser.add_argument(
        "--update", 
        action="store_true",
        help="Update existing ChoCo repository (only works with clone method)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.method == "symlink" and not args.choco_path:
        print("Error: --choco-path is required when using --method symlink")
        sys.exit(1)
    
    if args.update and args.method != "clone":
        print("Error: --update only works with --method clone")
        sys.exit(1)
    
    # Check prerequisites
    if args.method == "clone" or args.update:
        if not check_git_available():
            sys.exit(1)
    
    # Set up data directory
    data_dir = setup_data_directory()
    print(f"Working in data directory: {data_dir.resolve()}")
    
    # Handle update mode
    if args.update:
        update_data(data_dir)
        verify_setup(data_dir)
        return
    
    # Handle different methods
    if args.method == "release":
        print("Setting up data using release download method...")
        download_from_release(data_dir, args.release)
        
    elif args.method == "clone":
        print("Setting up data using clone method...")
        clone_choco_repository(data_dir)
        create_jams_symlink(data_dir)
        
    elif args.method == "symlink":
        print(f"Setting up data using symlink method with ChoCo at: {args.choco_path}")
        create_jams_symlink(data_dir, args.choco_path)
    
    # Verify setup
    if verify_setup(data_dir):
        print("\n🎉 Data setup completed successfully!")
        print("\nNext steps:")
        print("1. Activate the virtual environment if not already done:")
        print("   conda activate py-music")
        print("2. Install the package: pip install -e .")
        print("3. Run tests: python -m pytest tests/")

    else:
        print("\n❌ Data setup encountered issues. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
