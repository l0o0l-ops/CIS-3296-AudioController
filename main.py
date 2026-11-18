import geminiCall
from command import command_library
import time
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


start = time.perf_counter()

fc_step = None
result = None

#This is the first call to Gemini Using the Voice-to-Text transcription
try:
    interaction = geminiCall.client.interactions.create(
        model = "gemini-3.5-flash-lite",
        input = "Move forward, then turn left",
        tools = [geminiCall.move_foward_tool,
                 #geminiCall.move_backward_tool,
                geminiCall.turn_left_tool,
                #geminiCall.turn_right_tool,
                #geminiCall.grab_tool
                ],
        timeout=20,
    )

    #Looping through the gemini steps as we receive them
    for step in interaction.steps:
        #Looks for any steps that is the function call and if it is, then it will attempt to call the function and save it
        if step.type == "function_call":
            fc_step = step
            function_to_call = geminiCall.available_functions[step.name]
            result = function_to_call(**step.arguments)
            break

    

#If there is an error in the call to gemini we catch it and say what the problem was
except Exception as e:
    print("Request failed:", type(e).__name__)
    print(e)

#For performance reasons we want to see how long a geminiAPI call takes from beginning to end
finally:
    end = time.perf_counter()
    print(f"Response time: {end - start:.2f} seconds")


#The continued function calls to geminiAPI that will call the next function if possible from the previous function call
if fc_step is not None:
    final_interaction = geminiCall.client.interactions.create(
        model = "gemini-3.5-flash-lite",
        input = [
            {
                "type": "function_result",
                "name": fc_step.name,
                "call_id": fc_step.id,
                "result": [{"type": "text", "text": json.dumps(result)}]
            }
        ],
        tools = [geminiCall.move_foward_tool,
                 #geminiCall.move_backward_tool,
                geminiCall.turn_left_tool,
                #geminiCall.turn_right_tool,
                #geminiCall.grab_tool
                ],
        #Used to store the previous function calls so that the next function calls are called in the correct sequeunce
        previous_interaction_id = interaction.id,
        timeout=20,
    )

    print(final_interaction.output_text)
    for step in final_interaction.steps:
        if step.type == "function_call":
            function_to_call = geminiCall.available_functions[step.name]
            next_result = function_to_call(**step.arguments)



 
