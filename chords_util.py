import numpy as np
import pygame.midi
import time

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
C4 = 60


class Chords_Util:
    def __init__(self):
        self.notes = NOTES
        self.chords = {}
        self.c_vector = {}
        for note in NOTES:
            self.c_vector[note] = np.zeros(len(NOTES))
            self.c_vector[note + 'm'] = np.zeros(len(NOTES))

    def generate_vectors(self):
        # Foreach notes
        for i in range(len(NOTES)):
            # Major and Minor
            for j in range(2):
                target = NOTES[i] if j == 0 else NOTES[i] + 'm'
                third = (i+4) % 12 if j == 0 else (i+3) % 12
                fifth = (i+7) % 12

                self.c_vector[target][i] = 1
                self.c_vector[target][third] = 1
                self.c_vector[target][fifth] = 1
                self.chords[target] = [NOTES[i], NOTES[third], NOTES[fifth]]

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
