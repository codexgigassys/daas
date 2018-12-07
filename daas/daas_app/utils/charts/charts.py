from django.db.models import Max

from .bar_chart_json_generator import generate_stacked_bar_chart
from .pie_chart_json_generator import generate_pie_chart
from .data_zoom_chart_json_generator import generate_zoom_chart
from ...models import Sample, Result
from ..configuration_manager import ConfigurationManager
from .chart import Chart


class SamplesPerSizeChart(Chart):
    def __init__(self):
        super().__init__(name='samples_per_size_chart',
                         title='Samples per size',
                         echart_type='bar')

    def generate(self):
        ranges = [(0, 30), (30, 60), (60, 90), (90, 120), (120, 150), (150, 180), (180, 1000), (1000, 2**20)]
        samples_by_size_range = [Sample.objects.with_size_between(size_from*1024, size_to*1024 - 1) for (size_from, size_to) in ranges]
        y_axis_legend = ["< 30kb", "30-59kb", "60-89kb", "90-119kb", "120-149kb", "150-179kb", "180-1000kb", "> 1000kb"]
        chart = generate_stacked_bar_chart(y_axis_legend, samples_by_size_range)
        return chart


class SamplesPerElapsedTimeChart(Chart):
    def __init__(self):
        super().__init__(name='samples_per_elapsed_time_chart',
                         title='Samples per elapsed time',
                         echart_type='bar')

    def generate(self):
        max_elapsed_time = Result.objects.decompiled().aggregate(Max('elapsed_time'))['elapsed_time__max']
        # this would limit the number items on X axis to 30 at most.
        # If step is 2, X axis items would be: 1-2, 3-4, 5-6, ....
        # If step is 3: 1-3, 4-6, 7-9, ...
        # If step is 4: 1-4, 5-8, 8-11, ...
        steep = max(int(max_elapsed_time / 30) + 1, 2)
        # Generate the above mentioned ranges based on the steep, from zero to the maximum elapsed time.
        # Adding "steep + (max_elapsed_time % steep)" to the top of the range,
        # we ensure that there wont be any value outside the range list.
        ranges = [(i, i + (steep - 1)) for i in range(0, max_elapsed_time + steep + (max_elapsed_time % steep), steep)]
        samples_by_elapsed_time_range = [Sample.objects.with_elapsed_time_between(from_, to) for (from_, to) in ranges]
        y_axis_legend = ["%s-%s" % element for element in ranges]  # 1-2, 3-4, 5-6, ...
        chart = generate_stacked_bar_chart(y_axis_legend, samples_by_elapsed_time_range)
        return chart


class SamplesPerTypeChart(Chart):
    def __init__(self):
        super().__init__(name='samples_per_type_chart',
                         title='Samples per type',
                         echart_type='pie')

    def generate(self):
        chart = generate_pie_chart(Sample.objects.classify_by_file_type(count=True))
        return chart


class SamplesPerDecompilationStatusChart(Chart):
    def __init__(self, file_type):
        self.file_type = file_type
        super().__init__(name='samples_per_size_chart_%s' % file_type,  # todo fixme!
                         title='%s samples by status' % ConfigurationManager().get_configuration(file_type).sample_type,
                         echart_type='pie',
                         full_width=False)

    def generate(self):
        samples_of_a_given_type_by_status = {'Decompiled': Sample.objects.decompiled().filter(file_type=self.file_type).count(),
                                             'Time out': Sample.objects.timed_out().filter(file_type=self.file_type).count(),
                                             'Failed': Sample.objects.failed().filter(file_type=self.file_type).count()}
        chart = generate_pie_chart(samples_of_a_given_type_by_status)
        return chart


class SamplesPerUploadDateChart(Chart):
    def __init__(self):
        super().__init__(name='samples_per_upload_date_chart',
                         title='Samples per upload date',
                         echart_type='pie')

    def generate(self):
        counts = Sample.objects.samples_per_upload_date().classify_by_file_type()
        chart = generate_zoom_chart(counts)
        return chart


class SamplesPerProcessDateChart(Chart):
    def __init__(self):
        super().__init__(name='samples_per_process_date',
                         title='Samples per process date',
                         echart_type='pie')

    def generate(self):
        counts = Sample.objects.samples_per_process_date().classify_by_file_type()
        chart = generate_zoom_chart(counts)
        return chart
