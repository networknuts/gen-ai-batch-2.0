import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import time

SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 60  # seconds per chunk

def record_chunk(filename):
    print("🎙️ Recording...")
    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=np.int16
    )
    sd.wait()
    write(filename, SAMPLE_RATE, audio)
    print("✅ Saved:", filename)

if __name__ == "__main__":
    i = 0
    while True:
        record_chunk(f"chunk_{i}.wav")
        i += 1
