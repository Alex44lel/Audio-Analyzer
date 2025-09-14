import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import librosa
import librosa.display
import matplotlib.pyplot as plt
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import sys

sampling_rate = 44100
buffer_duration = 1 # seconds showed on the screen
block_size = 1024 # frames per audio block

buffer_size = sampling_rate * buffer_duration

audio_buffer = np.zeros(buffer_size, dtype=np.float32) # circular buffer
write_ptr = 0
stream = None


#this callback is called by the audio thread 
def audio_callback(indata,frames,time,status):
    global audio_buffer ,write_ptr

    if status:
        print(status)

    #extract first channel (this is numpy syntax)
    new_data = indata[:,0]

    n = len(new_data)

    if write_ptr+n < buffer_size:
        audio_buffer[write_ptr:write_ptr+n] = new_data
        write_ptr += n
    else:
        end = buffer_size - write_ptr
        audio_buffer[write_ptr:] = new_data[:end]
        audio_buffer[:n-end] = new_data[end:]
        write_ptr = (write_ptr + n) % buffer_size


# -----------------------------
# PyQtGraph Setup
# -----------------------------

app = QtWidgets.QApplication(sys.argv)
window = pg.GraphicsLayoutWidget(title="Real time audio visualization")
window.resize(1000,400)



#waveform plot:

#adds an empty curve line to the plot_waveform that i will later update
plot_waveform = window.addPlot(title="Waveform")
plot_waveform.setYRange(-0.05, 0.05)
plot_waveform.setXRange(-0.1, 0)
curve_waveform = plot_waveform.plot(pen='c')
plot_waveform.setLabel("bottom","Time",units='s')
plot_waveform.setLabel("left","Amplitude")

time_axis = np.linspace(-buffer_duration,0,buffer_size)


#FFT plot
window.nextRow()
plot_fft = window.addPlot(title="FFT Spectrum")
curve_fft = plot_fft.plot(pen='m')
# plot_fft.setLogMode(x=False, y=True)  # log scale for magnitude (dB-like)
plot_fft.setLabel('bottom', 'Frequency', units='Hz')
plot_fft.setLabel('left', 'Magnitude (HZ)')
plot_fft.setXRange(0, 6000)


fft_size = len(audio_buffer)

freq_axis_fft = np.fft.rfftfreq(fft_size, 1/sampling_rate)

#Spectogram plot
window.nextRow()
img_item =pg.ImageItem()
plot_spec = window.addPlot(title="Spectrogram (STFT)")
plot_spec.addItem(img_item)
plot_spec.setLabel('bottom', 'Time Frames')
plot_spec.setLabel('left', 'Magnitude (HZ)')

stft_size = 1024
spectogram_height = (stft_size // 2) + 1
spectogram_width = 150

spec_data = np.zeros((spectogram_height,spectogram_width))

freq_axis_stft = np.fft.rfftfreq(stft_size, 1/sampling_rate)


lut = pg.colormap.get('inferno').getLookupTable(0.0,1.0,100)
img_item.setLookupTable(lut)
img_item.setLevels([-80, 0])


# -----------------------------
# Update function
# -----------------------------

def update():
    global audio_buffer, write_ptr, spec_data
    #update wave
    rolled = np.roll(audio_buffer,-write_ptr) #puts the most recent sample at the end of the array
    curve_waveform.setData(time_axis,rolled)
    
    #update fft
    window_fn = np.hanning(len(rolled))
    spectrum = np.abs(np.fft.rfft(rolled *window_fn)) 
    curve_fft.setData(freq_axis_fft, spectrum)

    #update stft
    segment = rolled[-stft_size:] * np.hanning(stft_size)
    S = np.abs(np.fft.rfft(segment)) 
    S_db = 20 * np.log10(S + 1e-6)
    
    spec_data = np.roll(spec_data,-1,axis=1)
    spec_data[:, -1] = S_db

    #remember sounddevice normalizes amplitude between -1 and 1


    img_item.setImage(spec_data.transpose(),autoLevels=False)
   # update time axis of spectogram
    frame_duration = stft_size / sampling_rate
    total_time = frame_duration * spectogram_width
    img_item.setRect(
    QtCore.QRectF(
        -total_time,  # start time on the left (negative so it scrolls like your waveform)
        0,            # start freq
        total_time,   # width in seconds
        sampling_rate/2  # height in Hz
        )
    )
    print(stream.samplerate)

# -----------------------------
# Slider Logic
# -----------------------------
def change_sampling_rate(value):
    global sampling_rate, buffer_size, audio_buffer, write_ptr, stream, time_axis, freq_axis_fft

    new_rate = value * 1000  # slider step = kHz
    if new_rate == sampling_rate:
        return

    print(f"Changing sampling rate to {new_rate} Hz")

    sampling_rate = new_rate
    buffer_size = sampling_rate * buffer_duration
    audio_buffer = np.zeros(buffer_size, dtype=np.float32)
    write_ptr = 0

    # update time axis and fft axis
    time_axis = np.linspace(-buffer_duration, 0, buffer_size)
    freq_axis_fft = np.fft.rfftfreq(buffer_size, 1 / sampling_rate)


  

    # restart stream
    if stream:
        stream.stop()
        stream.close()
    stream = sd.InputStream(
        channels=1,
        samplerate=sampling_rate,
        blocksize=block_size,
        callback=audio_callback
    )
    stream.start()


    
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(60)




spinbox = QtWidgets.QSpinBox()
spinbox.setRange(2000, 96000)  # valid range of sampling rates in Hz
spinbox.setSingleStep(1000)    # step of 1000 Hz
spinbox.setValue(sampling_rate)
spinbox.valueChanged.connect(lambda val: change_sampling_rate(val // 1000))

dock = QtWidgets.QDockWidget("Sampling rate (Hz)")
dock.setWidget(spinbox)

main_window = QtWidgets.QMainWindow()
main_window.setCentralWidget(window)
main_window.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)


stream = sd.InputStream(channels=1, samplerate=sampling_rate, blocksize=block_size,callback=audio_callback)
stream.start()
main_window.resize(1000, 800)
main_window.show()
change_sampling_rate(sampling_rate//1000)
sys.exit(app.exec_())

#add take screenshot feature
#add in my notes that you have to normalize amplitude dividing by windowlength if you want to compare it with other windowlenghts
