from ..singleton import ThreadSafeSingleton
from .charts import (SamplesPerDecompilationStatusChart, SamplesPerElapsedTimeChart, SamplesPerProcessDateChart,
                     SamplesPerSizeChart, SamplesPerTypeChart, SamplesPerUploadDateChart)
from ..configuration_manager import ConfigurationManager
from ..lists import flatten


class ChartCache(metaclass=ThreadSafeSingleton):
    def __init__(self):
        self.grouped_charts = {'Samples per elapsed time': [SamplesPerElapsedTimeChart()],
                               'Samples per size': [SamplesPerSizeChart()],
                               'Samples per type': [SamplesPerTypeChart()],
                               'Samples per upload date': [SamplesPerUploadDateChart()],
                               'Samples per process date': [SamplesPerProcessDateChart()],
                               'Samples per decompilation status': [SamplesPerDecompilationStatusChart(file_type=identifier) for identifier in ConfigurationManager().get_identifiers()]}

    @property
    def charts(self):
        return flatten(self.grouped_charts.values())

    def charts_of_group(self, group_name):
        return self.grouped_charts[group_name]

    def get_updated_charts(self):
        self.update_charts()
        return self.charts

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
        # Add 's' for plural
        if value != 1:
            time_since_last_update_as_string += 's'
        return time_since_last_update_as_string
