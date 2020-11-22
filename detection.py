import numpy as np
from numpy import dot
from numpy.linalg import norm
from config import Config
from chords_util import Chords_Util
import matplotlib.pyplot as plt

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

    def detect_chords(self, chroma_cqt, vectors, onset_time):
        print(f"[DETECT] Data: {chroma_cqt.shape[0]} frames x {cfg.hop_length} hop_length")
        self.reset_dict()
        res_chords = []
        res_time = []
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
                # print(closest)
                res_chords.append(estimated)
                res_time.append(closest)
                self.reset_dict()

        return res_chords, res_time
