"""Fast, hardware-independent tests for JARVIS core orchestration."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import jarvis
import memory
import ui


class ApplicationImportTests(unittest.TestCase):
    def test_desktop_entrypoint_is_available(self):
        self.assertTrue(callable(ui.launch))


class MemoryStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_file = Path(self.temp_dir.name) / "memory.json"
        self.patch_file = patch.object(memory, "MEMORY_FILE", self.memory_file)
        self.patch_file.start()

    def tearDown(self):
        self.patch_file.stop()
        self.temp_dir.cleanup()

    def test_remember_recall_and_forget(self):
        memory.remember("name", "Test User")
        self.assertEqual(memory.recall("name"), "Test User")
        self.assertTrue(memory.forget("name"))
        self.assertIsNone(memory.recall("name"))
        self.assertFalse(memory.forget("missing"))

    def test_corrupt_memory_file_recovers_as_empty_store(self):
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.memory_file.write_text("{broken", encoding="utf-8")
        self.assertEqual(memory.load_memory(), {})


class CommandOrchestrationTests(unittest.TestCase):
    def test_empty_request_is_rejected(self):
        self.assertEqual(jarvis.process_command("  "), ("Please enter a request.", False))

    def test_exit_command_requests_shutdown(self):
        response, should_exit = jarvis.process_command("Goodbye")
        self.assertTrue(should_exit)
        self.assertIn("shutting down", response.casefold())

    def test_builtin_command_response_is_returned(self):
        with patch.object(jarvis, "execute", return_value="Opening Calculator."):
            self.assertEqual(
                jarvis.process_command("open calculator"),
                ("Opening Calculator.", False),
            )

    def test_memory_command_is_handled_before_ai(self):
        with patch.object(jarvis, "remember") as remember:
            response, should_exit = jarvis.process_command("my name is Test User")
        remember.assert_called_once_with("name", "Test User")
        self.assertIn("Test User", response)
        self.assertFalse(should_exit)


if __name__ == "__main__":
    unittest.main()
