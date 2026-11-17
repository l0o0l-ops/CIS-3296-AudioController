"""Command-line entry point for the audio controller.

Usage:
    acctl start    run the full pipeline in main.py (Vosk -> Gemini -> robot)
    acctl test     record one command and print what was heard (no Gemini)
"""
import typer

from acctl.transcriber import Transcriber

app = typer.Typer(help="AC: Audio Controller for the voice-controlled LEGO robot.")


def _show(result):
    print(f'You said: "{result.text}"' if result.text else "(nothing recognized)")
    if result.stop_heard:
        print("STOP detected")


@app.command()
def test():
    """Record one command and print what was heard (no Gemini)."""
    with Transcriber() as t:
        input("Press Enter to start talking...")
        t.start()
        input("Press Enter to stop...")
        _show(t.stop())


@app.command()
def start():
    """Run the full pipeline: Vosk, then Gemini, then the robot."""
    # Imported here, not at the top, because main.py loads the Gemini client,
    # which needs the API key. This keeps `acctl test` and `--help` key-free.
    from main import main
    main()
