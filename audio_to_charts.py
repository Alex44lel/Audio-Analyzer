import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import librosa
import librosa.display
import matplotlib.pyplot as plt


sampling_rate = 44100
duration = 1 # seconds

#--------------RECORD AUDIO------------------
print("RECORDING....")
audio = sd.rec(sampling_rate*duration,samplerate=sampling_rate,channels=1)
sd.wait()

#sd.rec records in values from -1 to 1 but wav files expect integers
wav.write("recording.wav", sampling_rate, (audio * 32767).astype(np.int16))
audio=audio.flatten()
print(audio)
print("END RECORDING....")

# ======================
# 1. Plot raw waveform
# ======================

fig, axes = plt.subplots(4, 1, figsize=(14, 10))


time = np.linspace(0,duration,len(audio))
axes[0].plot(time,audio)
axes[0].set_title("Waveform")


# ======================
# 2. DFT (frequency spectrum)
# ======================

N = len(audio)
print(N)
freqs= np.fft.rfftfreq(N,d=1/sampling_rate)
fft_magnitude = np.abs(np.fft.rfft(audio))
axes[1].plot(freqs, fft_magnitude)
axes[1].set_title("DFT (Magnitude Spectrum)")
axes[1].set_xlabel("Frequency [Hz]")
axes[1].set_ylabel("Magnitude")

# ======================
# 3. STFT spectrogram
# ======================

n_fft = 1024
hop_length = 512

D = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
print(D.shape)
S_db = librosa.amplitude_to_db(np.abs(D),ref=np.max)
img = librosa.display.specshow(S_db, sr=sampling_rate, hop_length=hop_length, x_axis='time', y_axis='hz', ax=axes[2])
plt.colorbar(img, ax=axes[2], format='%+2.0f dB')
axes[2].set_title("STFT Spectrogram")

number_mels = 64
S = librosa.feature.melspectrogram(y=audio, sr=sampling_rate, n_fft=n_fft, hop_length=hop_length, n_mels=number_mels, htk=True)
S_db_mel = librosa.power_to_db(S, ref=np.max)
img = librosa.display.specshow(S_db_mel, sr=sampling_rate, hop_length=256, x_axis='time', y_axis='mel', htk=True, ax=axes[3])
plt.colorbar(img,format='%+2.0f dB', ax=axes[3])
axes[3].set_title("Mel Spectrogram (HTK scale)")


plt.tight_layout()
plt.savefig("audio_analisis.png")

