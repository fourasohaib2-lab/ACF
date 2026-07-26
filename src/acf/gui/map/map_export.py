"""
Atmospheric Complexity Framework (ACF)

Map Export
==========

Export mixin for MapCanvas.
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
