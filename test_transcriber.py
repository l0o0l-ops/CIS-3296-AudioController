"""Manual microphone check. Run it directly: python3 test_transcriber.py"""
from transcriber import Transcriber


if __name__ == "__main__":
    with Transcriber() as t:
        input("Press Enter to start...")
        t.start()
        input("Press Enter to stop...")
        result = t.stop()
        print(repr(result.text), result.stop_heard)
