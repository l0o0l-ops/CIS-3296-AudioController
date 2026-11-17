"""Main pipeline: speech -> text (Vosk) -> function call (Gemini) -> robot.

Run it with either:  python main.py   or   acctl start

The robot step uses the placeholder functions in geminiCall.py, which only
print. command/command_library.py is not imported here: it uses Pybricks,
which runs on the LEGO hub, not on the laptop.
"""
import time

import typer

import geminiCall
from acctl.transcriber import Transcriber

MODEL = "gemini-3.5-flash-lite"
TOOLS = [geminiCall.move_tool, geminiCall.turn_tool]


def listen(t):
    """Record one phrase with Vosk and return the TranscriptResult."""
    input("\nPress Enter to start talking...")
    t.start()
    input("Press Enter to stop...")

    started = time.perf_counter()
    result = t.stop()
    print(f"Vosk took {time.perf_counter() - started:.2f} s")
    return result


def ask_gemini(text):
    """Send text to Gemini and return the function calls it chose."""
    started = time.perf_counter()
    try:
        interaction = geminiCall.client.interactions.create(
            model=MODEL,
            input=text,
            tools=TOOLS,
            timeout=20,
        )
        return [(step.name, step.arguments)
                for step in interaction.steps
                if step.type == "function_call"]
    except Exception as e:
        print("Gemini request failed:", type(e).__name__)
        print(e)
        return []
    finally:
        print(f"Gemini took {time.perf_counter() - started:.2f} s")


def run_calls(calls):
    """Run each function Gemini chose, if it is one we allow."""
    for name, arguments in calls:
        function = geminiCall.available_functions.get(name)
        if function is None:
            print(f"Ignored unknown function: {name}")
            continue
        print(f"Running {name}({arguments})")
        function(**arguments)


def main():
    with Transcriber() as t:
        print("Voice controller running. Ctrl+C to quit.")
        try:
            while True:
                result = listen(t)
                print(f'You said: "{result.text}"' if result.text
                      else "(nothing recognized)")

                if result.stop_heard:
                    # Stop skips Gemini so it reaches the robot right away.
                    # geminiCall.stop() is a placeholder for the robot's stop.
                    print("STOP detected")
                    geminiCall.stop()
                elif result.text:
                    calls = ask_gemini(result.text)
                    if calls:
                        run_calls(calls)
                    else:
                        print("Gemini didn't choose a function. No action taken.")

                if not typer.confirm("Keep recording?", default=True):
                    break
        except KeyboardInterrupt:
            pass
        print("\nVoice controller stopped.")


if __name__ == "__main__":
    main()

