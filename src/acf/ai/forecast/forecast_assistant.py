"""
Forecast Assistant
"""

from acf.ai.analyzers.dataset_analyzer import DatasetAnalyzer


class ForecastAssistant:
    """
    Génère un premier résumé météorologique.
    """

    def __init__(self):

        self.analyzer = DatasetAnalyzer()

    ##################################################

    def generate_report(self, dataset):

        analysis = self.analyzer.analyze(dataset)

        report = []

        ##################################################
        # TEMPERATURE
        ##################################################

        if "temperature" in analysis:
            mean = analysis["temperature"]["mean"]

            if mean < 0:
                report.append("Cold conditions expected.")

            elif mean < 15:
                report.append("Cool weather expected.")

            elif mean < 30:
                report.append("Warm weather expected.")

            else:
                report.append("Very hot conditions expected.")

        ##################################################
        # PRESSURE
        ##################################################

        if "pressure" in analysis:
            pressure = analysis["pressure"]["mean"]

            if pressure < 1000:
                report.append("Possible low-pressure system.")

            elif pressure > 1025:
                report.append("Stable high-pressure conditions.")

        ##################################################
        # HUMIDITY
        ##################################################

        if "humidity" in analysis:
            humidity = analysis["humidity"]["mean"]

            if humidity > 80:
                report.append("High humidity.")

        return report
