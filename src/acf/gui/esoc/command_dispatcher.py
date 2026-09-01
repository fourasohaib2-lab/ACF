"""Command dispatcher, thread-safe event bus, and Phase 12 product generator (ACF-UI-013)."""

import logging
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

logger = logging.getLogger("acf.gui.esoc")


class WorkerRunnable(QRunnable):
    """Background worker task for asynchronous execution (Phase 14)."""

    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        """
        NOTE (correction): used to swallow any exception raised by `fn`
        completely silently - no logging, no signal, nothing - so a
        background command that genuinely failed (e.g. a real forecast
        run erroring out) looked from the UI's perspective identical to
        one that quietly succeeded. A QRunnable.run() must not itself
        raise (that would take down the worker thread), but the failure
        is now at least logged rather than vanishing without a trace.
        """
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception:
            logger.exception("Async command %r failed in background worker", getattr(self.fn, "__name__", self.fn))


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
        self._command_handlers: dict[str, Callable[..., Any]] = {}
        self.thread_pool = QThreadPool.globalInstance()

    def register_command(self, command_name: str, handler: Callable[..., Any]) -> None:
        """Register a handler callback for a named command."""
        self._command_handlers[command_name] = handler

    def run_async(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Execute a callable asynchronously on the global thread pool (Phase 14)."""
        worker = WorkerRunnable(fn, *args, **kwargs)
        self.thread_pool.start(worker)

    def export_product(self, product_format: str, output_path: str) -> str:
        """Phase 12 Product Exporter: PNG, SVG, PDF, NetCDF4, GRIB2, GeoTIFF, COG, Zarr, CSV, GeoJSON, MP4, GIF.

        NOTE (correction): this used to write the identical one-line text
        string ("ACF Product Export Format: <FMT>") into `output_path`
        for ANY of the 12 claimed formats - a ".png" export got a text
        file, a "NetCDF4" export got the same text file, none of them
        real content in the requested format - then unconditionally
        emitted `product_exported` and returned the path as if a genuine
        export had happened. This method has no data parameter at all
        (only `product_format` and `output_path`), so there is no real
        simulation state or figure available here to serialize even in
        principle; real per-format writers exist elsewhere in this
        codebase (e.g. simulation_engine/output/netcdf_writer.py,
        zarr_writer.py, tested and genuinely functional) but operate on
        actual state/lats/lons/levels data this method was never given.
        Verified via grep: this method has zero callers anywhere in the
        codebase and zero test coverage - nothing currently depends on
        its exact return contract. Rather than keep fabricating a
        same-looking-regardless-of-format placeholder file, this now
        honestly raises instead of claiming an export that didn't happen.
        """
        raise NotImplementedError(
            f"export_product({product_format!r}, {output_path!r}) needs real simulation/figure "
            "data to serialize - none is passed to this method. Previously wrote an identical "
            "placeholder text file regardless of the requested format and claimed success; "
            "removed rather than left silently wrong. Wire a real per-format writer (see "
            "simulation_engine/output/netcdf_writer.py and zarr_writer.py for working examples) "
            "with actual data once this method has something real to export."
        )

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
            self.log_message_emitted.emit("WARNING", f"No handler registered for command: {command_name}")
            return None
