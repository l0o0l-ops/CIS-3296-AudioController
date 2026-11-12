"""Command-line entry point for the audio controller.

Usage:
    acctl start    keep listening for commands until you answer no or press Ctrl+C
    acctl test     record one command and print what was heard
"""
import typer

from transcriber import Transcriber

app = typer.Typer(help="AC: Audio Controller for the voice-controlled LEGO robot.")


def _show(result):
    print(f'You said: "{result.text}"' if result.text else "(nothing recognized)")
    if result.stop_heard:
        print("STOP detected")


@app.command()
def test():
    """Record one command and print what was heard."""
    with Transcriber() as t:
        input("Press Enter to start talking...")
        t.start()
        input("Press Enter to stop...")
        _show(t.stop())


@app.command()
def start():
    """Keep listening for commands until you answer no or press Ctrl+C."""
    with Transcriber() as t:
        print("Audio controller running. Ctrl+C to quit.")
        try:
            while True:
                input("\nPress Enter to start talking...")
                t.start()
                input("Press Enter to stop...")
                _show(t.stop())
                if not typer.confirm("Keep recording?", default=True):
                    break
        except KeyboardInterrupt:
            pass
        print("\nAudio controller stopped.")
