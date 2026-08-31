"""ESOC Live Remote HPC Terminal Panel (ACF-HPC-002)."""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry


class HPCTerminalPanel(QWidget):
    """Interactive live streaming remote terminal panel inside ESOC."""

    def __init__(
        self,
        registry: ModuleRegistry | None = None,
        dispatcher: CommandDispatcher | None = None,
    ) -> None:
        super().__init__()
        self.registry = registry
        self.dispatcher = dispatcher

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        header = QLabel("💻 REMOTE HPC LIVE TERMINAL")
        header.setStyleSheet("font-weight: bold; font-size: 13px; color: #76FF03;")
        layout.addWidget(header)

        # Output Terminal Text Box
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet(
            "background-color: #000000; color: #00FF00; font-family: monospace; font-size: 12px;"
        )
        # NOTE (correction — operationally dangerous): this used to
        # claim "Connected to: researcher@hpc.university.edu" from
        # construction, before any real connection was attempted, and
        # _exec_cmd() below used to fake EVERY command's output
        # (squeue/nvidia-smi/hostname/pwd each got a fixed canned
        # response, and any other command got "[EXECUTED]: {cmd} (Exit
        # Code: 0)" regardless of whether it was valid or would have
        # succeeded) with no real Paramiko SSH execution of any kind -
        # a user typing real commands into what is presented as a live
        # interactive remote terminal had no way to tell fake output
        # from a real cluster response. Now genuinely executes through
        # self.registry's real HPCConnectionManager when available (see
        # RemoteExecutor/SSHConnector's own "is_simulated" honesty
        # marker, fixed earlier this session), and honestly says so
        # when it isn't. Not fabricated.
        self.terminal_output.setText(
            "Atmospheric Complexity Framework (ACF) Remote Shell v1.0\n"
            "Not connected to any real HPC session yet.\n"
            "Commands typed below are sent through HPCConnectionManager if the registry provides one;\n"
            "output is labeled [SIMULATED] whenever no real SSH transport is active.\n\n"
            "[not connected]$ "
        )
        layout.addWidget(self.terminal_output)

        # Command Input Line & Send Button
        input_layout = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Enter command (e.g. squeue, nvidia-smi, module load cuda)...")
        self.cmd_input.returnPressed.connect(self._exec_cmd)
        input_layout.addWidget(self.cmd_input)

        btn_send = QPushButton("Execute")
        btn_send.clicked.connect(self._exec_cmd)
        input_layout.addWidget(btn_send)

        layout.addLayout(input_layout)

    def _exec_cmd(self) -> None:
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return

        self.cmd_input.clear()
        self.terminal_output.append(f"$ {cmd}")

        # NOTE (correction): see this class's NOTE above - every
        # command used to get a fixed canned response regardless of
        # whether it was ever really executed. Now routed through the
        # real HPCConnectionManager (via self.registry) when available,
        # and honestly labeled when it falls back to a simulated
        # response (see RemoteExecutor.execute_command()'s
        # "is_simulated" marker).
        hpc = self.registry.get_module("hpc_connector") if self.registry is not None else None
        if hpc is None:
            res = "[NOT CONNECTED]: no real HPC connector available from the module registry"
        else:
            try:
                result = hpc.executor.execute_command(cmd)
                tag = "[SIMULATED]" if result.get("is_simulated", True) else "[REMOTE]"
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                exit_code = result.get("exit_code", 0)
                res = f"{tag} (exit_code={exit_code})\n{stdout}"
                if stderr:
                    res += f"\n[stderr] {stderr}"
            except Exception as e:
                res = f"[ERROR]: command execution failed: {e}"

        self.terminal_output.append(res + "\n")
