#Initializing the client
from google import genai
import json

#from dotenv import load_dotenv
#load_dotenv()



#Used to test the time for the model since it was incredibly slow in the beginning
import time
client = genai.Client()



#Robot Functions
#Below here will be the list of functions that model will be able to do
#For now these are just placeholders for testing time delays in gemini and to see if it actually works or not
def move_foward(distance: int):
    print("Move foward", distance, "cm")

def move_backward(distance: int):
    print("Move Backwards", distance, "cm")

def turn_left():
    print("Turn Left")

def turn_right():
    print("Turn Right")

def grab():
    print("Grab the Object")

def release():
    print("Release the object")

def stop():
    print("Stop")

'''
Description for each function tool so that when gemini trys to assign a function it knows the data type that it should return and the description for each function
'''
move_foward_tool = {
    "type": "function",
    "name": "move_foward",
    "description": "moves the lego model foward in a straight line",
    "parameters": {
        "type": "object",
        "properties": {
            "distance": {
                "type": "integer",
                "description": "Distance to move in centimeters"
            },
        },
        "required": ["distance"]
    },
}

move_backward_tool = {
    "type": "function",
    "name": "move_backward",
    "description": "move the lego set backwards in a straight line",
    "parameters": 
    {
        "type": "object",
        "properties": {
            "distance": 
            {
                "type": "integer",
                "description": "Distance to move in centimeters"
            },
        },
        "required": ["distance"]
    }
}

turn_left_tool = {
    "type": "function",
    "name": "turn_left",
    "description": "Rotate the LEGO model to the left by a specied amount of degrees. If asked to turn the model 180 degrees, assume to turn the model left 180 degrees unless specified otherwise",
    "parameters":
    {
        "type": "object",
        "properties": {
            "degree": {
                "description": "The amount of degrees to rotate in the left direction"
            },
        },
        "required": ["degree"]
    }
}

turn_right_tool = {
    "type": "function",
    "name": "turn_right",
    "description": "Rotate the lego model to the right a specified amount of degress dependent on the users reponse",
    "parameters":
    {
        "type": "object",
        "properties": {
            "degree": {
                "description": "The amount of degrees to rotate the lego model in the right direction"
            },
        },
        "required": ["degree"]
    }
}

available_functions = {
    "move_foward": move_foward,
    "move_backward": move_backward,
    "turn_left": turn_left,
    "turn_right": turn_right,
}


start = time.perf_counter()



#This part here initalizes the AI model and defines the type of response we should be receiving from gemini
#Also the reason for the time stuff here is so if it takes to long it will stop trying to execute the command


try:
    interaction = client.interactions.create(
        model = "gemini-3.5-flash-lite",
        input = "move foward 20 centimeters",
        tools = [move_foward_tool,
                 move_backward_tool,
                 turn_left_tool,
                 turn_right_tool],
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
print(interaction.output_text)