from pyecharts.charts import Line
from pyecharts import options as opts

from .statistics_manager import StatisticsManager
from ..configuration_manager import ConfigurationManager


def bar_datazoom_slider() -> Line:
    groups = [StatisticsManager().get_sample_counts_per_upload_date(file_type) for file_type in
              ConfigurationManager().get_identifiers()]
    chart = Line()
    chart.add_xaxis(groups[0].captions)
    for group in groups:
        chart.add_yaxis(group.file_type,
                        group.counts,
                        linestyle_opts=opts.LineStyleOpts(width=2),
                        label_opts=opts.LabelOpts(is_show=False))
        chart.add_yaxis(group.simple_moving_average_legend,
                        group.simple_moving_average,
                        linestyle_opts=opts.LineStyleOpts(width=2, type_='dashed'),
                        label_opts=opts.LabelOpts(color="black", background_color="white"))
    chart.set_global_opts(title_opts=opts.TitleOpts(title="Samples per upload date"),
                          datazoom_opts=opts.DataZoomOpts())
    return chart
