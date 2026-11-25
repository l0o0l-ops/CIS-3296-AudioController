"""Integration test: speech -> Transcriber -> Gemini -> CommandLibrary -> hub bytes.

All three real components are used together (Transcriber, the Gemini tool names,
CommandLibrary). Only the outside world is faked: the microphone and Vosk
model, the Gemini API, and the Bluetooth hub. No hardware, internet or key needed.

run_pipeline() below follows the logic of main.py's loop (stop skips Gemini,
text goes to Gemini, function calls are looked up in a fixed whitelist).
Run from the project folder with:  python -m unittest discover -s tests -t . -v
"""
import asyncio
import json
import os
import unittest
from types import SimpleNamespace
from unittest import mock

os.environ.setdefault("GEMINI_API_KEY", "test-key-not-real")

from command.command_library import CommandLibrary
from vosk_stt import transcriber
from vosk_stt.transcriber import Transcriber


class FakeRecognizer:
    """Replays one scripted (accepted, text) pair per audio chunk."""

    def __init__(self, script=(), final_text=""):
        self.script = list(script)
        self.final_text = final_text
        self.last = json.dumps({"text": ""})

    def AcceptWaveform(self, chunk):
        accepted, text = self.script.pop(0)
        self.last = json.dumps({"text": text})
        return accepted

    def Result(self):
        return self.last

    def FinalResult(self):
        return json.dumps({"text": self.final_text})


def make_transcriber(main, stop):
    """Build a Transcriber with fake recognizers and no microphone."""
    with mock.patch.object(transcriber, "Model"), \
         mock.patch.object(transcriber, "SetLogLevel"), \
         mock.patch.object(transcriber.sd, "query_devices",
                           return_value={"default_samplerate": 16000}), \
         mock.patch.object(transcriber, "KaldiRecognizer", side_effect=[main, stop]):
        return Transcriber()


def feed(t, count):
    """Queue fake audio chunks as if the mic had captured them."""
    for i in range(count):
        t._queue.put(b"chunk%d" % i)


class FakeHubClient:
    """Stands in for the BLE client and answers "rdy" after every write."""

    def __init__(self, ready_event):
        self.ready_event = ready_event
        self.writes = []

    async def write_gatt_char(self, uuid, data, response=True):
        self.writes.append(data)
        self.ready_event.set()


class FakeGemini:
    """Returns scripted interactions: a function call, then a plain answer."""

    def __init__(self, *calls):
        self.calls = list(calls)
        self.requests = []

    def create(self, **kwargs):
        self.requests.append(kwargs)
        name, arguments = self.calls.pop(0) if self.calls else (None, None)
        steps = []
        if name:
            steps.append(SimpleNamespace(type="function_call", name=name,
                                         arguments=arguments, id="call-1"))
        return SimpleNamespace(id="int-%d" % len(self.requests),
                               steps=steps, output_text="ok")


def speak(text, stop_text=""):
    """A Transcriber that 'hears' the given phrase, with no mic or model."""
    t = make_transcriber(
        main=FakeRecognizer([(True, text)] if text else [(False, "")]),
        stop=FakeRecognizer([(True, stop_text)] if stop_text else [(False, "")]))
    t._recording = True
    feed(t, 1)
    return t


async def run_pipeline(transcriber, gemini, commands):
    """One round of main.py's loop: listen result -> stop or Gemini -> robot."""
    available = {
        "move_forward": commands.move_forward,
        "move_backward": commands.move_backward,
        "turn_left": commands.turn_left,
        "turn_right": commands.turn_right,
        "grab": commands.grab,
    }
    result = transcriber.stop()
    if result.stop_heard:
        await commands.send(b"mos")          # stop skips Gemini
        return result
    if not result.text:
        return result
    user_input, previous_id = result.text, None
    while True:
        interaction = await asyncio.to_thread(
            gemini.create, input=user_input, previous_interaction_id=previous_id)
        previous_id = interaction.id
        call = next((s for s in interaction.steps if s.type == "function_call"), None)
        if call is None or call.name not in available:
            return result
        outcome = await available[call.name](**(call.arguments or {}))
        user_input = [{"type": "function_result", "name": call.name,
                       "call_id": call.id, "result": str(outcome)}]


class PipelineIntegrationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ready = asyncio.Event()
        self.ready.set()
        self.hub = FakeHubClient(self.ready)
        self.commands = CommandLibrary(self.hub, self.ready, "uuid")

        async def no_wait(_seconds):
            pass

        patcher = mock.patch("command.command_library.asyncio.sleep", no_wait)
        patcher.start()
        self.addCleanup(patcher.stop)

    def hub_commands(self):
        return [w[1:] for w in self.hub.writes]  # drop the 0x06 prefix

    async def test_speech_to_forward_movement(self):
        gemini = FakeGemini(("move_forward", {"time": 3}))
        await run_pipeline(speak("move forward for three seconds"), gemini, self.commands)
        self.assertEqual(self.hub_commands(), [b"mof", b"stp"])
        self.assertEqual(gemini.requests[0]["input"], "move forward for three seconds")
        # The robot's result goes back to Gemini as a function_result.
        self.assertEqual(gemini.requests[1]["input"][0]["type"], "function_result")

    async def test_speech_to_left_turn(self):
        gemini = FakeGemini(("turn_left", {"time": 2}))
        await run_pipeline(speak("turn left"), gemini, self.commands)
        self.assertEqual(self.hub_commands(), [b"tul", b"mof", b"mos", b"res"])

    async def test_speech_to_grab_with_no_arguments(self):
        gemini = FakeGemini(("grab", None))
        await run_pipeline(speak("pick that up"), gemini, self.commands)
        self.assertEqual(self.hub_commands(), [b"grb"])

    async def test_stop_skips_gemini_and_stops_the_robot(self):
        gemini = FakeGemini(("move_forward", {"time": 3}))
        await run_pipeline(speak("stop", stop_text="stop"), gemini, self.commands)
        self.assertEqual(gemini.requests, [])          # Gemini never called
        self.assertEqual(self.hub_commands(), [b"mos"])

    async def test_unclear_request_sends_nothing_to_the_robot(self):
        gemini = FakeGemini((None, None))              # Gemini returns no function call
        await run_pipeline(speak("what is the weather"), gemini, self.commands)
        self.assertEqual(self.hub_commands(), [])

    async def test_unknown_function_from_gemini_is_ignored(self):
        gemini = FakeGemini(("self_destruct", {}))
        await run_pipeline(speak("do something odd"), gemini, self.commands)
        self.assertEqual(self.hub_commands(), [])

    async def test_silence_sends_nothing_anywhere(self):
        gemini = FakeGemini(("move_forward", {"time": 3}))
        await run_pipeline(speak(""), gemini, self.commands)
        self.assertEqual(gemini.requests, [])
        self.assertEqual(self.hub_commands(), [])


if __name__ == "__main__":
    unittest.main()
