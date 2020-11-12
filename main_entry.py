import matplotlib.pyplot as plt
import numpy as np
import librosa
import soundfile as sf
import librosa.display
from config import Config
import sounddevice as sd

DURATION = 10
N_CHROMA = 12
HOP_LENGTH = 512
CHORDS_ARR = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def load_audio(filename, dur=None):
    print("[LOAD] Start loading audio...")
    y, sr = librosa.load(filename, duration=dur)
    minute = int(y.shape[0] / sr / 60)
    second = y.shape[0] / sr % 60
    print(f"[LOAD] Loaded audio with {minute} minutes and {second:.2f} seconds...")
    print(f"[LOAD] Sample rate: {sr}")
    return y, sr


def play_audio(y, sr):
    sd.play(y, sr, blocking=True)


def get_chroma_cqt(y, sr, verbose=False):
    chroma_cqt = librosa.feature.chroma_cqt(y=y, sr=sr,
                                            hop_length=HOP_LENGTH, n_chroma=N_CHROMA)
    max_pitch_index = np.argmax(chroma_cqt, axis=0)
    if verbose:
        librosa.display.specshow(chroma_cqt, y_axis='chroma', x_axis='time')
        plt.show()
        print(f"[CQT] Shape of CQT array: {chroma_cqt.shape}")
        print(f"[CQT] Shape of max_pitch array: {max_pitch_index.shape}")
    return chroma_cqt, max_pitch_index


def main():
    y, sr = load_audio('src/audio_input/Apologize.flac', dur=DURATION)
    chroma_cqt, max_pitch_index = get_chroma_cqt(y, sr, verbose=True)

    pitch_count_dict = {}
    for i in range(max_pitch_index.shape[0]):
        max_pitch = CHORDS_ARR[max_pitch_index[i]]
        if max_pitch not in pitch_count_dict:
            pitch_count_dict[max_pitch] = 0
        else:
            pitch_count_dict[max_pitch] += 1
    print(pitch_count_dict)


if __name__ == '__main__':
    main()

