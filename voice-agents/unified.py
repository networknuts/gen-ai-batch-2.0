import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import time
import os
from openai import OpenAI

# -----------------------------
# CONFIG
# -----------------------------
SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 60  # seconds per chunk

NOTES_FILE = "meeting_notes.txt"
SYSTEM_PROMPT_FILE = "system_prompt.txt"

client = OpenAI()

# -----------------------------
# AUDIO RECORDING
# -----------------------------
def record_chunk(filename: str):
    print(f"🎙️ Recording {filename}...")
    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=np.int16
    )
    sd.wait()
    write(filename, SAMPLE_RATE, audio)
    print(f"✅ Saved {filename}")

# -----------------------------
# TRANSCRIPTION
# -----------------------------
def transcribe(audio_file: str) -> str:
    with open(audio_file, "rb") as f:
        response = client.audio.transcriptions.create(
            file=f,
            model="gpt-4o-transcribe"
        )
    return response.text.strip()

# -----------------------------
# NOTES HANDLING
# -----------------------------
def append_notes(text: str):
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    print("📝 Notes appended")

# -----------------------------
# SUMMARIZATION
# -----------------------------
def load_system_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def summarize_notes():
    if not os.path.exists(NOTES_FILE):
        print("❌ No notes found")
        return

    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        notes = f.read()

    system_prompt = load_system_prompt(SYSTEM_PROMPT_FILE)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Meeting Notes:\n{notes}"}
        ]
    )

    print("\n========== MEETING SUMMARY ==========\n")
    print(response.choices[0].message.content)

# -----------------------------
# MAIN LOOP
# -----------------------------
def run_meeting_recorder():
    chunk_index = 0

    try:
        while True:
            wav_file = f"chunk_{chunk_index}.wav"

            record_chunk(wav_file)

            text = transcribe(wav_file)
            if text:
                append_notes(text)

            chunk_index += 1

    except KeyboardInterrupt:
        print("\n🛑 Recording stopped by user")
        summarize_notes()

if __name__ == "__main__":
    run_meeting_recorder()
