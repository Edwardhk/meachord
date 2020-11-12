import matplotlib.pyplot as plt
import numpy as np
import librosa
import soundfile as sf
import librosa.display
from config import Config
import sounddevice as sd

DURATION = 20
N_CHROMA = 12
HOP_LENGTH = 512
CHORDS_ARR = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def load_audio(filename, dur=None):
    print("[LOAD] Start loading audio...")
    load_y, load_sr = librosa.load(filename, duration=dur)

    minute = int(load_y.shape[0] / load_sr / 60)
    second = load_y.shape[0] / load_sr % 60
    print(f"[LOAD] Loaded audio with {minute} minutes and {second:.2f} seconds...")
    return load_y, load_sr


def play_audio(y, sr):
    sd.play(y, sr, blocking=True)


if __name__ == '__main__':
    y, sr = load_audio('src/audio_input/Apologize.flac', dur=30)
    chroma_cq = librosa.feature.chroma_cqt(y=y, sr=sr,
                                           hop_length=HOP_LENGTH, n_chroma=N_CHROMA)
    max_pitch_index = np.argmax(chroma_cq, axis=0)

    pitch_count_dict = {}

    for i in range(int(sr/HOP_LENGTH)):
        max_pitch = CHORDS_ARR[max_pitch_index[i]]
        if max_pitch not in pitch_count_dict:
            pitch_count_dict[max_pitch] = 0
        else:
            pitch_count_dict[max_pitch] += 1
    print(pitch_count_dict)

