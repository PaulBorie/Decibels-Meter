import os, errno
import pyaudio
import numpy
from scipy.signal import lfilter
import lib.spl_lib as spl

FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 44100
CHUNK = 88200 
NUMERATOR, DENOMINATOR = spl.A_weighting(RATE)

def getPyAudio():
    return pyaudio.PyAudio()

def getDdefaultInputDevice(pa):
    for i in range(pa.get_device_count()):
        if "default" == pa.get_device_info_by_index(i).get('name'):
            return i

def getStream(pa):
    return pa.open(format = FORMAT,
        channels = CHANNEL,
        rate = RATE,
        input = True,
        frames_per_buffer = CHUNK,
        input_device_index=getDdefaultInputDevice(pa))

def record(stream, time, error_count=0):
    print("Recording...")
    sum = 0
    count = 0
    block = 0
    for i in range(0, int(RATE / CHUNK * time)):
        try:
            block = stream.read(CHUNK)
        except IOError as e:
            error_count += 1
            print(" (%d) Error recording: %s" % (error_count, e))
        else:
            decoded_block = numpy.frombuffer(block, dtype=numpy.int16)
            y = lfilter(NUMERATOR, DENOMINATOR, decoded_block)
            new_decibel = 20*numpy.log10(spl.rms_flat(y))
            sum += new_decibel
            count += 1
    return (sum/count)

def close_stream(pa, stream):
    stream.stop_stream()
    stream.close()
    pa.terminate()