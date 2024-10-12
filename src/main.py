import os
import tempfile
import time
import wave
import pyaudio
import webrtcvad
from groq import Groq
from pathlib import Path
from openai import OpenAI
import pygame
import logging
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

groq_client = Groq()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logging.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    sys.exit(1)

openai_client = OpenAI(api_key=openai_api_key)

RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 1024
FRAME_DURATION_MS = 20
FRAME_SIZE = int(RATE * FRAME_DURATION_MS / 1000)
VAD_MODE = 3

audio = pyaudio.PyAudio()
vad = webrtcvad.Vad(VAD_MODE)
pygame.mixer.init()

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

system_message = f"""You are a helpful voice assistant. The user is talking to you via voice and can hear your responses, so keep them concise and short. You can't do any human things, other than talking. Max 3 sentences.
# Context
- Date: {get_current_date()}"""

conversation_history = [
    {"role": "system", "content": system_message}
]

try:
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=FRAME_SIZE)
    stream.start_stream()
    logging.info("Audio stream started.")
except Exception as e:
    logging.error(f"Failed to open audio stream: {e}")
    sys.exit(1)

def record_until_silence():
    frames = []
    silence_threshold = 20
    silent_chunks = 0

    logging.info("Recording started. Speak into the microphone.")
    while True:
        try:
            data = stream.read(FRAME_SIZE, exception_on_overflow=False)
        except Exception as e:
            logging.error(f"Error reading audio stream: {e}")
            break

        is_speech = vad.is_speech(data, RATE)

        if is_speech:
            frames.append(data)
            silent_chunks = 0
        else:
            silent_chunks += 1

        if silent_chunks > silence_threshold:
            logging.info("Silence detected. Stopping recording.")
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
        logging.info(f"Audio recorded and saved to temporary file: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        logging.error(f"Failed to save audio: {e}")
        return None

def transcribe_audio(file_path):
    try:
        with open(file_path, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="whisper-large-v3",
                response_format="text",
                language="en"
            )
        logging.info(f"Transcription successful: {transcription}")
        return transcription if isinstance(transcription, str) else transcription.get("text", "")
    except Exception as e:
        logging.error(f"Failed to transcribe audio: {e}")
        return ""

def generate_response(question):
    try:
        conversation_history.append({"role": "user", "content": question})
        response = groq_client.chat.completions.create(
            messages=conversation_history,
            model="llama-3.2-3b-preview",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stream=False
        )
        generated_text = response.choices[0].message.content
        logging.info(f"Generated response: {generated_text}")
        conversation_history.append({"role": "assistant", "content": generated_text})
        return generated_text
    except Exception as e:
        logging.error(f"Failed to generate response: {e}")
        return ""

def text_to_speech(text, model="tts-1", voice="alloy"):
    try:
        logging.info("Requesting speech synthesis from OpenAI.")
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        speech_file_path = Path(temp_dir) / f"speech_{timestamp}.mp3"

        response = openai_client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )

        response.stream_to_file(speech_file_path)
        logging.info(f"Audio response saved to {speech_file_path}")

        pygame.mixer.music.load(str(speech_file_path))
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        logging.info("Audio playback completed.")

    except Exception as e:
        logging.error(f"Error in text_to_speech: {e}")

def main():
    logging.info("Application started. Press Ctrl+C to stop.")
    try:
        while True:
            frames = record_until_silence()
            if frames:
                audio_path = save_audio(frames)
                if not audio_path:
                    continue

                transcription = transcribe_audio(audio_path)
                if not transcription:
                    os.remove(audio_path)
                    continue

                response = generate_response(transcription)
                if not response:
                    os.remove(audio_path)
                    continue

                text_to_speech(response)

                try:
                    os.remove(audio_path)
                except Exception as e:
                    logging.error(f"Failed to delete temporary audio file {audio_path}: {e}")

            time.sleep(0.1)

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt detected. Stopping transcription...")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        try:
            stream.stop_stream()
            stream.close()
            audio.terminate()
            pygame.mixer.quit()
            logging.info("Audio stream closed.")
        except Exception as e:
            logging.error(f"Error closing audio stream: {e}")

if __name__ == "__main__":
    main()
