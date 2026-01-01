"""
Debug Script: Test WASO calculation on ONE file
Run this to see exactly what's happening
"""

import numpy as np
import mne
from pathlib import Path

mne.set_log_level('WARNING')

def load_hypnogram_debug(filepath):
    """Load hypnogram with detailed output"""
    print(f"\n{'='*80}")
    print(f"Loading: {filepath.name}")
    print('='*80)
    
    try:
        annotations = mne.read_annotations(filepath)
        
        print(f"Total annotations: {len(annotations)}")
        print(f"\nFirst 10 annotations:")
        for i, annot in enumerate(annotations[:10]):
            print(f"  {i}: onset={annot['onset']:.1f}s, duration={annot['duration']:.1f}s, desc='{annot['description']}'")
        
        # Calculate number of epochs
        end_time = annotations.onset[-1] + annotations.duration[-1]
        n_epochs = int(np.ceil(end_time / 30.0))
        
        print(f"\nTotal recording duration: {end_time:.1f} seconds ({end_time/3600:.2f} hours)")
        print(f"Number of 30-second epochs: {n_epochs}")
        
        # Initialize sleep stages
        sleep_stages = np.full(n_epochs, 9, dtype=int)
        
        # Parse annotations
        for annot in annotations:
            desc = annot['description']
            onset = annot['onset']
            duration = annot['duration']
            
            # Parse stage
            if desc is None:
                stage_code = 9
            else:
                d = desc.strip().lower()
                if 'wake' in d or d == 'w' or 'stage w' in d:
                    stage_code = 0
                elif 'stage 1' in d or 'n1' in d or d == '1':
                    stage_code = 1
                elif 'stage 2' in d or 'n2' in d or d == '2':
                    stage_code = 2
                elif 'stage 3' in d or 'n3' in d or d == '3':
                    stage_code = 3
                elif 'stage 4' in d or d == '4':
                    stage_code = 4
                elif 'rem' in d or 'stage r' in d or d == 'r':
                    stage_code = 5
                else:
                    stage_code = 9
            
            start_epoch = int(np.floor(onset / 30.0))
            end_epoch = int(np.ceil((onset + duration) / 30.0))
            
            start_epoch = max(start_epoch, 0)
            end_epoch = min(end_epoch, n_epochs)
            
            sleep_stages[start_epoch:end_epoch] = stage_code
        
        return sleep_stages
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def calculate_waso_debug(sleep_stages):
    """Calculate WASO with full debugging"""
    print(f"\n{'='*80}")
    print("CALCULATING WASO")
    print('='*80)
    
    if sleep_stages is None or len(sleep_stages) == 0:
        print("ERROR: No sleep stages!")
        return None
    
    # Show stage distribution
    print(f"\nTotal epochs: {len(sleep_stages)}")
    print(f"\nStage distribution:")
    unique, counts = np.unique(sleep_stages, return_counts=True)
    for stage, count in zip(unique, counts):
        stage_names = {0: 'Wake', 1: 'N1', 2: 'N2', 3: 'N3', 4: 'N4', 5: 'REM', 9: 'Unknown'}
        stage_name = stage_names.get(stage, f'Stage{stage}')
        percent = (count / len(sleep_stages)) * 100
        print(f"  {stage_name:10s}: {count:4d} epochs ({percent:5.1f}%)")
    
    # Show first and last 30 epochs
    print(f"\nFirst 30 epochs: {sleep_stages[:30]}")
    print(f"Last 30 epochs: {sleep_stages[-30:]}")
    
    # Find first and last sleep
    print(f"\n{'='*80}")
    print("FINDING SLEEP PERIOD")
    print('='*80)
    
    first_sleep = None
    last_sleep = None
    
    for i, stage in enumerate(sleep_stages):
        if stage > 0 and stage != 9:
            if first_sleep is None:
                first_sleep = i
                print(f"First sleep found at epoch {i} (stage {stage})")
            last_sleep = i
    
    if last_sleep is not None:
        print(f"Last sleep found at epoch {last_sleep} (stage {sleep_stages[last_sleep]})")
    
    # Calculate WASO
    print(f"\n{'='*80}")
    print("CALCULATING WASO")
    print('='*80)
    
    if first_sleep is None:
        print("ERROR: No sleep detected!")
        return 0
    
    if last_sleep is None:
        print("ERROR: last_sleep is None!")
        return 0
    
    print(f"Sleep period: epoch {first_sleep} to {last_sleep}")
    print(f"Sleep period duration: {last_sleep - first_sleep + 1} epochs ({(last_sleep - first_sleep + 1) * 0.5:.1f} minutes)")
    
    sleep_period = sleep_stages[first_sleep:last_sleep+1]
    print(f"\nSleep period length: {len(sleep_period)} epochs")
    print(f"Sleep period stages: {sleep_period[:30]}...")
    
    # Count wake epochs
    wake_epochs = np.sum(sleep_period == 0)
    print(f"\nWake epochs (stage 0) in sleep period: {wake_epochs}")
    
    WASO = wake_epochs * 0.5
    print(f"WASO: {WASO:.1f} minutes")
    
    # Additional stats
    other_stages = {
        1: np.sum(sleep_period == 1),
        2: np.sum(sleep_period == 2),
        3: np.sum(sleep_period == 3),
        4: np.sum(sleep_period == 4),
        5: np.sum(sleep_period == 5),
        9: np.sum(sleep_period == 9)
    }
    
    print(f"\nEpochs within sleep period:")
    stage_names = {0: 'Wake', 1: 'N1', 2: 'N2', 3: 'N3', 4: 'N4', 5: 'REM', 9: 'Unknown'}
    print(f"  Wake: {wake_epochs}")
    for stage, count in other_stages.items():
        if count > 0:
            print(f"  {stage_names[stage]}: {count}")
    
    return WASO

if __name__ == "__main__":
    # Find first hypnogram file
    data_path = Path('sleep_edf_data')
    hypno_files = list(data_path.glob('*-Hypnogram.edf'))
    
    if len(hypno_files) == 0:
        print("ERROR: No hypnogram files found in sleep_edf_data/")
    else:
        # Test first file
        test_file = hypno_files[0]
        
        print("\n" + "="*80)
        print("TESTING WASO CALCULATION")
        print("="*80)
        print(f"Test file: {test_file.name}")
        
        # Load hypnogram
        sleep_stages = load_hypnogram_debug(test_file)
        
        # Calculate WASO
        if sleep_stages is not None:
            waso = calculate_waso_debug(sleep_stages)
            
            print("\n" + "="*80)
            print("FINAL RESULT")
            print("="*80)
            print(f"WASO = {waso:.1f} minutes")
            print("="*80)