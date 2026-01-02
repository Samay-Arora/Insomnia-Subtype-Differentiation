# Insomnia-Subtype-Differentiation

## Replication Steps

To replicate the findings of this study, follow these sequential steps. This pipeline is designed to be fully reproducible, handling everything from raw data download to feature extraction automatically.

### Phase 1: Environment Setup for Intel Mac

We use a double Python environment to ensure library compatibility (specifically for `mne`, `antropy`, and `scikit-learn`). Each branch has its own neccesary libraries because they take different approaches.

```bash

git clone [https://github.com/Samay-Arora/Insomnia-Subtype-Differentiation.git](https://github.com/Samay-Arora/Insomnia-Subtype-Differentiation.git)
cd Insomnia-Subtype-Differentiation

# 2. Create a clean virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
# Note: We use --only-binary for numba/llvmlite to avoid compilation errors on macOS
pip install --upgrade pip
pip install --only-binary :all: llvmlite numba
pip install -r requirements.txt
```

### Phase 2: Data Download for Intel Mac

```bash
# 1. Download Sleep-EDF (Healthy + Mild Sleep Difficulty)
# This uses wget to pull ~153 subjects from PhysioNet
mkdir -p sleep_edf_data
cd sleep_edf_data
wget -r -np -nd -A "SC*-PSG.edf" [https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/](https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/)
wget -r -np -nd -A "SC*-Hypnogram.edf" [https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/](https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/)
wget -r -np -nd -A "ST*-PSG.edf" [https://physionet.org/files/sleep-edfx/1.0.0/sleep-telemetry/](https://physionet.org/files/sleep-edfx/1.0.0/sleep-telemetry/)
wget -r -np -nd -A "ST*-Hypnogram.edf" [https://physionet.org/files/sleep-edfx/1.0.0/sleep-telemetry/](https://physionet.org/files/sleep-edfx/1.0.0/sleep-telemetry/)
cd ..

# 2. Download CAP Sleep Database (Insomnia + Healthy Controls)
# We filter specifically for Insomnia (ins*) and Normal (n*) subjects to avoid confounding disorders
mkdir -p cap_data
cd cap_data

# 1. Download Insomnia Patients
wget -r -np -nd -A "ins*.edf" [https://physionet.org/files/capslpdb/1.0.0/](https://physionet.org/files/capslpdb/1.0.0/)
wget -r -np -nd -A "ins*.txt" [https://physionet.org/files/capslpdb/1.0.0/](https://physionet.org/files/capslpdb/1.0.0/)

# 2. Download Healthy Controls (and accidentally grab other 'n' files)
wget -r -np -nd -A "n*.edf" [https://physionet.org/files/capslpdb/1.0.0/](https://physionet.org/files/capslpdb/1.0.0/)
wget -r -np -nd -A "n*.txt" [https://physionet.org/files/capslpdb/1.0.0/](https://physionet.org/files/capslpdb/1.0.0/)

# 3. CLEANUP: Remove confounding disorders (Narcolepsy, Epilepsy, PLM)
rm -f narco* nfle* plm* sdb* rbd*
cd ..
```

### Phase 3: Data Preprocessing for Intel Mac

```bash
python scripts/harmonize.py

python scripts/extract_features.py

# Optional:
# python scripts/clustering.py
# python scripts/chaos_clustering.py

python scripts/insomnia_clustering.py
```
