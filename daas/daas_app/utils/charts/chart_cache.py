from ..singleton import ThreadSafeSingleton
from .charts import (SamplesPerDecompilationStatusChart, SamplesPerElapsedTimeChart, SamplesPerProcessDateChart,
                     SamplesPerSizeChart, SamplesPerTypeChart, SamplesPerUploadDateChart)
from ..configuration_manager import ConfigurationManager


class ChartCache(metaclass=ThreadSafeSingleton):
    def __init__(self):
        self.charts = [SamplesPerElapsedTimeChart(),
                       SamplesPerSizeChart(),
                       SamplesPerTypeChart(),
                       SamplesPerUploadDateChart(),
                       SamplesPerProcessDateChart()]
        for identifier in ConfigurationManager().get_identifiers():
            self.charts.append(SamplesPerDecompilationStatusChart(file_type=identifier))

    def add_chart(self, chart):
        self.charts[chart.name] = chart

    def get_charts(self):
        return [chart.to_dictionary() for chart in self.charts]

    def get_updated_charts(self):
        return [chart.updated().to_dictionary() for chart in self.charts]

    @property
    def time_since_last_update(self):
        return max([chart.time_since_last_update.seconds for chart in self.charts])
