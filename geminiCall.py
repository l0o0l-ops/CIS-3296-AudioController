#Initializing the client
from google import genai
import json
from command import command_library

from dotenv import load_dotenv
load_dotenv()



#Used to test the time for the model since it was incredibly slow in the beginning
import time
client = genai.Client()



#Robot Functions
#Below here will be the list of functions that model will be able to do
#For now these are just placeholders for testing time delays in gemini and to see if it actually works or not
# def move(time: int, speed: int):
#     print("Move")

# def turn(degree: int):
#     print("Turn")

# def grab():
#     print("Grab the Object")

# def stop():
#     print("Stop")

'''
Description for each function tool so that when gemini trys to assign a function it knows the data type that it should return and the description for each function
'''

move_tool = {
    "type": "function",
    "name": "move",
    "description": "moves the lego model foward or backwards in a straight line",
    "parameters": {
        "type": "object",
        "properties": {
            "time": {
                "type": "integer",
                "description": "The amount of time in seconds the LEGO model should move for"
            },
            "speed": {
                "type": "integer",
                "description": "The speed that the lego model should move with a foward motion being a positive value and a backwards motion being in the negative direction. The speed of the lego set should be assigned within the range of 1000 to 3000 with a smaller number being a slower speed"
            }
        },
        "required": ["time", "speed"],
    },
}



turn_tool = {
    "type": "function",
    "name": "turn",
    "description": "Rotate the LEGO model to the left or right depending on the specified direction of the user. If the user asks to completly rotate the model, turn the model 180 degrees to the left so it is now in the opposite direction.",
    "parameters":
    {
        "type": "object",
        "properties": {
            "degree": {
                "description": "To turn left, a positive degree from 1 to 359 should be given and to turn right, a negative degree from -1 to -359 should be returned"
            },
        },
        "required": ["degree"]
    }
}



grab_tool = {
    "type": "function",
    "name": "grab",
    "description": "The Lego model will move foward and bring its attached hook downwards to grab an object",
    "parameters":
    {
        "type": "object",
    }
}

available_functions = {
    "move": command_library.move,
    "turn": command_library.turn,
}


start = time.perf_counter()



#This part here initalizes the AI model and defines the type of response we should be receiving from gemini
#Also the reason for the time stuff here is so if it takes to long it will stop trying to execute the command

'''
try:
    interaction = client.interactions.create(
        model = "gemini-3.5-flash-lite",
        input = "move foward 20 centimeters",
        tools = [move_tool,
                 turn_tool],
        timeout=20,

    )

    for step in interaction.steps:
        if step.type == "function_call":
            function_to_call = available_functions[step.name]
            function_to_call(**step.arguments)
            print(step.name)
            print(step.arguments)

    


except Exception as e:
    print("Request failed:", type(e).__name__)
    print(e)

finally:
    end = time.perf_counter()
    print(f"Response time: {end - start:.2f} seconds")

'''
