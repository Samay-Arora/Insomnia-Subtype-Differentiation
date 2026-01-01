"""
Complete Pipeline: Sleep-EDF Data Download, Processing, and Labeling
FIXED VERSION with manual download instructions

RECOMMENDED: Manual download is faster and more reliable!
Follow instructions in download_instructions() function below.
"""

import os
import requests
import numpy as np
import pandas as pd
import mne
from pathlib import Path
from tqdm import tqdm
import time
import zipfile
import shutil

# Suppress MNE warnings
mne.set_log_level('WARNING')

class SleepEDFPipeline:
    """Complete pipeline for Sleep-EDF processing and insomnia labeling"""
    
    def __init__(self, data_dir='sleep_edf_data', output_dir='processed_data'):
        self.data_dir = data_dir
        self.output_dir = output_dir
        Path(data_dir).mkdir(exist_ok=True)
        Path(output_dir).mkdir(exist_ok=True)
        
        # Clinical thresholds
        self.SOL_threshold = 30
        self.WASO_threshold = 30
        self.awakening_threshold = 3
        self.sleep_efficiency_threshold = 85
        self.early_wake_threshold = 60
        
        # Sleep stage mapping
        self.sleep_stages_map = {
            'Sleep stage W': 0, 'Sleep stage 1': 1, 'Sleep stage 2': 2,
            'Sleep stage 3': 3, 'Sleep stage 4': 4, 'Sleep stage R': 5,
            'Sleep stage ?': 9, 'Movement time': 9
        }
    
    # ==================== AUTOMATIC WGET DOWNLOAD (MAC/LINUX) ====================
    
    def download_with_wget(self):
        """
        Download using wget command (Mac/Linux)
        Downloads BOTH PSG (EEG signals) and Hypnogram (labels) files
        """
        print()
        print("=" * 80)
        print("DOWNLOADING PSG (EEG) + HYPNOGRAM FILES WITH WGET")
        print("=" * 80)
        print()
        
        # Check if wget is installed
        import subprocess
        try:
            result = subprocess.run(['wget', '--version'], 
                                capture_output=True, 
                                text=True, 
                                timeout=5)
            if result.returncode != 0:
                raise FileNotFoundError
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("❌ ERROR: wget is not installed!")
            print()
            print("Install wget first:")
            print("  brew install wget")
            print()
            return {'success': False, 'message': 'wget not installed'}
        
        print("✓ wget is installed")
        print()
        print("⚠️  NOTE: Downloading BOTH PSG and Hypnogram files")
        print("   - PSG files: EEG signal data (~50MB each)")
        print("   - Hypnogram files: Sleep stage annotations (~1KB each)")
        print("   - Total: ~306 files, ~7.5GB")
        print()
        print("This will take 10-20 minutes depending on connection speed...")
        print()
        
        # Download command - accept BOTH PSG and Hypnogram files
        download_cmd = [
            'wget', '-r', '-N', '-c', '-np',
            '--directory-prefix=sleep_edf_data',
            'https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/',
            '--accept', '*-PSG.edf,*-Hypnogram.edf'
        ]
        
        try:
            # Run wget download
            print("Running wget download...")
            result = subprocess.run(download_cmd, 
                                capture_output=False,
                                text=True)
            
            if result.returncode != 0:
                print(f"⚠️  wget returned code {result.returncode}")
            
            # Move files from nested directory
            nested_path = Path('sleep_edf_data/physionet.org/files/sleep-edfx/1.0.0/sleep-cassette')
            
            if nested_path.exists():
                print("\nMoving files to correct location...")
                edf_files = list(nested_path.glob('*.edf'))
                
                for src_file in edf_files:
                    dest_file = Path(self.data_dir) / src_file.name
                    shutil.move(str(src_file), str(dest_file))
                
                # Clean up nested folders
                print("Cleaning up temporary folders...")
                shutil.rmtree('sleep_edf_data/physionet.org', ignore_errors=True)
                
                # Count final files
                psg_files = list(Path(self.data_dir).glob('*-PSG.edf'))
                hypno_files = list(Path(self.data_dir).glob('*-Hypnogram.edf'))
                
                print()
                print("=" * 80)
                print("DOWNLOAD COMPLETE!")
                print("=" * 80)
                print(f"✓ PSG files (EEG signals): {len(psg_files)}")
                print(f"✓ Hypnogram files (labels): {len(hypno_files)}")
                print(f"✓ Total files: {len(psg_files) + len(hypno_files)}")
                print(f"✓ Location: {self.data_dir}/")
                print("=" * 80)
                print()
                
                if len(psg_files) == 0:
                    print("⚠️  WARNING: No PSG files downloaded!")
                    print("   PSG files contain the actual EEG data needed for feature extraction")
                    return {'success': False, 'message': 'No PSG files'}
                
                return {'success': True, 'psg': len(psg_files), 'hypno': len(hypno_files)}
            
            else:
                # Check if files downloaded directly
                psg_files = list(Path(self.data_dir).glob('*-PSG.edf'))
                hypno_files = list(Path(self.data_dir).glob('*-Hypnogram.edf'))
                
                if len(psg_files) > 0 or len(hypno_files) > 0:
                    print()
                    print("=" * 80)
                    print("DOWNLOAD COMPLETE!")
                    print("=" * 80)
                    print(f"✓ PSG files: {len(psg_files)}")
                    print(f"✓ Hypnogram files: {len(hypno_files)}")
                    print("=" * 80)
                    print()
                    return {'success': True, 'psg': len(psg_files), 'hypno': len(hypno_files)}
                else:
                    print("\n⚠️  Files not found in expected location")
                    return {'success': False, 'message': 'Files not found'}
        
        except Exception as e:
            print(f"\n❌ Error during download: {e}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def print_manual_instructions():
        """Fallback manual download instructions"""
        print()
        print("=" * 80)
        print("MANUAL DOWNLOAD INSTRUCTIONS")
        print("=" * 80)
        print()
        print("If automatic download fails, manually run this in terminal:")
        print()
        print("# Download BOTH PSG (EEG) and Hypnogram (labels) files:")
        print("mkdir -p sleep_edf_data && \\")
        print("wget -r -N -c -np \\")
        print("  --directory-prefix=sleep_edf_data \\")
        print("  https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/ \\")
        print("  --accept '*-PSG.edf,*-Hypnogram.edf' && \\")
        print("mv sleep_edf_data/physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/*.edf sleep_edf_data/ && \\")
        print("rm -rf sleep_edf_data/physionet.org")
        print()
        print("This downloads ~306 files (~7.5GB total)")
        print("=" * 80)
        print()
    
    # ==================== DOWNLOAD WITH PROPER HEADERS ====================
    
    def download_with_session(self, delay=1.0):
        """
        Download using requests.Session with proper headers
        More reliable than simple requests
        """
        print()
        print("=" * 80)
        print("DOWNLOADING WITH SESSION HEADERS")
        print("=" * 80)
        
        base_url = "https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/"
        
        # Create session with headers
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        
        downloaded = 0
        already_exists = 0
        failed = []
        
        subject_numbers = list(range(83))
        nights = [1, 2]
        total = len(subject_numbers) * len(nights)
        
        print(f"Attempting to download {total} files...")
        print()
        
        with tqdm(total=total, desc="Downloading", unit="file") as pbar:
            for subject_num in subject_numbers:
                for night in nights:
                    subject_str = str(subject_num).zfill(2)
                    filename = f"SC4{subject_str}{night}E0-Hypnogram.edf"
                    filepath = os.path.join(self.data_dir, filename)
                    
                    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
                        already_exists += 1
                        pbar.update(1)
                        continue
                    
                    url = base_url + filename
                    
                    try:
                        response = session.get(url, timeout=30, allow_redirects=True)
                        
                        if response.status_code == 200 and len(response.content) > 1000:
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                            downloaded += 1
                            time.sleep(delay)
                        else:
                            failed.append((filename, response.status_code))
                    
                    except Exception as e:
                        failed.append((filename, str(e)))
                    
                    pbar.update(1)
        
        total_files = downloaded + already_exists
        
        print()
        print("=" * 80)
        print("DOWNLOAD SUMMARY")
        print("=" * 80)
        print(f"✓ Successfully available: {total_files}")
        print(f"  - Newly downloaded: {downloaded}")
        print(f"  - Already existed: {already_exists}")
        print(f"✗ Failed: {len(failed)}")
        
        if len(failed) > 0 and len(failed) < 20:
            print("\nFailed files (showing first 10):")
            for fname, error in failed[:10]:
                print(f"  - {fname}: {error}")
        
        print("=" * 80)
        print()
        
        if total_files < 50:
            print("⚠️  WARNING: Very few files downloaded!")
            print("   Please use manual download method (see instructions above)")
            print()
            self.print_download_instructions()
        
        return {'total': total_files, 'downloaded': downloaded, 'failed': len(failed)}
    
    # ==================== PROCESS DATA ====================
    
    def load_hypnogram(self, filepath):
        """Load sleep stage annotations"""
        try:
            raw = mne.io.read_raw_edf(filepath, preload=True, verbose=False)
            annotations = raw.annotations
            
            sleep_stages = []
            for annot in annotations:
                stage_name = annot['description']
                stage_code = self.sleep_stages_map.get(stage_name, 9)
                sleep_stages.append(stage_code)
            
            return np.array(sleep_stages)
        except Exception as e:
            return None
    
    def calculate_sleep_onset_latency(self, sleep_stages):
        """Time from start to first sleep (minutes)"""
        for i, stage in enumerate(sleep_stages):
            if stage > 0 and stage != 9:
                return i * 0.5
        return len(sleep_stages) * 0.5
    
    def calculate_wake_after_sleep_onset(self, sleep_stages):
        """Total wake time during sleep (minutes)"""
        first_sleep = None
        last_sleep = None
        
        for i, stage in enumerate(sleep_stages):
            if stage > 0 and stage != 9:
                if first_sleep is None:
                    first_sleep = i
                last_sleep = i
        
        if first_sleep is None:
            return 0
        
        sleep_period = sleep_stages[first_sleep:last_sleep+1]
        wake_epochs = np.sum(sleep_period == 0)
        return wake_epochs * 0.5
    
    def count_awakenings(self, sleep_stages):
        """Number of awakening episodes"""
        first_sleep = None
        for i, stage in enumerate(sleep_stages):
            if stage > 0 and stage != 9:
                first_sleep = i
                break
        
        if first_sleep is None:
            return 0
        
        awakenings = 0
        in_wake = False
        
        for stage in sleep_stages[first_sleep:]:
            if stage == 0:
                if not in_wake:
                    awakenings += 1
                    in_wake = True
            elif stage != 9:
                in_wake = False
        
        return awakenings
    
    def check_early_morning_awakening(self, sleep_stages):
        """Check if final wake exceeds threshold"""
        last_sleep_index = None
        for i in range(len(sleep_stages)-1, -1, -1):
            if sleep_stages[i] > 0 and sleep_stages[i] != 9:
                last_sleep_index = i
                break
        
        if last_sleep_index is None:
            return False
        
        final_wake_duration = (len(sleep_stages) - last_sleep_index - 1) * 0.5
        return final_wake_duration > self.early_wake_threshold
    
    def calculate_all_metrics(self, sleep_stages):
        """Calculate comprehensive sleep metrics"""
        valid_stages = sleep_stages[sleep_stages != 9]
        
        total_sleep_epochs = np.sum((valid_stages > 0) & (valid_stages != 9))
        total_sleep_time = total_sleep_epochs * 0.5
        time_in_bed = len(valid_stages) * 0.5
        sleep_efficiency = (total_sleep_time / time_in_bed * 100) if time_in_bed > 0 else 0
        
        stage_percents = {}
        for stage in [1, 2, 3, 4, 5]:
            count = np.sum(valid_stages == stage)
            stage_percents[f'N{stage}_percent'] = (count / len(valid_stages) * 100) if len(valid_stages) > 0 else 0
        
        return {
            'SOL_minutes': self.calculate_sleep_onset_latency(sleep_stages),
            'WASO_minutes': self.calculate_wake_after_sleep_onset(sleep_stages),
            'num_awakenings': self.count_awakenings(sleep_stages),
            'early_morning_awakening': self.check_early_morning_awakening(sleep_stages),
            'total_sleep_time_minutes': total_sleep_time,
            'time_in_bed_minutes': time_in_bed,
            'sleep_efficiency_percent': sleep_efficiency,
            **stage_percents
        }
    
    def classify_insomnia_subtype(self, metrics):
        """Classify into insomnia subtype"""
        SOL = metrics['SOL_minutes']
        WASO = metrics['WASO_minutes']
        num_awakenings = metrics['num_awakenings']
        early_wake = metrics['early_morning_awakening']
        sleep_efficiency = metrics['sleep_efficiency_percent']
        
        if (SOL < self.SOL_threshold and WASO < self.WASO_threshold and 
            sleep_efficiency > self.sleep_efficiency_threshold and not early_wake):
            return "Good_Sleeper"
        elif SOL > self.SOL_threshold:
            if WASO < self.WASO_threshold and not early_wake:
                return "Sleep_Onset_Insomnia"
            else:
                return "Mixed_Insomnia"
        elif WASO > self.WASO_threshold or num_awakenings > self.awakening_threshold:
            if not early_wake and SOL < self.SOL_threshold:
                return "Sleep_Maintenance_Insomnia"
            else:
                return "Mixed_Insomnia"
        elif early_wake:
            return "Early_Morning_Awakening"
        elif sleep_efficiency < self.sleep_efficiency_threshold:
            return "Poor_Sleeper_Unspecified"
        else:
            return "Good_Sleeper"
    
    def process_all_subjects(self):
        """Process all hypnogram files"""
        print()
        print("=" * 80)
        print("PROCESSING HYPNOGRAMS AND GENERATING LABELS")
        print("=" * 80)
        
        data_path = Path(self.data_dir)
        hypno_files = sorted(list(data_path.glob('*-Hypnogram.edf')))
        
        if len(hypno_files) == 0:
            print()
            print("❌ ERROR: No hypnogram files found!")
            print(f"   Looking in: {self.data_dir}/")
            print()
            self.print_download_instructions()
            return None
        
        print(f"Found {len(hypno_files)} recordings")
        print()
        
        results = []
        
        for hypno_file in tqdm(hypno_files, desc="Processing", unit="subject"):
            try:
                filename = hypno_file.stem
                subject_id = filename.split('-')[0]
                
                sleep_stages = self.load_hypnogram(hypno_file)
                
                if sleep_stages is None or len(sleep_stages) == 0:
                    continue
                
                metrics = self.calculate_all_metrics(sleep_stages)
                subtype = self.classify_insomnia_subtype(metrics)
                
                result = {'subject_id': subject_id, 'insomnia_subtype': subtype, **metrics}
                results.append(result)
                
            except Exception as e:
                print(f"\nError processing {hypno_file.name}: {e}")
                continue
        
        df = pd.DataFrame(results)
        
        print()
        print("=" * 80)
        print("PROCESSING SUMMARY")
        print("=" * 80)
        print(f"Successfully processed: {len(df)} subjects")
        print()
        print("Insomnia Subtype Distribution:")
        print(df['insomnia_subtype'].value_counts().to_string())
        print()
        
        return df
    
    def save_labeled_dataset(self, df):
        """Save labeled dataset"""
        output_file = os.path.join(self.output_dir, 'labeled_insomnia_dataset.csv')
        df.to_csv(output_file, index=False)
        
        print("=" * 80)
        print("DATASET SAVED")
        print("=" * 80)
        print(f"File: {output_file}")
        print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
        print()
        
        summary_file = os.path.join(self.output_dir, 'dataset_summary.txt')
        with open(summary_file, 'w') as f:
            f.write("INSOMNIA DATASET SUMMARY\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Total Subjects: {len(df)}\n\n")
            f.write("Insomnia Subtype Distribution:\n")
            f.write(df['insomnia_subtype'].value_counts().to_string())
            f.write("\n\n")
            f.write("Sleep Metrics Summary:\n")
            f.write(df[['SOL_minutes', 'WASO_minutes', 'sleep_efficiency_percent']].describe().to_string())
        
        print(f"Summary: {summary_file}")
        print("=" * 80)
        print()
        
        return output_file

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    import sys
    
    pipeline = SleepEDFPipeline()
    
    # Check command line arguments
    if '--help' in sys.argv:
        print("\n🚀 Sleep-EDF Insomnia Classification Pipeline")
        print("\nUsage:")
        print("  python pipeline.py                # Auto-download with wget + process")
        print("  python pipeline.py --skip-download # Process existing files only")
        print("  python pipeline.py --manual        # Show manual download instructions")
        print()
        sys.exit(0)
    
    if '--manual' in sys.argv:
        pipeline.print_manual_instructions()
        sys.exit(0)
    
    # Default behavior: download with wget then process
    if '--skip-download' not in sys.argv:
        print("\n🚀 Starting automatic download with wget...")
        result = pipeline.download_with_wget()
        
        if not result.get('success'):
            print("\n⚠️  Automatic download failed.")
            pipeline.print_manual_instructions()
            print("\nAfter manual download, run:")
            print("  python pipeline.py --skip-download")
            print()
            sys.exit(1)
    else:
        print("\n⏭️  Skipping download (using existing files)")
    
    # Process existing files
    print("\n🚀 Processing hypnogram files...")
    df = pipeline.process_all_subjects()
    
    if df is not None and len(df) > 0:
        pipeline.save_labeled_dataset(df)
        
        print()
        print("=" * 80)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 80)
        print(f"Dataset ready: processed_data/labeled_insomnia_dataset.csv")
        print(f"Total subjects: {len(df)}")
        print()
        print("Next steps:")
        print("  1. Review: processed_data/labeled_insomnia_dataset.csv")
        print("  2. Check: processed_data/dataset_summary.txt")
        print("  3. Proceed to feature extraction and ML training")
        print("=" * 80)
        print()
    else:
        print("\n❌ No data to process.")
        print("\nMake sure files are in sleep_edf_data/ folder")
        pipeline.print_manual_instructions()