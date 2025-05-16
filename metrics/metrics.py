import librosa
import torch 
import torchaudio
from huggingface_hub import hf_hub_download
import numpy as np
import whisper
import unicodedata
from pathlib import Path
from typing import Union
import re
from Levenshtein import distance as _lev 

# Predicts UTMOS score for a given audio file
def UTMOS(audio_path: Union[str, Path]) -> float:
    wave, sr = librosa.load(audio_path, sr=None, mono=True)
    predictor = torch.hub.load("tarepan/SpeechMOS:v1.2.0", "utmos22_strong", trust_repo=True)
    return predictor(torch.from_numpy(wave).unsqueeze(0), sr)

# Computes SECS (embedding similarity) between reference and generated audio
def SECS(ref_wav: Union[str, Path], gen_wav: Union[str, Path]) -> float:
    model_file = hf_hub_download(repo_id='Jenthe/ECAPA2', filename='ecapa2.pt')
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    ecapa2 = torch.jit.load(model_file, map_location=device)

    g, sr = torchaudio.load(gen_wav)
    r, sr = torchaudio.load(ref_wav)

    r_emb = ecapa2(r.to(device, non_blocking=True)).cpu()[0]
    g_emb = ecapa2(g.to(device, non_blocking=True)).cpu()[0]

    return float(np.dot(r_emb, g_emb) / (np.linalg.norm(r_emb) * np.linalg.norm(g_emb)))



# Transcribe audio using Whisper
def _asr_transcribe(audio: Union[str, Path], lang: str | None = None) -> str:
    # Load Whisper ASR model
_   asr = whisper.load_model("tiny")
    result = _asr.transcribe(str(audio), fp16=torch.cuda.is_available(), language=lang)
    return result["text"].strip()

# Remove punctuation and symbols
def _strip_punct_and_symbols(txt: str) -> str:
    return "".join(ch for ch in txt if unicodedata.category(ch)[0] not in {"P", "S"})

# Normalize text: lowercase, remove symbols, normalize spaces
_ws_re = re.compile(r"\s+")
def _norm(txt: str) -> str:
    txt = txt.lower()
    txt = _strip_punct_and_symbols(txt)
    return _ws_re.sub(" ", txt).strip()

# Compute Character Error Rate between reference and transcribed text
def CER(audio_path: Union[str, Path], reference_text: str, *, lang: str | None = "pt", normalise: bool = True) -> float:
    hyp = _asr_transcribe(audio_path, lang)
    if normalise:
        reference_text, hyp = _norm(reference_text), _norm(hyp)
    return _lev(reference_text, hyp) / max(1, len(reference_text))
