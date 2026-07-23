"""
Atmospheric Complexity Framework API
"""

from acf.core.default_parameters import create_registry
from acf.ai.analyzers.dataset_analyzer import DatasetAnalyzer
from acf.ai.forecast.forecast_assistant import ForecastAssistant
from acf.ai.alerts.weather_alert_engine import WeatherAlertEngine


class ACFAPI:

    def __init__(self):

        self.registry = create_registry()

        self.analyzer = DatasetAnalyzer()

        self.forecast = ForecastAssistant()

        self.alert_engine = WeatherAlertEngine()

    ##################################################

    def parameters(self):

        return self.registry.all()

    ##################################################

    def parameter(self, parameter_id):

        return self.registry.get(parameter_id)

    ##################################################

    def analyze(self, dataset):

        return self.analyzer.analyze(dataset)

    ##################################################

    def forecast_report(self, dataset):

        return self.forecast.generate_report(dataset)

    ##################################################

    def register_alert_rule(
        self,
        variable,
        threshold,
        level,
        message
    ):

        self.alert_engine.register_rule(
            variable,
            threshold,
            level,
            message
        )

    ##################################################

    def alerts(self, dataset):

        return self.alert_engine.analyze(dataset)
