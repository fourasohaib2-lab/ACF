"""
Atmospheric Complexity Framework (ACF)

Map Export
==========

NOTE (Physics Guard, 2026-09-06 Tier C sweep): despite "for MapCanvas"
below, `class MapCanvas(EventMixin, QWidget)` in map_canvas.py does
NOT mix this class in - verified by reading that class's own base
list. Real code, not fabricated, just never wired in - see
map_rendering.py's own NOTE (same finding, fuller context) and this
package's __init__.py for the broader disconnected-reserve pattern.

Export mixin - NOT currently used by MapCanvas.
"""

from pathlib import Path


class ExportMixin:
    ##################################################
    # PNG
    ##################################################

    def export_png(
        self,
        filename,
        dpi=300,
    ):

        if self.figure is None:
            return False

        self.figure.savefig(
            filename,
            dpi=dpi,
            bbox_inches="tight",
        )

        return True

    ##################################################
    # PDF
    ##################################################

    def export_pdf(
        self,
        filename,
    ):

        if self.figure is None:
            return False

        self.figure.savefig(
            filename,
            format="pdf",
            bbox_inches="tight",
        )

        return True

    ##################################################
    # SVG
    ##################################################

    def export_svg(
        self,
        filename,
    ):

        if self.figure is None:
            return False

        self.figure.savefig(
            filename,
            format="svg",
            bbox_inches="tight",
        )

        return True

    ##################################################
    # Generic
    ##################################################

    def export(
        self,
        filename,
        dpi=300,
    ):

        extension = Path(filename).suffix.lower()

        if extension == ".png":
            return self.export_png(
                filename,
                dpi,
            )

        elif extension == ".pdf":
            return self.export_pdf(
                filename,
            )

        elif extension == ".svg":
            return self.export_svg(
                filename,
            )

        return False
