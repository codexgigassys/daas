from pyecharts.charts import Line
from pyecharts import options as opts
import bottleneck
from typing import List

from ..statistics_manager import StatisticsManager
from ..configuration_manager import ConfigurationManager


def simple_moving_average(series: List[int], window: int = 7):
    """ Calculates the simple moving average. The <window> parameter indicates how much values to consider. """
    return [round(move_mean_value, 1) for move_mean_value in bottleneck.move_mean(series, window=window, min_count=1)]


def bar_datazoom_slider() -> Line:
    groups = [StatisticsManager().get_sample_count_per_upload_date(file_type) for file_type in
              ConfigurationManager().get_identifiers()]
    chart = Line()
    chart.add_xaxis(groups[0].captions)
    for group in groups:
        chart.add_yaxis(group.file_type,
                        group.counts,
                        linestyle_opts=opts.LineStyleOpts(width=2),
                        label_opts=opts.LabelOpts(is_show=False))
        chart.add_yaxis(f'{group.file_type} SMA (7 days)',
                        simple_moving_average(group.counts),
                        linestyle_opts=opts.LineStyleOpts(width=2, type_='dashed'),
                        label_opts=opts.LabelOpts(color="black", background_color="white"))
    chart.set_global_opts(title_opts=opts.TitleOpts(title="Samples per upload date"),
                          datazoom_opts=opts.DataZoomOpts())
    #.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    return chart
