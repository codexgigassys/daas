from pyecharts import options as opts
from pyecharts.charts import Bar
from typing import List

from ..statistics_manager import StatisticsManager, RangeGroup
from ..configuration_manager import ConfigurationManager


def generte_bar_chart(title: str, xaxis_caption: str, range_groups: List[RangeGroup], bar_gap: int = 4) -> Bar:
    chart = Bar(init_opts=opts.InitOpts(width="1400px", height="720px"))
    chart.set_global_opts(title_opts=opts.TitleOpts(title=title),
                          yaxis_opts=opts.AxisOpts(name='Samples',
                                                   name_textstyle_opts=opts.global_options.TextStyleOpts(font_size=16)),
                          xaxis_opts=opts.AxisOpts(name=xaxis_caption,
                                                   name_textstyle_opts=opts.global_options.TextStyleOpts(font_size=16)))

    # Data (y axis)
    for range_group in range_groups:
        # Add values on the yaxis for each file type.
        # If the count is 0, replace it by None to avoid overlapped numbers in the chart.
        chart.add_yaxis(range_group.file_type, range_group.counts, category_gap=bar_gap, stack="stack1")

    # Captions (x axis)
    chart.add_xaxis(range_groups[0].captions)
    chart.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    return chart


def samples_per_size() -> Bar:
    range_groups = [StatisticsManager().get_size_statistics_for_file_type(file_type) for file_type in ConfigurationManager().get_identifiers()]
    return generte_bar_chart(title='Samples per size',
                             xaxis_caption='Size (kb)',
                             range_groups=range_groups)


def samples_per_elapsed_time() -> Bar:
    range_groups = [StatisticsManager().get_elapsed_time_statistics_for_file_type(file_type) for file_type in ConfigurationManager().get_identifiers()]
    return generte_bar_chart(title='Samples per elapsed time',
                             xaxis_caption='Elapsed time (s)',
                             range_groups=range_groups,
                             bar_gap=16)
