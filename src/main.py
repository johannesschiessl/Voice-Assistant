import time
import os
from audio_handler import record_until_silence, save_audio, cleanup
from transcription import transcribe_audio
from conversation import generate_response
from tts import text_to_speech

def main():
    print("Application started. Press Ctrl+C to stop.")
    print("Start speaking into the microphone...")
    try:
        while True:
            frames = record_until_silence()
            if frames:
                audio_path = save_audio(frames)
                if not audio_path:
                    continue

                transcription = transcribe_audio(audio_path)
                print(f"User: {transcription}")
                if not transcription:
                    os.remove(audio_path)
                    continue

                response = generate_response(transcription)
                if not response:
                    os.remove(audio_path)
                    continue

                print(f"Assistant: {response}")
                text_to_speech(response)
                
                try:
                    os.remove(audio_path)
                except Exception as e:
                    pass

            time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        pass
    finally:
        print("Application stopped.")
        cleanup()

if __name__ == "__main__":
    main()
