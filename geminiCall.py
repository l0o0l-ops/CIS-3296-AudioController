#Initializing the client
from google import genai



#Used to test the time for the model since it was incredibly slow in the beginning
import time
client = genai.Client()



#Robot Functions
#Below here will be the list of functions that model will be able to do
#For now these are just placeholders for testing time delays in gemini and to see if it actually works or not
def move_foward():
    print("Move Foward")

def move_backward():
    print("Move Backwards")

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


start = time.perf_counter()



#This part here initalizes the AI model and defines the type of response we should be receiving from gemini
#Also the reason for the time stuff here is so if it takes to long it will stop trying to execute the command
try:
    interaction = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input="The user said: 'Move forward'. Identify the requested robot action in one word.",
        timeout=20
    )


except Exception as e:
    print("Request failed:", type(e).__name__)
    print(e)

finally:
    end = time.perf_counter()
    print(f"Response time: {end - start:.2f} seconds")
print(interaction.output_text)