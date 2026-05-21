import librosa
import soundfile as sf
import numpy as np


def remove_silence(input_file, output_file, top_db, min_duration_ms):

    y, sr = librosa.load(input_file, sr=None)

    intervals = librosa.effects.split(
        y,
        top_db=top_db
    )

    min_samples = int(sr * min_duration_ms / 1000)

    intervals = [
        (start, end)
        for start, end in intervals
        if (end - start) >= min_samples
    ]

    if len(intervals) == 0:
        raise Exception("No audio left after silence removal")

    cleaned_audio = np.concatenate([
        y[start:end]
        for start, end in intervals
    ])

    sf.write(output_file, cleaned_audio, sr)

    return True