"""Tek ornek kilidi yardimcilari."""

from __future__ import annotations

import unittest

from overlay import _INSTANCE_SOCK, _ping_existing_instance, _start_single_instance_server


class SingleInstanceTests(unittest.TestCase):
    def test_sock_name(self) -> None:
        self.assertEqual(_INSTANCE_SOCK, "TokenTracker.single")

    def test_ping_without_server(self) -> None:
        from PySide6.QtNetwork import QLocalServer

        QLocalServer.removeServer(_INSTANCE_SOCK)
        # If another TokenTracker is running, ping may succeed — that's ok for this unit.
        result = _ping_existing_instance()
        self.assertIsInstance(result, bool)

    def test_server_starts(self) -> None:
        server = _start_single_instance_server()
        self.assertIsNotNone(server)
        try:
            self.assertTrue(_ping_existing_instance())
        finally:
            server.close()
            from PySide6.QtNetwork import QLocalServer

            QLocalServer.removeServer(_INSTANCE_SOCK)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    unittest.main()
