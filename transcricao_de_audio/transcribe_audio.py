import whisper
from pydub import AudioSegment
from pydub.silence import split_on_silence
import pandas as pd
import os
import glob
import argparse

# Load Whisper model
model = whisper.load_model("base")

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Process audio files for transcription.")
parser.add_argument("input_dir", type=str, help="Directory containing the audio files.")
parser.add_argument("output_dir", type=str, help="Directory to save the processed files.")
args = parser.parse_args()

# Directories
input_dir = args.input_dir
output_dir = args.output_dir
audio_dir = os.path.join(output_dir, "wavs")
os.makedirs(audio_dir, exist_ok=True)

# Silence detection parameters
min_silence_len = 900  # milliseconds
keep_silence = 400     # milliseconds
min_chunk_length = 2000

# Process all MP3 and WAV files
audio_files = sorted(glob.glob(os.path.join(input_dir, "*.mp3")) + glob.glob(os.path.join(input_dir, "*.wav")))

for audio_file in audio_files:
    print(f"--> Processing {audio_file}")
    # Load audio file, handle both MP3 and WAV
    if audio_file.endswith(".mp3"):
        audio = AudioSegment.from_mp3(audio_file)
    else:
        audio = AudioSegment.from_wav(audio_file)

    # Calculate silence threshold for current file
    silence_thresh = audio.dBFS - 14

    # Split into chunks
    audio_chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence
    )

    print(f"    Split into {len(audio_chunks)} chunks.")

    file_metadata = []
    file_basename = os.path.splitext(os.path.basename(audio_file))[0]

    for i, chunk in enumerate(audio_chunks):
        if len(chunk) < min_chunk_length:
            continue

        sentence_id = f"{file_basename}_{str(i + 1).zfill(4)}"
        chunk_path = os.path.join(audio_dir, f"{sentence_id}.wav")

        # Export chunk to disk as WAV
        chunk.export(chunk_path, format="wav")

        # Transcribe chunk
        result = model.transcribe(chunk_path, language="pt")
        text = result['text'].strip()

        file_metadata.append({
            "ID": sentence_id,
            "text": text,
            "textCleaned": text.lower()
        })

    # Save metadata CSV for this file
    file_df = pd.DataFrame(file_metadata)
    file_csv_path = os.path.join(output_dir, f"metadata.csv")
    file_df.to_csv(file_csv_path, sep="|", header=False, index=False, mode="a")

    print(f"    Transcriptions saved to: {file_csv_path}")

print("\nAll files processed!")

