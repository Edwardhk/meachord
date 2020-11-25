import numpy as np
import pygame.midi
import time
import librosa
import sounddevice as sd
from config import Config

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
VARIATION = ['', 'm', '7', 'm7']
C4 = 60

cfg = Config()

class Chords_Util:
    def __init__(self):
        self.notes = NOTES
        self.variation = VARIATION
        self.chords = {}
        self.c_vector = {}
        for note in NOTES:
            for var in VARIATION:
                self.c_vector[note+var] = np.zeros(len(NOTES))
        self.c_vector['N'] = np.zeros(len(NOTES))

    def generate_vectors(self):
        # Foreach notes
        for i in range(len(NOTES)):
            for var in VARIATION:
                target_name = NOTES[i] + var

                # Set root and fifth
                self.c_vector[target_name][i] = 1
                self.c_vector[target_name][(i + 7) % 12] = 1

                # Check minor
                if 'm' in var:
                    self.c_vector[target_name][(i+3) % 12] = 1
                else:
                    self.c_vector[target_name][(i+4) % 12] = 1

                # Check seventh
                if '7' in var:
                    self.c_vector[target_name][(i+11) % 12] = 1

        return self.c_vector

    def validate(self, scale):
        if self.chords.get(scale) is not None:
            return scale
        # Translate flat to sharp
        else:
            res = ""
            if scale == "Db":
                res = "C#"
            elif scale == "Eb":
                res = "D#"
            elif scale == "Gb":
                res = "F#"
            elif scale == "Ab":
                res = "G#"
            elif scale == "Bb":
                res = "A#"
            else:
                print(f"[Validate] Wrong chord input!")
            print(f"[Validate] Given {scale}, translated into {res}")
            return res

    def vec_to_chords(self, vec):
        res = []
        for i in range(len(vec)):
            if vec[i]:
                res.append(self.notes[i])
        return res

    def load_audio(self, filename, dur=None):
        print("[LOAD] Start loading audio...")
        y, sr = librosa.load(filename, duration=dur, sr=cfg.sr)
        minute = int(y.shape[0] / sr / 60)
        second = y.shape[0] / sr % 60
        print(f"[LOAD] Loaded audio with {minute} minutes and {second:.2f} seconds...")
        print(f"[LOAD] Sample rate: {sr}")
        print(f"[LOAD] Data shape: {y.shape}")
        return y, sr

    def play_audio(self, y, sr):
        sd.play(y, sr, blocking=True)

    def play_chords_audio(self, scale='C', dur=0.5, vol=127, vec_input=None):
        scale = self.validate(scale)
        if self.chords.get(scale) is None:
            print("[ERROR] Wrong scale given")
            return
        pygame.midi.init()
        player = pygame.midi.Output(0)

        chords = self.chords.get(scale)
        print(f"[CHORD] Playing {chords}")
        player.note_on(C4 + NOTES.index(chords[0]), vol)
        player.note_on(C4 + NOTES.index(chords[1]), vol)
        player.note_on(C4 + NOTES.index(chords[2]), vol)
        time.sleep(dur)
        player.note_off(C4 + NOTES.index(chords[0]), vol)
        player.note_off(C4 + NOTES.index(chords[1]), vol)
        player.note_off(C4 + NOTES.index(chords[2]), vol)

        del player
        pygame.midi.quit()
