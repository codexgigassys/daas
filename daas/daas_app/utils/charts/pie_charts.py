from pyecharts import options as opts
from pyecharts.charts import Pie

from .statistics_manager import StatisticsManager


def generate_pie_chart(statistics, title) -> Pie:
    chart = (
        Pie()
        .add("", statistics)
        .set_global_opts(title_opts=opts.TitleOpts(title=title, pos_left='center', pos_top='top'),
                         legend_opts=opts.LegendOpts(pos_top='bottom'))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return chart


def samples_per_type() -> Pie:
    return generate_pie_chart(StatisticsManager().get_sample_count_per_file_type(), "Samples per type")


def samples_per_status_for_file_type(file_type: str) -> Pie:
    return generate_pie_chart(StatisticsManager().get_sample_count_per_status_for_type(file_type), "Samples per type")
