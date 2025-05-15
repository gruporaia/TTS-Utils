#!/bin/bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate nemo_tn

python3 ../scripts/normalization/normalization.py "$1" "$2"

conda deactivate