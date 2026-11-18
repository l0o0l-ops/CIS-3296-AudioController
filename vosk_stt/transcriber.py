"""Speech-to-text for the voice robot, using Vosk.

Use it from another file like this:

    from transcriber import Transcriber

    with Transcriber() as t:
        t.start()              # begin recording
        result = t.stop()      # stop and get what was said
        print(result.text, result.stop_heard)
"""
import json
import queue
import sys
from dataclasses import dataclass
from pathlib import Path

import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel

# Project root is one level above this file (vosk_stt/), so this works from any folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "vosk-model-small-en-us-0.15"
BLOCKSIZE = 4000  # samples per audio chunk (about 0.25 s at 16 kHz)


@dataclass
class TranscriptResult:
    text: str         # what the user said, e.g. "move forward a bit"
    stop_heard: bool  # True if the word "stop" was heard


class Transcriber:
    def __init__(self, model_path=DEFAULT_MODEL_PATH):
        SetLogLevel(-1)
        self._model = Model(str(model_path))
        self._samplerate = int(sd.query_devices(kind="input")["default_samplerate"])
        # Full vocabulary, so Gemini receives natural phrasing.
        self._recognizer = KaldiRecognizer(self._model, self._samplerate)
        # Only listens for "stop", so it can catch that word reliably.
        self._stop_recognizer = KaldiRecognizer(
            self._model, self._samplerate, json.dumps(["stop", "[unk]"]))
        self._queue = queue.Queue()
        self._recording = False
        self._stream = None

    def __enter__(self):
        """Open the microphone."""
        self._stream = sd.RawInputStream(
            samplerate=self._samplerate, blocksize=BLOCKSIZE,
            dtype="int16", channels=1, callback=self._callback)
        self._stream.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        """Close the microphone."""
        self._stream.stop()
        self._stream.close()

    def _callback(self, indata, frames, time, status):
        """Called by sounddevice for every chunk of mic audio."""
        if status:
            print(status, file=sys.stderr)
        if self._recording:
            self._queue.put(bytes(indata))

    def start(self):
        """Begin recording. Audio is kept until stop() is called."""
        self._drain()
        self._recording = True

    def stop(self):
        """Stop recording and return what was said."""
        self._recording = False
        parts = []
        stop_heard = False
        while not self._queue.empty():
            chunk = self._queue.get()
            if self._recognizer.AcceptWaveform(chunk):
                parts.append(json.loads(self._recognizer.Result())["text"])
            if self._stop_recognizer.AcceptWaveform(chunk):
                if self._has_stop(self._stop_recognizer.Result()):
                    stop_heard = True
        parts.append(json.loads(self._recognizer.FinalResult())["text"])
        if self._has_stop(self._stop_recognizer.FinalResult()):
            stop_heard = True
        text = " ".join(p for p in parts if p)
        return TranscriptResult(text=text, stop_heard=stop_heard)

    def _drain(self):
        """Throw away any audio left over from before."""
        while not self._queue.empty():
            self._queue.get()

    @staticmethod
    def _has_stop(result_json):
        return "stop" in json.loads(result_json)["text"].split()


if __name__ == "__main__":
    # Quick manual test: press Enter to start, Enter to stop, Ctrl+C to quit.
    with Transcriber() as t:
        try:
            while True:
                input("\nPress Enter to start talking...")
                t.start()
                print("Speaking... press Enter to stop.")
                input()
                result = t.stop()
                print("You said:", result.text or "(nothing recognized)")
                if result.stop_heard:
                    print("STOP detected")
        except KeyboardInterrupt:
            print("\nStopped.")
