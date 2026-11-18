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
# def move_foward(time: int):
#     print("Move")
#     return {"action": "move_foward", "status": "completed"}

# def move_backward(time: int):
#     print("Move")
#     return {"action": "move", "status": "completed"}

# def turn_left(time: int):
#     print("Turn")

# def turn_right(time: int):
#     print("Turn")

# def grab():
#     print("Grab the Object")

# def stop():
#     print("Stop")

'''
Description for each function tool so that when gemini trys to assign a function it knows the data type that it should return and the description for each function
'''

move_forward_tool = {
    "type": "function",
    "name": "move_forward",
    "description": "moves the lego model fowards in a straight line",
    "parameters": {
        "type": "object",
        "properties": {
            "time": {
                "type": "integer",
                "description": "The amount of time in seconds the LEGO model should move for in seconds. If no time is specified return 2 seconds"
            },
        },
        "required": ["time"],
    },
}

move_backward_tool = {
    "type": "function",
    "name": "move_backward",
    "description": "moves the lego model backwards in a straight line",
    "parameters": {
        "type": "object",
        "properties": {
            "time": {
                "type": "integer",
                "description": "The amount of time in seconds the LEGO model should move for in seconds. If no time is specified return 2 seconds"
            },
        },
        "required": ["time"],
    },
}



turn_left_tool = {
    "type": "function",
    "name": "turn_left",
    "description": "Rotate the LEGO model to the left. If the user asks to completly rotate the model, turn the model 180 degrees to the left so it is now in the opposite direction.",
    "parameters":
    {
        "type": "object",
        "properties": {
            "time": {
                "type": "integer",
                "description": "To turn left a time should be returned from 1 to 5 seconds. If no time is specified return 2 seconds"
            },
        },
        "required": ["time"]
    }
}


turn_right_tool = {
    "type": "function",
    "name": "turn_right",
    "description": "Rotate the LEGO model to the right",
    "parameters":
    {
        "type": "object",
        "properties": {
            "time": {
                "type": "integer",
                "description": "To turn right, a time should be returned from 1 to 5 seconds. If no time is specified return 2 seconds"
            },
        },
        "required": ["time"]
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
    "move_forward": command_library.CommandLibrary.move_forward,
    "move_backward": command_library.CommandLibrary.move_backward,
    "turn_left": command_library.CommandLibrary.turn_left,
    "turn_right": command_library.CommandLibrary.turn_right,
    "grab": command_library.CommandLibrary.grab
}

#start = time.perf_counter()

