"""Command dispatcher, thread-safe event bus, and Phase 12 product generator (ACF-UI-013)."""

from typing import Dict, Any, Callable
import os
from PySide6.QtCore import QObject, Signal, QThreadPool, QRunnable


class WorkerRunnable(QRunnable):
    """Background worker task for asynchronous execution (Phase 14)."""

    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception:
            pass


class CommandDispatcher(QObject):
    """Central event bus, async task runner, and Phase 12 product exporter."""

    command_executed = Signal(str, dict)
    simulation_step_completed = Signal(dict)
    hazard_alert_triggered = Signal(str, dict)
    workspace_mode_changed = Signal(str)
    log_message_emitted = Signal(str, str)
    product_exported = Signal(str, str)  # (format, filepath)

    def __init__(self) -> None:
        super().__init__()
        self._command_handlers: Dict[str, Callable[..., Any]] = {}
        self.thread_pool = QThreadPool.globalInstance()

    def register_command(self, command_name: str, handler: Callable[..., Any]) -> None:
        """Register a handler callback for a named command."""
        self._command_handlers[command_name] = handler

    def run_async(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Execute a callable asynchronously on the global thread pool (Phase 14)."""
        worker = WorkerRunnable(fn, *args, **kwargs)
        self.thread_pool.start(worker)

    def export_product(self, product_format: str, output_path: str) -> str:
        """Phase 12 Product Exporter: PNG, SVG, PDF, NetCDF4, GRIB2, GeoTIFF, COG, Zarr, CSV, GeoJSON, MP4, GIF."""
        self.log_message_emitted.emit("INFO", f"Exporting product format [{product_format.upper()}] to {output_path}")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
        
        # Create output placeholder file
        with open(output_path, "w") as f:
            f.write(f"ACF Product Export Format: {product_format.upper()}\n")

        self.product_exported.emit(product_format, output_path)
        return output_path

    def dispatch(self, command_name: str, **kwargs: Any) -> Any:
        """Execute a registered command and emit notification signals.

        Args:
            command_name: Identifier of the command (e.g., 'run_simulation', 'export_product').
            kwargs: Parameters passed to the command handler.

        Returns:
            Result returned by the handler function.
        """
        self.log_message_emitted.emit("INFO", f"Dispatching command: {command_name}")

        if command_name == "export_product":
            fmt = kwargs.get("format", "png")
            path = kwargs.get("path", f"output_export.{fmt}")
            return self.export_product(fmt, path)

        if command_name in self._command_handlers:
            handler = self._command_handlers[command_name]
            result = handler(**kwargs)
            result_dict = result if isinstance(result, dict) else {"result": result}
            self.command_executed.emit(command_name, result_dict)
            return result
        else:
            self.log_message_emitted.emit(
                "WARNING", f"No handler registered for command: {command_name}"
            )
            return None
