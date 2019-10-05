from pyecharts.charts import Line
from pyecharts import options as opts
from typing import List

from .statistics_manager import StatisticsManager
from .groups import DateCounterGroup
from ..configuration_manager import ConfigurationManager


def generate_line_chart_with_slider(title: str, xaxis_caption: str, groups: List[DateCounterGroup]) -> Line:
    chart = Line()
    chart.set_global_opts(title_opts=opts.TitleOpts(title=title),
                          datazoom_opts=opts.DataZoomOpts(range_start=0, range_end=100),
                          yaxis_opts=opts.AxisOpts(name='Samples',
                                                   name_textstyle_opts=opts.global_options.TextStyleOpts(font_size=16)),
                          xaxis_opts=opts.AxisOpts(name=xaxis_caption,
                                                   name_textstyle_opts=opts.global_options.TextStyleOpts(font_size=16)))
    # X axis
    chart.add_xaxis(groups[0].captions)

    # Y axis
    for group in groups:
        # Samples per day
        chart.add_yaxis(group.file_type,
                        group.counts,
                        linestyle_opts=opts.LineStyleOpts(width=2),
                        label_opts=opts.LabelOpts(is_show=False))
        # Simple moving average (SMA)
        chart.add_yaxis(group.simple_moving_average_legend,
                        group.simple_moving_average,
                        linestyle_opts=opts.LineStyleOpts(width=2, type_='dashed'),
                        label_opts=opts.LabelOpts(color='black', background_color='white'))
    return chart


def samples_per_upload_date() -> Line:
    groups = [StatisticsManager().get_sample_counts_per_upload_date(file_type) for file_type in
              ConfigurationManager().get_identifiers()]
    return generate_line_chart_with_slider(title='Samples per upload date',
                                           xaxis_caption='Upload date',
                                           groups=groups)


def samples_per_process_date() -> Line:
    groups = [StatisticsManager().get_sample_counts_per_process_date(file_type) for file_type in
              ConfigurationManager().get_identifiers()]
    return generate_line_chart_with_slider(title='Samples per upload date',
                                           xaxis_caption='Process date',
                                           groups=groups)
