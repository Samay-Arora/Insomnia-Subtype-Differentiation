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
