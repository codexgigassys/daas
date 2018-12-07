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
        self.update_charts()
        return self.get_charts()

    @property
    def time_since_last_update(self):
        return max([chart.time_since_last_update.seconds for chart in self.charts])

    def update_charts(self):
        for chart in self.charts:
            chart.update()

    @property
    def time_since_last_update_as_string(self):
        time_since_last_update = self.time_since_last_update
        if time_since_last_update < 60:
            value = int(time_since_last_update)
            time_since_last_update_as_string = "%s second" % value
        elif time_since_last_update < 3600:
            value = int(time_since_last_update / 60)
            time_since_last_update_as_string = "%s minute" % value
        elif time_since_last_update < 3600*24:
            value = int(time_since_last_update / 3600)
            time_since_last_update_as_string = "%s hour" % value
        else:
            value = int(time_since_last_update / (3600 * 24))
            time_since_last_update_as_string = "%s day" % value
        # Add 's' for plural if value is not 1:
        time_since_last_update_as_string += ('.' if value == 1 else 's.')
        return time_since_last_update_as_string
