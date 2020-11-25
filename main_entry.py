import matplotlib.pyplot as plt
import numpy as np
import math
import os
import librosa
import librosa.display

from flask import Flask, request, redirect, url_for
from flask_cors import CORS

from config import Config
from chords_util import Chords_Util
from detection import Detection

cfg = Config()
chords_util = Chords_Util()
detection = Detection()

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = "upload_tmp"


@app.route('/detect', methods=['GET', 'POST'])
def detect():
    file_tag = "audioFile"
    if request.method == 'POST':
        if file_tag not in request.files:
            return "File not found!"
        file = request.files[file_tag]
        if file.filename == '':
            return "Empty file name!"
        if file:
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)
            y, sr = chords_util.load_audio(path, dur=cfg.dur)
            chroma_cqt = detection.get_chroma_cqt(y, sr)
            onset_time = detection.get_onset_time(y, sr)
            res_chords, res_time = detection.detect_chords(chroma_cqt, onset_time)
            print(res_chords)
            # os.remove(path)
            return str(res_chords)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()

