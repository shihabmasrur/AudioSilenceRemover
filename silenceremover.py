import librosa
import soundfile as sf
import numpy as np
import os

# =========================================
# CONFIG
# =========================================

INPUT_FILE = "input.mp3"
OUTPUT_FILE = "output.mp3"

# Higher = removes more quiet parts
# Typical values: 20 - 40
TOP_DB = 30

# =========================================
# LOAD AUDIO
# =========================================

print("Loading audio...")

y, sr = librosa.load(INPUT_FILE, sr=None)

print(f"Sample Rate: {sr}")
print(f"Audio Length: {len(y)/sr:.2f} seconds")

# =========================================
# DETECT NON-SILENT PARTS
# =========================================

print("Detecting speech/non-silent sections...")

intervals = librosa.effects.split(
    y,
    top_db=TOP_DB
)

print(f"Found {len(intervals)} audio sections")

# =========================================
# REMOVE SILENCE
# =========================================

print("Removing silence...")

cleaned_audio = np.concatenate([
    y[start:end]
    for start, end in intervals
])

# =========================================
# SAVE OUTPUT
# =========================================

sf.write(OUTPUT_FILE, cleaned_audio, sr)

print("\nDone.")
print(f"Saved cleaned audio as: {OUTPUT_FILE}")