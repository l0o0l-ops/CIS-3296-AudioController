import geminiCall
from command import command_library

#import gemini.py, commandlibrary.py, vosk.py

#start two nested while loop, one for whole program, another for vosk listening

#while for whole

#while for vosk -> output String

#gemini take String -> output function call chosen from command library.py

#Initializing the client
from google import genai
import json

#from dotenv import load_dotenv
#load_dotenv()


#Main pipeline: speech -> text (Vosk) -> command (Gemini) -> robot.

#Run from the project folder:  python main.py
import time 
from acctl.transcriber import Transcriber


def listen():
    """Record one phrase and return the recognized text."""
    with Transcriber() as t:
        input("Press Enter to start talking...")
        t.start()
        input("Press Enter to stop...")
        return t.stop().text

text = listen()
print(f'You said: "{text}"')
try:
    interaction = geminiCall.client.interactions.create(
        model = "gemini-3.5-flash-lite",
        input = result.text, 
        tools = [geminiCall.move_tool,
                 geminiCall.turn_tool],
        timeout=20,

    )

    for step in interaction.steps:
        if step.type == "function_call":
            function_to_call = geminiCall.available_functions[step.name]
            function_to_call(**step.arguments)
            print(step.name)
            print(step.arguments)

    


except Exception as e:
    print("Request failed:", type(e).__name__)
    print(e)

finally:
    end = geminiCall.time.perf_counter()
    print(f"Response time: {end - geminiCall.start:.2f} seconds")


 
