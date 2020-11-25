import numpy as np
import matplotlib.pyplot as plt
import librosa
from numpy import dot
from numpy.linalg import norm

from config import Config
from chords_util import Chords_Util

cfg = Config()
chord_util = Chords_Util()


class Detection:
    def __init__(self):
        self.threshold = 100
        self.c_dict = {}

    def reset_dict(self):
        for note in chord_util.notes:
            for variation in chord_util.variation:
                self.c_dict[note+variation] = 0

    def detect_chords(self, chroma_cqt, onset_time):
        vectors = chord_util.generate_vectors()
        print(f"[DETECT] Data: {chroma_cqt.shape[0]} frames x {cfg.hop_length} hop_length")
        self.reset_dict()
        res_chords = []
        res_time = []
        prev_detected = ""
        for i in range(len(chroma_cqt)):
            max_sim = 0
            estimated = ''
            # Estimate the chords of each hop according to cosine sim
            for key in vectors.keys():
                if norm(chroma_cqt[i]) * norm(vectors[key]):
                    cos_sim = dot(chroma_cqt[i], vectors[key]) / (norm(chroma_cqt[i]) * norm(vectors[key]))
                else:
                    cos_sim = 0
                if cos_sim > max_sim:
                    max_sim = cos_sim
                    estimated = key

            # Put estimate either in dict or output if exceeds threshold
            if self.c_dict.get(estimated) is None:
                self.c_dict[estimated] = 0
            elif self.c_dict.get(estimated) < cfg.threshold:
                self.c_dict[estimated] += 1
            else:
                reset_second = i * cfg.hop_length / cfg.sr
                # Snap the second exceeding threshold to nearest onset time
                closest = onset_time[np.abs(np.subtract.outer(onset_time, reset_second)).argmin(0)]

                # Assuming no duplicated detection
                if estimated != prev_detected:
                    res_chords.append(estimated)
                res_time.append(closest)
                prev_detected = estimated
                self.reset_dict()

        return res_chords, res_time

    def get_chroma_cqt(self, y, sr):
        chroma_cqt = librosa.feature.chroma_cqt(y=y, sr=sr,
                                                hop_length=cfg.hop_length, n_chroma=cfg.n_chroma)
        chroma_cqt_trans = chroma_cqt.transpose()
        if cfg.verbose:
            librosa.display.specshow(chroma_cqt_trans, y_axis='s', x_axis='chroma')
            plt.show()
            print(f"[CQT] Shape of CQT transpose array: {chroma_cqt_trans.shape}")
        return chroma_cqt_trans

    def get_onset_time(self, y, sr):
        # onset_env = librosa.onset.onset_strength(y, sr=sr)
        onset_frames = librosa.onset.onset_detect(y, sr=sr, wait=1,
                                                  pre_avg=1, post_avg=1, pre_max=1, post_max=1)

        # onset_frames = librosa.util.peak_pick(onset_env, 7, 7, 7, 7, 0.5, 5)
        # dtempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr,
        # aggregate=None)
        # print(dtempo/60)
        return librosa.frames_to_time(onset_frames)

    def get_hps(self, X, f_s):
        # initialize
        iOrder = 2
        f_min = 300
        f = np.zeros(X.shape[1])

        iLen = int((X.shape[0] - 1) / iOrder)
        afHps = X[np.arange(0, iLen), :]
        k_min = int(round(f_min / f_s * 2 * (X.shape[0] - 1)))

        # compute the HPS
        for j in range(1, iOrder):
            X_d = X[::(j + 1), :]
            afHps *= X_d[np.arange(0, iLen), :]

        return afHps
        f = np.argmax(afHps[np.arange(k_min, afHps.shape[0])], axis=0)
        # # find max index and convert to Hz
        return (f + k_min) / (X.shape[0] - 1) * f_s / 2

    def get_chroma(self, X, f_s):
        isSpectrum = X.ndim == 1
        if isSpectrum:
            X = np.expand_dims(X, axis=1)

        # allocate memory
        v_pc = np.zeros([12, X.shape[1]])

        # generate filter matrix
        H = self.generatePcFilters(X.shape[0], f_s)

        # compute pitch chroma
        v_pc = np.dot(H, X ** 2)

        # norm pitch chroma to a sum of 1 but avoid div by zero
        norm = v_pc.sum(axis=0, keepdims=True)
        norm[norm == 0] = 1
        v_pc = v_pc / norm
        return np.squeeze(v_pc) if isSpectrum else v_pc

    def generatePcFilters(self, iSpecLength, f_s):

        # initialization at C4
        f_mid = 261.63
        iNumOctaves = 4
        iNumPitchesPerOctave = 12

        # sanity check
        while (f_mid * 2 ** iNumOctaves > f_s / 2.):
            iNumOctaves = iNumOctaves - 1

        H = np.zeros([iNumPitchesPerOctave, iSpecLength])

        # for each pitch class i create weighting factors in each octave j
        for i in range(0, iNumPitchesPerOctave):
            afBounds = np.array(
                [2 ** (-1 / (2 * iNumPitchesPerOctave)), 2 ** (1 / (2 * iNumPitchesPerOctave))]) * f_mid * 2 * (
                                   iSpecLength - 1) / f_s
            for j in range(0, iNumOctaves):
                iBounds = np.array([math.ceil(2 ** j * afBounds[0]), math.ceil(2 ** j * afBounds[1])])
                H[i, range(iBounds[0], iBounds[1])] = 1 / (iBounds[1] - iBounds[0])

            # increment to next semi-tone
            f_mid = f_mid * 2 ** (1 / iNumPitchesPerOctave)

        return (H)