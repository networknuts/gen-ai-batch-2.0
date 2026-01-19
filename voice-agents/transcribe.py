# transcribe.py
import whisper
import sys

model = whisper.load_model("base")

def transcribe(file):
    result = model.transcribe(file)
    return result["text"]

if __name__ == "__main__":
    audio_file = sys.argv[1]
    text = transcribe(audio_file)
    print(text)
