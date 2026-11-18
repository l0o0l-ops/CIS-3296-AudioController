"""Manual microphone check. Run from the project folder: python3 -m tests.test_transcriber"""
from vosk_stt.transcriber import Transcriber


if __name__ == "__main__":
    with Transcriber() as t:
        input("Press Enter to start...")
        t.start()
        input("Press Enter to stop...")
        result = t.stop()
        print(repr(result.text), result.stop_heard)
