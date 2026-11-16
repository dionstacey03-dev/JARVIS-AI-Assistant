"""Unit tests for JARVIS desktop commands without opening apps or websites."""

import unittest
from unittest.mock import patch

import commands


class CommandTests(unittest.TestCase):
    def test_time_command_returns_readable_time(self):
        with patch.object(commands.dt, "datetime") as clock:
            clock.now.return_value.astimezone.return_value.strftime.return_value = "It is 09:30 AM."
            self.assertEqual(commands.execute("what time is it"), "It is 09:30 AM.")

    def test_open_website_uses_browser(self):
        with patch.object(commands.webbrowser, "open") as open_browser:
            self.assertEqual(commands.execute("open github"), "Opening Github.")
        open_browser.assert_called_once_with("https://github.com")

    def test_google_search_encodes_query(self):
        with patch.object(commands.webbrowser, "open") as open_browser:
            result = commands.execute("search google for python async")
        self.assertEqual(result, "Searching Google for python async.")
        open_browser.assert_called_once_with(
            "https://www.google.com/search?q=python+async"
        )

    def test_empty_search_query_is_explained(self):
        self.assertIn("what you would like", commands.execute("search google for"))

    def test_unknown_command_is_not_claimed_as_executed(self):
        self.assertIsNone(commands.execute("do something impossible"))

    def test_screen_analysis_failure_is_handled(self):
        with patch.object(commands, "capture_screen", side_effect=OSError("no display")):
            self.assertEqual(
                commands.execute("what is on my screen"),
                "I was unable to analyze the screen.",
            )


if __name__ == "__main__":
    unittest.main()
