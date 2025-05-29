from faster_whisper import WhisperModel
from pydub import AudioSegment
import pandas as pd
import os
import glob
import re
from .normalization import normalize_text

def build_dataset(input_dir, output_dir):
    # Load Whisper model
    model_size = "base"
    model = WhisperModel(model_size, compute_type="int8" if model_size == "large" else "auto")

    # Directories
    audio_dir = os.path.join(output_dir, "wavs")
    os.makedirs(audio_dir, exist_ok=True)

    def ends_with_punctuation(text):
        return bool(re.search(r'[.!?](?:["”])?$|…$', text.strip()))

    def split_text_into_phrases(text):
        phrases = re.split(r'(?<=[.!?])\s+', text.strip())
        return [phrase.strip() for phrase in phrases if phrase]

    # Process audio files
    audio_files = sorted(
        glob.glob(os.path.join(input_dir, "**", "*.mp3"), recursive=True) +
        glob.glob(os.path.join(input_dir, "**", "*.wav"), recursive=True)
    )

    all_metadata = []

    for audio_file in audio_files:
        print(f"Processing: {audio_file}")
        base_name = os.path.splitext(os.path.basename(audio_file))[0]

        # Load and preprocess audio
        audio = AudioSegment.from_file(audio_file).set_channels(1).set_frame_rate(16000)
        audio = audio.high_pass_filter(80)

        # Transcribe
        segments, _ = model.transcribe(
            audio_file,
            language="pt",
            vad_filter=False,
            word_timestamps=False,
            beam_size=5
        )

        # Build grouped phrases with timing
        grouped_segments = []
        current_group = []
        group_start = None

        for seg in segments:
            if not current_group:
                group_start = seg.start
            current_group.append(seg)

            if ends_with_punctuation(seg.text):
                full_text = " ".join(s.text.strip() for s in current_group)
                phrases = split_text_into_phrases(full_text)
                total_duration = sum(s.end - s.start for s in current_group)

                if phrases:
                    avg_duration = total_duration / len(phrases)
                    for idx, phrase in enumerate(phrases):
                        phrase_start = group_start + idx * avg_duration
                        phrase_end = phrase_start + avg_duration

                        transformed = normalize_text(phrase)

                        segment_data = {
                            "ID": f"{base_name}_{len(grouped_segments)+1:04d}",
                            "start": round(phrase_start, 2),
                            "end": round(phrase_end, 2),
                            "text": phrase,
                            "textCleaned": transformed.lower()
                        }
                        grouped_segments.append(segment_data)

                current_group = []

        if current_group:
            group_start = current_group[0].start
            full_text = " ".join(s.text.strip() for s in current_group)
            phrases = split_text_into_phrases(full_text)
            total_duration = sum(s.end - s.start for s in current_group)

            if phrases:
                avg_duration = total_duration / len(phrases)
                for idx, phrase in enumerate(phrases):
                    phrase_start = group_start + idx * avg_duration
                    phrase_end = phrase_start + avg_duration

                    transformed = normalize_text(phrase)

                    segment_data = {
                        "ID": f"{base_name}_{len(grouped_segments)+1:04d}",
                        "start": round(phrase_start, 2),
                        "end": round(phrase_end, 2),
                        "text": phrase,
                        "textCleaned": transformed.lower()
                    }
                    grouped_segments.append(segment_data)

        # Create DataFrame
        df = pd.DataFrame(grouped_segments)

        # Export each audio segment
        for row in df.itertuples(index=False):
            start_ms = int(row.start * 1000)
            end_ms = int(row.end * 1000)

            if end_ms > start_ms:
                phrase_audio = audio[start_ms:end_ms]
                chunk_path = os.path.join(audio_dir, f"{row.ID}.wav")
                print(f"Exporting: {chunk_path}")
                phrase_audio.export(chunk_path, format="wav", parameters=["-ar", "16000"])

        # Drop timestamp columns and append to all_metadata
        df = df.drop(columns=["start", "end"])
        all_metadata.append(df)

    # Combine all metadata and save final CSV
    final_df = pd.concat(all_metadata, ignore_index=True)
    final_csv_path = os.path.join(output_dir, "metadata.csv")
    final_df.to_csv(final_csv_path, sep="|", index=False, header=True)
    print(f"Saved final metadata to {final_csv_path}")

    print("Processing complete!")
