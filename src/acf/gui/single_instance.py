"""
acf.gui.single_instance - prevents multiple simultaneous ESOC instances.

Real user-reported bug (2026-09-06): launching the app more than once
(double-clicking a desktop shortcut, re-running the launch command
without noticing a previous instance was already up, a misconfigured
autostart entry) opened a separate, fully independent ESOCWindow each
time - "several dashboards showing at once", with zero coordination
between them. Verified by reading acf.gui.app.run() and
ESOCWindow.__init__(): neither ever checked for an existing instance -
confirmed by grepping the whole gui/ package for
"QLocalServer"/"QLocalSocket"/"singleton" before this fix, zero hits.

Uses Qt's own QLocalServer/QLocalSocket - a named local socket (a Unix
domain socket path or a Windows named pipe under the hood, not a TCP
port that could collide with something else or need a firewall rule) -
the standard, real, cross-platform Qt mechanism for this, not a
home-rolled PID/lock-file scheme prone to races.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket

#: Real, fixed name for the local socket - every acf-gui process on this
#: machine/user session tries to reach the same name, which is exactly
#: the point (one name -> at most one real listener -> at most one real
#: instance).
SERVER_NAME = "acf-esoc-single-instance"

#: How long to wait for a connection/write/read before concluding no
#: real instance answered. Generous enough for a loaded machine, short
#: enough not to make every launch feel sluggish.
_TIMEOUT_MS = 300


class SingleInstanceGuard(QObject):
    """
    Real single-instance guard for the ESOC application.

    Call acquire() once, right after constructing QApplication (a
    QLocalSocket/QLocalServer needs a real Qt event loop context to
    exist). It returns True exactly once per machine/session - for the
    one process that should actually go on to build a real ESOCWindow.
    Every later process in the same session gets False, and this class
    has already asked the real first instance (via the socket) to raise
    its own window - the caller of a False result should exit
    immediately without building any UI of its own.

    activation_requested fires, in the FIRST instance only, every time
    a later instance tries to start - connect it to raise/activate the
    real window so a user who "launches the app again" sees their
    existing session come to the front, not nothing (and not a second
    window).
    """

    activation_requested = Signal()

    def __init__(self, server_name: str = SERVER_NAME, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._server_name = server_name
        self._server: QLocalServer | None = None

    def acquire(self) -> bool:
        """
        Try to become the one real running instance.

        Returns
        -------
        bool
            True if no other real instance answered (this process
            should build its own UI, and is now listening for later
            processes to ask it to raise that UI). False if a real
            other instance answered and was already asked, over the
            socket, to activate itself.
        """
        probe = QLocalSocket()
        probe.connectToServer(self._server_name)
        if probe.waitForConnected(_TIMEOUT_MS):
            # A real other instance is listening right now - tell it to
            # raise its own window, then this process is done.
            probe.write(b"activate")
            probe.flush()
            probe.waitForBytesWritten(_TIMEOUT_MS)
            probe.disconnectFromServer()
            return False

        # No real listener answered. On Linux, QLocalServer's underlying
        # socket file can be left behind after a crash/kill -9 without a
        # clean shutdown - removeServer() is only safe to call here
        # BECAUSE the connect attempt above just proved nothing is truly
        # listening on this name right now.
        QLocalServer.removeServer(self._server_name)

        self._server = QLocalServer(self)
        self._server.newConnection.connect(self._on_new_connection)
        if not self._server.listen(self._server_name):
            # Could not bind for a reason unrelated to another real
            # instance existing (e.g. a permissions problem) - fail
            # open rather than blocking a genuine launch over a
            # socket-layer issue this guard cannot itself resolve.
            return True

        return True

    def _on_new_connection(self) -> None:
        if self._server is None:
            return
        conn = self._server.nextPendingConnection()
        if conn is None:
            return
        conn.readyRead.connect(lambda: self._on_ready_read(conn))

    def _on_ready_read(self, conn: QLocalSocket) -> None:
        conn.readAll()
        self.activation_requested.emit()
        conn.disconnectFromServer()
