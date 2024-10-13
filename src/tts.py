import os
import tempfile
import pygame
from openai import OpenAI
from pathlib import Path
from datetime import datetime

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

pygame.mixer.init()

def text_to_speech(text, model="tts-1", voice="alloy"):
    try:
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        speech_file_path = Path(temp_dir) / f"speech_{timestamp}.mp3"

        response = openai_client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )

        response.stream_to_file(speech_file_path)

        pygame.mixer.music.load(str(speech_file_path))
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        pass
