"""Automated tests for Transcriber's text and stop-word logic.

No microphone or model file is needed: Vosk is replaced with scripted fakes.
Run from the project folder with:  python -m unittest test_stop_logic -v
"""
import json
import unittest
from unittest import mock

import transcriber
from transcriber import Transcriber


def result_json(text):
    return json.dumps({"text": text})


class FakeRecognizer:
    """Replays one scripted (accepted, text) pair per audio chunk."""

    def __init__(self, script=(), final_text=""):
        self.script = list(script)
        self.final_text = final_text
        self.last = result_json("")

    def AcceptWaveform(self, chunk):
        accepted, text = self.script.pop(0)
        self.last = result_json(text)
        return accepted

    def Result(self):
        return self.last

    def FinalResult(self):
        return result_json(self.final_text)


def make_transcriber(main=None, stop=None):
    """Build a Transcriber with fake recognizers and no microphone."""
    recognizers = [main or FakeRecognizer(), stop or FakeRecognizer()]
    with mock.patch.object(transcriber, "Model"), \
         mock.patch.object(transcriber, "SetLogLevel"), \
         mock.patch.object(transcriber.sd, "query_devices",
                           return_value={"default_samplerate": 16000}), \
         mock.patch.object(transcriber, "KaldiRecognizer", side_effect=recognizers):
        return Transcriber()


def feed(t, count):
    """Queue `count` fake audio chunks as if the mic had captured them."""
    for i in range(count):
        t._queue.put(b"chunk%d" % i)


class StopWordDetectionTests(unittest.TestCase):
    def test_detects_stop_as_a_word(self):
        self.assertTrue(Transcriber._has_stop(result_json("stop")))

    def test_detects_stop_inside_a_sentence(self):
        self.assertTrue(Transcriber._has_stop(result_json("please stop now")))

    def test_ignores_sentences_without_stop(self):
        self.assertFalse(Transcriber._has_stop(result_json("move forward")))

    def test_ignores_empty_result(self):
        self.assertFalse(Transcriber._has_stop(result_json("")))

    def test_ignores_words_that_only_contain_stop(self):
        self.assertFalse(Transcriber._has_stop(result_json("stopping")))
        self.assertFalse(Transcriber._has_stop(result_json("stopwatch")))


class StopMethodTests(unittest.TestCase):
    def test_returns_recognized_text_without_stop(self):
        t = make_transcriber(
            main=FakeRecognizer([(True, "move forward")]),
            stop=FakeRecognizer([(False, "")]))
        t._recording = True
        feed(t, 1)
        result = t.stop()
        self.assertEqual(result.text, "move forward")
        self.assertFalse(result.stop_heard)

    def test_sets_stop_heard_when_stop_is_in_audio(self):
        t = make_transcriber(
            main=FakeRecognizer([(True, "stop")]),
            stop=FakeRecognizer([(True, "stop")]))
        t._recording = True
        feed(t, 1)
        result = t.stop()
        self.assertTrue(result.stop_heard)
        self.assertEqual(result.text, "stop")

    def test_joins_multiple_recognized_parts(self):
        t = make_transcriber(
            main=FakeRecognizer([(True, "move"), (True, "forward")]),
            stop=FakeRecognizer([(False, ""), (False, "")]))
        t._recording = True
        feed(t, 2)
        self.assertEqual(t.stop().text, "move forward")

    def test_skips_empty_parts(self):
        t = make_transcriber(
            main=FakeRecognizer([(True, ""), (True, "go")]),
            stop=FakeRecognizer([(False, ""), (False, "")]))
        t._recording = True
        feed(t, 2)
        self.assertEqual(t.stop().text, "go")

    def test_uses_final_result_for_text_left_in_recognizer(self):
        t = make_transcriber(
            main=FakeRecognizer(final_text="turn left"),
            stop=FakeRecognizer())
        t._recording = True
        self.assertEqual(t.stop().text, "turn left")

    def test_uses_final_result_for_stop_word_left_in_recognizer(self):
        t = make_transcriber(
            main=FakeRecognizer(),
            stop=FakeRecognizer(final_text="stop"))
        t._recording = True
        self.assertTrue(t.stop().stop_heard)

    def test_nothing_recorded_gives_empty_result(self):
        t = make_transcriber()
        result = t.stop()
        self.assertEqual(result.text, "")
        self.assertFalse(result.stop_heard)

    def test_stop_ends_recording(self):
        t = make_transcriber()
        t._recording = True
        t.stop()
        self.assertFalse(t._recording)


class StartAndCallbackTests(unittest.TestCase):
    def test_start_clears_old_audio_and_begins_recording(self):
        t = make_transcriber()
        feed(t, 3)
        t.start()
        self.assertTrue(t._recording)
        self.assertTrue(t._queue.empty())

    def test_callback_keeps_audio_only_while_recording(self):
        t = make_transcriber()
        t._callback(b"ignored", 1, None, None)
        self.assertTrue(t._queue.empty())
        t._recording = True
        t._callback(b"kept", 1, None, None)
        self.assertEqual(t._queue.get(), b"kept")


if __name__ == "__main__":
    unittest.main()
