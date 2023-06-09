"""
This files creates the X and y features in joblib to be used by the predictive models.
"""

import os
import time
import joblib
import librosa
import numpy as np

from config import SAVE_DIR_PATH
from config import TRAINING_FILES_PATH


class CreateFeatures:

    @staticmethod
    def features_creator(path, save_dir) -> str:
        """
        This function creates the dataset and saves both data and labels in
        two files, X.joblib and y.joblib in the joblib_features folder.
        With this method, you can persist your features and train quickly
        new machine learning models instead of reloading the features
        every time with this pipeline.
        """

        lst = []
        max_features_len = 0

        start_time = time.time()

        for subdir, dirs, files in os.walk(path):
            for file in files:
                try:
                    print("Processing %s" % file, end='\r')

                    # Load librosa array, obtain mfcss, store the file and the mcss information in a new array
                    X, sample_rate = librosa.load(os.path.join(subdir, file),
                                                  res_type='kaiser_fast')

                    mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate,
                                                         n_mfcc=40).T, axis=0)
                    mel_spec = np.mean(librosa.feature.melspectrogram(y=X, sr=sample_rate,
                                                                      n_fft=4096).T, axis=0)
                    contrast = np.mean(librosa.feature.spectral_contrast(y=X, sr=sample_rate,
                                                                         n_fft=2048).T, axis=0)

                    chroma = librosa.feature.chroma_stft(y=X, sr=sample_rate,
                                                         n_fft=2048).T
                    tonnetz = np.mean(librosa.feature.tonnetz(y=X, sr=sample_rate,
                                                              chroma=chroma).T, axis=0)
                    chroma = np.mean(chroma, axis=0)

                    if max_features_len == 0:
                        max_features_len = max(len(mfccs), len(mel_spec), len(contrast), len(chroma), len(tonnetz))

                    # Pad features to match the max length
                    mfccs = np.pad(mfccs, (0, max_features_len - len(mfccs)))
                    mel_spec = np.pad(mel_spec, (0, max_features_len - len(mel_spec)))
                    contrast = np.pad(contrast, (0, max_features_len - len(contrast)))
                    chroma = np.pad(chroma, (0, max_features_len - len(chroma)))
                    tonnetz = np.pad(tonnetz, (0, max_features_len - len(tonnetz)))

                    # The instruction below converts the labels (from 1 to 8) to a series from 0 to 7
                    # This is because our predictor needs to start from 0 otherwise it will try to predict also 0.
                    file = int(file[7:8]) - 1
                    arr = (mfccs, mel_spec, contrast, chroma, tonnetz), file
                    lst.append(arr)
                # If the file is not valid, skip it
                except ValueError as err:
                    print(err)
                    continue

        print("--- Data loaded. Loading time: %s seconds ---" %
              (time.time() - start_time))

        # Creating X and y: zip makes a list of all the first elements, and a list of all the second elements.
        X, y = zip(*lst)

        # Array conversion
        X, y = np.asarray(X), np.asarray(y)

        # Array shape check
        print(X.shape, y.shape)

        # Preparing features dump
        X_name, y_name = 'X.joblib', 'y.joblib'

        joblib.dump(X, os.path.join(save_dir, X_name))
        joblib.dump(y, os.path.join(save_dir, y_name))

        return "Completed"


if __name__ == '__main__':
    print('Routine started')
    FEATURES = CreateFeatures.features_creator(
        path=TRAINING_FILES_PATH, save_dir=SAVE_DIR_PATH)
    print('Routine completed.')
