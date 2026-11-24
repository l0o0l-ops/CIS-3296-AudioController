# CIS-3296-AudioController
CIS-3296 software design project

### Set Up Instructions:
1) Create a virtual enviorment
py -3.14 -m venv .venv

2) Activating the virtual enviorment
.\.venv\scripts\Activate.ps1

3) clone github repository
```
git clone https://github.com/l0o0l-ops/CIS-3296-AudioController
```

4) Install the foresaid parts
```
python -m pip install -r requirements.txt
```

5) Download Vosk model
    1) make "models" folder in cloned repository
    2) Download "vosk-model-small-en-us-0.15" from https://alphacephei.com/vosk/models
    3) extract downloaded zip file under the "model" folder made in 1

6) Hardware setup
    1) prepare [LEGO mindstorm Robot Inventor](https://www.lego.com/ja-jp/service/device-guide/mindstorms-robot-inventor)
    2) build the robot using the [build guide](https://www.lego.com/cdn/product-assets/product.bi.additional.main.pdf/51515_MVP.pdf)
    3) connect the hub to your PC, and install pybricks firmware from [pybricks website](https://code.pybricks.com/), set the name of hub to "Temple"
    4) drag and drop command/command_listener.py to the pybricks website, and run it on hub, it will write the pyfile into the Hub

7) Set up .env file
access to [Gemini api studio](https://aistudio.google.com/api-keys) and create api key for new project, and add "GEMINI_API_KEY = {YOUR_API_KEY}" to .env file

### Run instructions
1) turn on Hardware
press the button, and check if the bluetooth button glows blue

2) run main.py
it will take a while for the set up (10-20s), once CLI shows message "Start the program on the hub now with the button.", press the button on hub

3) input your voice
When CLI shows "Voice controller running. Ctrl+C to quit.", press Enter to start recording your voice, and press Enter again after talking
example: Enter -- "move forward" -- Enter

4) Observe
Once the input is received, the transcribed text will be sent to Gemini, will be converted to the sequence of command, sent to the hardware, and executed.
After Hardware finishes executing, you'll be asked "Keep recording?  [Y/n] ". If you want to continue, enter Y, and it will repeat the same procedure again, otherwise, enter n

5) Ending program
The program will disconnect with Hardware automatically, and prints "done." in the end of the program

### unfinished features
integration of Vosk + gemini pipeline and LEGO mindstorm
The pipline of voice -> command selection is complete, but we haven't tested the integration with LEGO mindstorm yet


### known issues
importing vosk_stt (or its dependencies like sounddevice / PyAudio) initializes the Windows COM threading model to STA (Single-Threaded Apartment), which conflicts with bleak because it expects an active Windows message loop or an MTA (Multi-Threaded Apartment) environment


### sections still to be completed.
main.py (integration). We need to repeat testing the whole system

