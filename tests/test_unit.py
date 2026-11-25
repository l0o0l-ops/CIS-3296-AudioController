"""Simple unit tests, three per person. No robot, mic, internet or API key needed.

Run from the project folder with:  python -m unittest tests.test_unit -v
"""
import asyncio
import inspect
import json
import os
import unittest
from unittest import mock

os.environ.setdefault("GEMINI_API_KEY", "test-key-not-real")  # dummy, never used

import geminiCall
from command.command_library import CommandLibrary
from vosk_stt.transcriber import Transcriber


# ---------------------------------------------------------------- Keiji (Vosk)
class KeijiVoskTests(unittest.TestCase):
    def has_stop(self, text):
        return Transcriber._has_stop(json.dumps({"text": text}))

    def test_finds_stop_in_a_sentence(self):
        self.assertTrue(self.has_stop("please stop now"))

    def test_no_stop_in_a_normal_command(self):
        self.assertFalse(self.has_stop("move forward"))

    def test_word_containing_stop_does_not_count(self):
        self.assertFalse(self.has_stop("stopping"))


# --------------------------------------------------------- Seiji (robot code)
class FakeHub:
    """Fake Bluetooth client: saves what is written and says 'ready' again."""

    def __init__(self, ready):
        self.ready = ready
        self.writes = []

    async def write_gatt_char(self, uuid, data, response=True):
        self.writes.append(data)
        self.ready.set()


class SeijiRobotTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        ready = asyncio.Event()
        ready.set()
        self.hub = FakeHub(ready)
        self.robot = CommandLibrary(self.hub, ready, "uuid")

        async def no_wait(_seconds):  # skip real waiting
            pass

        patcher = mock.patch("command.command_library.asyncio.sleep", no_wait)
        patcher.start()
        self.addCleanup(patcher.stop)

    async def test_send_adds_the_write_prefix(self):
        await self.robot.send(b"mof")
        self.assertEqual(self.hub.writes, [b"\x06mof"])

    async def test_move_forward_starts_then_stops(self):
        await self.robot.move_forward(2)
        self.assertEqual(self.hub.writes, [b"\x06mof", b"\x06stp"])

    async def test_grab_sends_grb(self):
        await self.robot.grab()
        self.assertEqual(self.hub.writes, [b"\x06grb"])


# ------------------------------------------------------------ Danny (Gemini)
TOOLS = [geminiCall.move_forward_tool, geminiCall.move_backward_tool,
         geminiCall.turn_left_tool, geminiCall.turn_right_tool,
         geminiCall.grab_tool]


class DannyGeminiTests(unittest.TestCase):
    def test_every_tool_has_a_name_and_description(self):
        for tool in TOOLS:
            self.assertTrue(tool["name"])
            self.assertTrue(tool["description"])

    def test_every_tool_matches_a_robot_method(self):
        for tool in TOOLS:
            method = getattr(CommandLibrary, tool["name"], None)
            self.assertIsNotNone(method, tool["name"])
            self.assertTrue(inspect.iscoroutinefunction(method))

    def test_moving_and_turning_tools_need_an_integer_time(self):
        for tool in TOOLS:
            if tool["name"] == "grab":
                continue
            self.assertEqual(tool["parameters"]["properties"]["time"]["type"], "integer")
            self.assertIn("time", tool["parameters"]["required"])


if __name__ == "__main__":
    unittest.main()
