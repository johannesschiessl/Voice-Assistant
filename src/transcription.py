from groq import Groq

groq_client = Groq()

def transcribe_audio(file_path):
    try:
        with open(file_path, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="whisper-large-v3",
                response_format="text",
                language="en"
            )
        return transcription if isinstance(transcription, str) else transcription.get("text", "")
    except Exception as e:
        return ""
