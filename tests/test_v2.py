"""Tests for JARVIS V2 local history, approval gates and integration safety."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import conversation
import integrations
import orchestrator
import system_monitor

class ConversationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original = conversation.HISTORY_FILE
        conversation.HISTORY_FILE = Path(self.temp.name) / "history.json"

    def tearDown(self):
        conversation.HISTORY_FILE = self.original
        self.temp.cleanup()

    def test_history_round_trip(self):
        conversation.add_turn("user", "hello")
        conversation.add_turn("assistant", "hi")
        self.assertEqual([x["role"] for x in conversation.load_history()], ["user", "assistant"])

    def test_invalid_role_rejected(self):
        with self.assertRaises(ValueError):
            conversation.add_turn("system", "unsafe")

    def test_clear_history(self):
        conversation.add_turn("user", "hello")
        conversation.clear_history()
        self.assertEqual(conversation.load_history(), [])

class ApprovalTests(unittest.TestCase):
    def test_sensitive_action_requires_approval(self):
        self.assertFalse(orchestrator.authorize("send_email"))
        self.assertTrue(orchestrator.authorize("send_email", user_approved=True))

    def test_unknown_action_rejected(self):
        with self.assertRaises(ValueError):
            orchestrator.plan_action("run_arbitrary_shell")

    def test_whatsapp_requires_approval_before_credentials(self):
        with self.assertRaises(PermissionError):
            integrations.send_whatsapp_message("+10000000000", "hello")

    def test_whatsapp_requires_configuration(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                integrations.send_whatsapp_message("+10000000000", "hello", user_approved=True)

class MonitoringTests(unittest.TestCase):
    def test_snapshot_has_core_metrics(self):
        snapshot = system_monitor.get_system_snapshot()
        self.assertIn("cpu_percent", snapshot)
        self.assertIn("memory_percent", snapshot)

if __name__ == "__main__":
    unittest.main()
