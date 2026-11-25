"""Main pipeline: speech -> text (Vosk) -> function calls (Gemini) -> robot.

Run from the project folder: python main.py

Vosk handles speech recognition on the laptop.
Gemini selects the LEGO commands.
command_library.py sends commands to the LEGO hub over Bluetooth.
"""

import sys

sys.coinit_flags = 0


import time
from contextlib import suppress
import asyncio

import geminiCall
from bleak import BleakClient, BleakScanner
from command import command_library




  

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"

# Replace this with the name of your hub if you changed
# it when installing the Pybricks firmware.
HUB_NAME = "Temple"

MODEL = "gemini-3.5-flash-lite"
TOOLS = [geminiCall.move_forward_tool,
        geminiCall.move_backward_tool,
        geminiCall.turn_left_tool,
        geminiCall.turn_right_tool,
        geminiCall.grab_tool]




def listen(t):
    """Record one phrase with Vosk and return the TranscriptResult."""
    input("\nPress Enter to start talking...")
    t.start()
    input("Press Enter to stop...")

    started = time.perf_counter()
    result = t.stop()
    print(f"Vosk took {time.perf_counter() - started:.2f} s")
    return result

def _load_transcriber():
    from vosk_stt.transcriber import Transcriber
    return Transcriber


async def main():

    Transcriber = await asyncio.to_thread(_load_transcriber) #use different thread to avoid compatibility
    print("model import")

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


    # Connect to the hub.
    with Transcriber() as t:
        try:
            print("Voice controller running. Ctrl+C to quit.")
                # Do a Bluetooth scan to find the hub.
            device = await BleakScanner.find_device_by_name(HUB_NAME)

            if device is None:
                print(f"could not find hub with name: {HUB_NAME}")
                return
            else:
                print(f"{HUB_NAME} found!")
            async with BleakClient(device, handle_disconnect) as client:

                # Subscribe to notifications from the hub.    
                commands = command_library.CommandLibrary(client, ready_event, PYBRICKS_COMMAND_EVENT_CHAR_UUID)
                await client.start_notify(PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx)
                available_functions = {
                        "move_forward": commands.move_forward,
                        "move_backward": commands.move_backward,
                        "turn_left": commands.turn_left,
                        "turn_right": commands.turn_right,
                        "grab": commands.grab
                        }

                async def ask_gemini(text):


                    started = time.perf_counter()
                    user_input = text
                    previous_id = None
                    
                    try:
                        while True:

                            if previous_id is None:
                                interaction = await asyncio.to_thread(
                                    geminiCall.client.interactions.create,
                                    model=MODEL,
                                    input=user_input,
                                    tools=TOOLS,
                                    timeout=20,
                                )
                            else:
                                interaction = await asyncio.to_thread(
                                    geminiCall.client.interactions.create,
                                    model=MODEL,
                                    input=user_input,
                                    tools=TOOLS,
                                    timeout=20,
                                    previous_interaction_id=previous_id,
                                )
                            
                            previous_id = interaction.id

                            function_call = None

                            for step in interaction.steps:
                                if step.type == "function_call":
                                    function_call = step
                                    break

                            if function_call is None:
                                print("Gemini:", interaction.output_text)
                                break
                            
                            function = available_functions.get(function_call.name)


                            if function is None:
                                print(f"Unknown function: {function_call.name}")
                                break
                            print(f"Running {function_call.name}({function_call.arguments})")

                            #result = await function(**function_call.arguments)
                            result = await function(**(function_call.arguments or {}))

                            print(f"Function result: {result}")

                            # Send the result back to Gemini.
                            user_input = [
                                {
                                    "type": "function_result",
                                    "name": function_call.name,
                                    "call_id": function_call.id,
                                    "result": str(result)
                                }
                            ]
                    except Exception as e:
                        print("Gemini request failed:", type(e).__name__)
                        print(e)
                        return []
                    finally:
                        print(f"Gemini took {time.perf_counter() - started:.2f} s")


                    
                    # Tell user to start program on the hub.
                print("Start the program on the hub now with the button.")
                await asyncio.sleep(5)
                

            # Send a few messages to the hub. Replace with vosk-gemini pipeline
        
        
            
                while True:
                    result = await asyncio.to_thread(listen,t)
                    print(f'You said: "{result.text}"' if result.text
                            else "(nothing recognized)")

                    if result.stop_heard:
                        # Stop skips Gemini so it reaches the robot right away.
                        # geminiCall.stop() is a placeholder for the robot's stop.
                        print("STOP detected")
                        geminiCall.stop()
                    elif result.text:
                        await ask_gemini(result.text)

                    answer = await asyncio.to_thread(input, "Keep recording?  [Y/n] ")
                    if answer.strip().lower() == "n":
                        await commands.bye()
                        break
        except KeyboardInterrupt:
            pass
        print("\nVoice controller stopped.")

        # Send a message to indicate stop.
        

        print("done.")
    


if __name__ == "__main__":
    with suppress(asyncio.CancelledError):
        asyncio.run(main())

