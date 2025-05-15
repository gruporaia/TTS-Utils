#!/bin/bash

source ~/miniconda3/etc/profile.d/conda.sh

conda activate transcricao_audio_env

python3 ../scripts/transcricao_de_audio/transcribe_audio.py "$1" "$2"

conda deactivate
