# transcribe.py
import sys
from openai import OpenAI

client = OpenAI()

def transcribe(audio_file_path: str) -> str:
    """
    Sends an audio file to OpenAI's gpt-4o-transcribe model
    and returns the transcribed text.
    """
    with open(audio_file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            file=audio_file,
            model="gpt-4o-transcribe"
        )

    return response.text


if __name__ == "__main__":
    audio_file = sys.argv[1]
    text = transcribe(audio_file)
    print(text)
