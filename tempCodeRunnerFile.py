
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