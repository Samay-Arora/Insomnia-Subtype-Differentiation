"""
Debug Script: Check what's actually in the hypnogram files
Run this to see what data we're getting
"""

import mne
import numpy as np
from pathlib import Path

mne.set_log_level('WARNING')

def debug_hypnogram_file(filepath):
    """
    Examine one hypnogram file in detail
    """
    print("=" * 80)
    print(f"DEBUGGING FILE: {filepath.name}")
    print("=" * 80)
    print()
    
    try:
        # Load the file
        raw = mne.io.read_raw_edf(filepath, preload=True, verbose=False)
        
        print("✓ File loaded successfully")
        print()
        
        # Check basic info
        print("FILE INFORMATION:")
        print(f"  Duration: {raw.times[-1]} seconds ({raw.times[-1]/3600:.2f} hours)")
        print(f"  Sampling rate: {raw.info['sfreq']} Hz")
        print(f"  Number of channels: {len(raw.ch_names)}")
        print(f"  Channel names: {raw.ch_names}")
        print()
        
        # Check annotations
        annotations = raw.annotations
        print("ANNOTATIONS:")
        print(f"  Total annotations: {len(annotations)}")
        print()
        
        if len(annotations) == 0:
            print("  ❌ WARNING: No annotations found!")
            return
        
        # Show first 20 annotations
        print("  First 20 annotations:")
        for i, annot in enumerate(annotations[:20]):
            onset = annot['onset']
            duration = annot['duration']
            description = annot['description']
            print(f"    [{i}] {onset:6.1f}s - {duration:4.1f}s : {description}")
        
        print()
        
        # Count unique sleep stages
        stage_counts = {}
        for annot in annotations:
            stage = annot['description']
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
        
        print("  Sleep stage distribution:")
        for stage, count in sorted(stage_counts.items()):
            percent = (count / len(annotations)) * 100
            print(f"    {stage:20s}: {count:4d} epochs ({percent:5.1f}%)")
        
        print()
        
        # Check if this looks right
        print("DATA VALIDATION:")
        
        # Expected: ~8 hours = ~960 30-second epochs
        expected_epochs = (raw.times[-1] / 30)
        if len(annotations) < expected_epochs * 0.5:
            print(f"  ⚠️  WARNING: Too few annotations!")
            print(f"     Expected ~{expected_epochs:.0f} epochs for {raw.times[-1]/3600:.1f} hour recording")
            print(f"     Found only {len(annotations)} annotations")
        else:
            print(f"  ✓ Annotation count looks reasonable ({len(annotations)} epochs)")
        
        # Check if we have actual sleep stages
        sleep_stages = ['Sleep stage 1', 'Sleep stage 2', 'Sleep stage 3', 
                        'Sleep stage 4', 'Sleep stage R', 'Sleep stage N1',
                        'Sleep stage N2', 'Sleep stage N3']
        
        has_sleep = any(stage in stage_counts for stage in sleep_stages)
        
        if not has_sleep:
            print("  ❌ WARNING: No actual sleep stages found!")
            print("     Available stages:", list(stage_counts.keys()))
        else:
            print("  ✓ Sleep stages detected")
        
        print()
        print("=" * 80)
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR loading file: {e}")
        print()
        return False


def check_multiple_files(data_dir='sleep_edf_data', num_files=5):
    """
    Check multiple files to see if issue is consistent
    """
    print()
    print("=" * 80)
    print("CHECKING MULTIPLE HYPNOGRAM FILES")
    print("=" * 80)
    print()
    
    data_path = Path(data_dir)
    hypno_files = sorted(list(data_path.glob('*-Hypnogram.edf')))
    
    if len(hypno_files) == 0:
        print(f"❌ No hypnogram files found in {data_dir}/")
        return
    
    print(f"Found {len(hypno_files)} total files")
    print(f"Checking first {num_files} files...\n")
    
    for i, hypno_file in enumerate(hypno_files[:num_files]):
        debug_hypnogram_file(hypno_file)
        
        if i < num_files - 1:
            input("Press Enter to check next file...")
            print("\n")


if __name__ == "__main__":
    # First check one file in detail
    data_path = Path('sleep_edf_data')
    hypno_files = list(data_path.glob('*-Hypnogram.edf'))
    
    if len(hypno_files) > 0:
        print("\n🔍 Debugging first hypnogram file...")
        debug_hypnogram_file(hypno_files[0])
        
        print("\nWould you like to check more files? (y/n): ", end='')
        response = input().strip().lower()
        
        if response == 'y':
            check_multiple_files(num_files=3)
    else:
        print("❌ No hypnogram files found in sleep_edf_data/")
        print("Please ensure files were downloaded correctly")