# notes.py
from transcribe import transcribe

NOTES_FILE = "meeting_notes.txt"

def append_notes(audio_file):
    text = transcribe(audio_file)
    with open(NOTES_FILE, "a") as f:
        f.write(text + "\n")

if __name__ == "__main__":
    import sys
    append_notes(sys.argv[1])
