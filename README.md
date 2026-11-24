# CIS-3296-AudioController
CIS-3296 software design project: a voice-controlled LEGO Mindstorms robot.

Speech -> text (Vosk) -> function call (Gemini) -> Bluetooth command -> robot.

## What you need
- The team's LEGO Mindstorms robot, with its hub already set up (drive motor on port B, steering on A, grabber on D)
- A computer with Bluetooth and a microphone (developed on macOS and Windows; the full pipeline has been run on macOS)
- Python 3 (the team used 3.14) and git
- A Gemini API key
- The Vosk speech model (download, see step 4)

## Set up instructions

### 1) Get the code
```
git clone https://github.com/l0o0l-ops/CIS-3296-AudioController
cd CIS-3296-AudioController
git checkout main_prototype
```

### 2) Create and activate a virtual environment
macOS / Linux:
```
python3 -m venv .venv
source .venv/bin/activate
```
Windows (PowerShell):
```
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Do this in every new terminal window before running the program. Your prompt should start with `(.venv)`.

### 3) Install the packages
```
python -m pip install -r requirements.txt
```
On Linux, also run `sudo apt install libportaudio2` (needed for the microphone).

### 4) Download the Vosk speech model
The model is not stored in GitHub. Download `vosk-model-small-en-us-0.15.zip` from https://alphacephei.com/vosk/models and unzip it into a folder named `models` in the project folder.

macOS / Linux:
```
mkdir -p models
unzip ~/Downloads/vosk-model-small-en-us-0.15.zip -d models
```
The result must be `models/vosk-model-small-en-us-0.15/` (it contains the folders `am`, `conf` and `graph`). The folder name must match exactly.

### 5) Set up the .env file
Create an API key in [Google AI Studio](https://aistudio.google.com/api-keys). In the project folder, create a file named `.env` that contains one line:
```
GEMINI_API_KEY=your_key_here
```
Write it without spaces around `=` and without quotes or braces. Never commit `.env` (it is already in `.gitignore`).

### 6) macOS permissions
The first run asks for Bluetooth and microphone access. Allow both for Terminal (or VS Code). If you denied it by mistake, change it in System Settings > Privacy & Security.

## Run instructions
1. Turn on the hub. Press its button and check that the Bluetooth light is on. Close any other app connected to the hub (for example a Pybricks website tab).
2. In the project folder, with the virtual environment active, run:
   ```
   python main.py
   ```
   Start-up takes 10-20 seconds.
3. When the screen shows "Start the program on the hub now with the button.", press the button on the hub.
4. When the screen shows "Voice controller running. Ctrl+C to quit.", press Enter, say a command, and press Enter again.
   Example: Enter -- "move forward for three seconds" -- Enter
5. The text is sent to Gemini, converted to a function call, sent to the hub, and executed. When the hub finishes, you are asked "Keep recording?  [Y/n]". Press `y` to continue or `n` to end.
6. On `n`, the program disconnects from the hub and prints "done."

Supported commands: move forward, move backward, turn left, turn right (all take a time in seconds, 2 seconds if you give none; turns are limited to 1-5 seconds) and grab. Saying "stop" stops the drive motor.

## Troubleshooting
- `zsh: command not found: python`: the virtual environment is not active. Run `source .venv/bin/activate`.
- `could not find hub with name: Temple`: the hub is off, asleep, low on battery, or still connected to another app. Turn the hub off and on, close other apps connected to it, and try again. It can take one or two tries.
- Model not found: check that the folder is `models/vosk-model-small-en-us-0.15`.
- Gemini errors: check `.env` and the internet connection.
- `The program was stopped (SystemExit)` from the hub: the program on the hub has ended (for example the hub button was pressed again). Start it again with the button.

## Current status
The full pipeline (voice -> Vosk -> Gemini -> Bluetooth -> hub) has been run on macOS. The Windows setup steps above are the team's original steps; the full pipeline has not been recorded on every operating system.

## Known limits
- "Stop" only works between commands. While the robot is moving, the program waits until the move is finished.
- A misheard word can still produce a movement command.
- Only the first action in a phrase with several actions is run.
- Turns use a time in seconds, not degrees. Distances in centimeters are not supported.
- "Place" (release an object) is not implemented.
- The hub has no timer that stops the motor if Bluetooth is lost.
- Gemini takes about 3 seconds (up to 5.5), so the 2-second response goal is not met.
- Windows only: importing the audio libraries (`sounddevice`) sets the Windows COM mode to single-threaded (STA), which conflicts with `bleak`, the Bluetooth library. `main.py` works around this by importing `vosk_stt` in a separate thread and by opening the microphone before connecting to the hub. This does not affect macOS.
