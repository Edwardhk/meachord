import matplotlib.pyplot as plt
import numpy as np
import librosa
import soundfile as sf
import librosa.display
from chords_util import Chords_Util
import sounddevice as sd

SAMPLE_RATE = 44100
DURATION = 20
N_CHROMA = 12
HOP_LENGTH = 512

def load_audio(filename, dur=None):
    print("[LOAD] Start loading audio...")
    y, sr = librosa.load(filename, duration=dur, sr=SAMPLE_RATE)
    minute = int(y.shape[0] / sr / 60)
    second = y.shape[0] / sr % 60
    print(f"[LOAD] Loaded audio with {minute} minutes and {second:.2f} seconds...")
    print(f"[LOAD] Sample rate: {sr}")
    print(f"[LOAD] Data shape: {y.shape}")
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


def get_onset_data(y, sr):
    onset_env = librosa.onset.onset_strength(y, sr=sr)
    # onset_frames = librosa.onset.onset_detect(y, sr=sr, wait=1,
    #                                           pre_avg=1, post_avg=1, pre_max=1, post_max=1,
    #                                           backtrack=True)
    onset_frames = librosa.util.peak_pick(onset_env, 7, 7, 7, 7, 0.5, 5)
    onset_times = librosa.frames_to_time(onset_frames)
    clicks = librosa.clicks(frames=onset_frames, sr=sr, length=len(y))
    # play_audio(y+clicks, sr)
    #dtempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr,
                                # aggregate=None)
    #print(dtempo/60)


def main():
    chords_util = Chords_Util()
    vecs = chords_util.generate_vectors()
    y, sr = load_audio('src/audio_input/Janice.wav', dur=DURATION)
    chroma_cqt, max_pitch_index = get_chroma_cqt(y, sr)
    # get_onset_data(y, sr)
    # print(dtempo)

    # pitch_count_dict = {}
    # for i in range(max_pitch_index.shape[0]):
    #     max_pitch = BASE_NOTE[max_pitch_index[i]]
    #     if max_pitch not in pitch_count_dict:
    #         pitch_count_dict[max_pitch] = 0
    #     else:
    #         pitch_count_dict[max_pitch] += 1
    # print(pitch_count_dict)


if __name__ == '__main__':
    main()

