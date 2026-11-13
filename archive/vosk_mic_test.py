import json
import queue
import sys

import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel

MODEL_PATH = "models/vosk-model-small-en-us-0.15"
SetLogLevel(-1)  # hide Vosk's startup logs

audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    """Called by sounddevice for every chunk of mic audio."""
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(bytes(indata))

model = Model(MODEL_PATH)
samplerate = int(sd.query_devices(kind="input")["default_samplerate"])
recognizer = KaldiRecognizer(model, samplerate)


print(f"Listening at {samplerate} Hz... (Ctrl+C to stop)")

with sd.RawInputStream(samplerate=samplerate, blocksize=8000,
                       dtype="int16", channels=1, callback=callback):
    try:
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                text = json.loads(recognizer.Result())["text"]
                if text:
                    print("You said:", text)
    except KeyboardInterrupt:
        print("\nStopped.")