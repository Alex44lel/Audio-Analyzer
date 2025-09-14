# Audio Analyzer

Small, focused tools to record audio from your microphone and visualize it as a waveform, FFT spectrum, and spectrogram. Includes:
- A live, low-latency viewer built with PyQtGraph.
- A one-shot recorder that saves a WAV and an analysis image.

<img width="1141" height="943" alt="image" src="https://github.com/user-attachments/assets/d6434384-b09b-40f8-8af0-9408a71346d2" />


Files:
- [live_audio_to_chart.py](live_audio_to_chart.py) — real-time visualization (waveform, FFT, spectrogram).
- [audio_to_charts.py](audio_to_charts.py) — records 1 second and saves charts to an image.

## Quick start

1) Create and activate a virtual environment (optional, recommended):

2) Install dependencies:
```bash
python -m pip install -r requirements.txt
```

3) Give your terminal/app microphone permission (OS-dependent).

## How to run

### Live viewer (recommended)
Shows waveform, FFT, and spectrogram in real-time. Use the docked spin box to change sampling rate.

```bash
python live_audio_to_chart.py
```

What you’ll see:
- Waveform (top)
  - Time range: last 1 second (modifiable).
  - Y range: [-0.05, 0.05] (audio from sounddevice is normalized to [-1, 1]) (modifiable).
- FFT Spectrum (middle)
  - Hann window applied to the 1-second buffer.
  - Frequency axis limited to 0–6 kHz (modifiable) for readability.
- Spectrogram (bottom)
  - STFT size: 1024 (Hann window) (modifiable).
  - Scrolls left to right using a fixed-width image buffer.
  - Colormap: inferno, levels in dB [-80, 0].

Controls:
- “Sampling rate (Hz)” spin box: 2000–96000 Hz. The app restarts the input stream when this changes.



Script: [live_audio_to_chart.py](live_audio_to_chart.py)

### One-shot analysis (records 1 second)
Records 1 second at 44.1 kHz mono, writes a WAV, and saves charts (waveform, FFT, STFT spectrogram, Mel spectrogram) to an image.

```bash
python audio_to_charts.py
```

Outputs:
- `recording.wav` — 16-bit PCM.
- `audio_analisis.png` — figure with 4 panels:
  - Waveform
  - DFT (magnitude spectrum)
  - STFT Spectrogram (n_fft=1024, hop_length=512)
  - Mel Spectrogram (64 mels, HTK scale)

Script: [audio_to_charts.py](audio_to_charts.py)
