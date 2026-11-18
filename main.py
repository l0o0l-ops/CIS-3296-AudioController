"""Main pipeline: speech -> text (Vosk) -> function call (Gemini) -> robot.

Run from the project folder:  python main.py

The robot step uses the placeholder functions in geminiCall.py, which only
print. command/command_library.py is not imported here: it uses Pybricks,
which runs on the LEGO hub, not on the laptop.
"""
import time

import geminiCall
from vosk_stt.transcriber import Transcriber
import asyncio
from contextlib import suppress
from bleak import BleakScanner, BleakClient
from command import command_library

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"

# Replace this with the name of your hub if you changed
# it when installing the Pybricks firmware.
HUB_NAME = "Temple"

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


async def main():

    main_task = asyncio.current_task()

    def handle_disconnect(_):
        print("Hub was disconnected.")

        # If the hub disconnects before this program is done,
        # cancel this program so it doesn't get stuck waiting
        # forever.
        if not main_task.done():
            main_task.cancel()

    ready_event = asyncio.Event()

    def handle_rx(_, data: bytearray):
        if data[0] == 0x01:  # "write stdout" event (0x01)
            payload = data[1:]

            if payload == b"rdy":
                ready_event.set()
            else:
                print("Received:", payload)

    # Do a Bluetooth scan to find the hub.
    device = await BleakScanner.find_device_by_name(HUB_NAME)

    if device is None:
        print(f"could not find hub with name: {HUB_NAME}")
        return

    # Connect to the hub.
    async with BleakClient(device, handle_disconnect) as client:

        # Subscribe to notifications from the hub.
        
        commands = command_library.CommandLibrary(client, ready_event, PYBRICKS_COMMAND_EVENT_CHAR_UUID)
        await client.start_notify(PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx)
        


        # Tell user to start program on the hub.
        print("Start the program on the hub now with the button.")

        # Send a few messages to the hub. Replace with vosk-gemini pipeline
        # with Transcriber() as t:
        #         print("Voice controller running. Ctrl+C to quit.")
        #         try:
        #             while True:
        #                 result = listen(t)
        #                 print(f'You said: "{result.text}"' if result.text
        #                       else "(nothing recognized)")
        
        #                 if result.stop_heard:
        #                     # Stop skips Gemini so it reaches the robot right away.
        #                     # geminiCall.stop() is a placeholder for the robot's stop.
        #                     print("STOP detected")
        #                     geminiCall.stop()
        #                 elif result.text:
        #                     calls = ask_gemini(result.text)
        #                     if calls:
        #                         run_calls(calls)
        #                     else:
        #                         print("Gemini didn't choose a function. No action taken.")
        
        #                 if input("Keep recording? [Y/n] ").strip().lower() == "n":
        #                     break
        #         except KeyboardInterrupt:
        #             pass
        #         print("\nVoice controller stopped.")

        # Send a message to indicate stop.
        await commands.bye()

        print("done.")
    


if __name__ == "__main__":
    with suppress(asyncio.CancelledError):
        asyncio.run(main())

