import os
import tempfile
import wave
import pyaudio
import webrtcvad

RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 1024
FRAME_DURATION_MS = 20
FRAME_SIZE = int(RATE * FRAME_DURATION_MS / 1000)
VAD_MODE = 3

audio = pyaudio.PyAudio()
vad = webrtcvad.Vad(VAD_MODE)

try:
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=FRAME_SIZE)
    stream.start_stream()
except Exception as e:
    sys.exit(1)

def record_until_silence():
    frames = []
    silence_threshold = 20
    silent_chunks = 0

    while True:
        try:
            data = stream.read(FRAME_SIZE, exception_on_overflow=False)
        except Exception as e:
            break

        is_speech = vad.is_speech(data, RATE)

        if is_speech:
            frames.append(data)
            silent_chunks = 0
        else:
            silent_chunks += 1

        if silent_chunks > silence_threshold:
            break

    return frames

def save_audio(frames):
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        return temp_file.name
    except Exception as e:
        return None

def cleanup():
    try:
        stream.stop_stream()
        stream.close()
        audio.terminate()
    except Exception as e:
        pass
