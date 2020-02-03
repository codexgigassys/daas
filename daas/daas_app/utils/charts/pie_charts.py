from pyecharts import options as opts
from pyecharts.charts import Pie
from typing import List, Tuple

from .statistics_manager import StatisticsManager


def generate_pie_chart(statistics: List[Tuple[str, int]], title: str) -> Pie:
    chart = (
        Pie()
        .add("", statistics)
        .set_global_opts(title_opts=opts.TitleOpts(title=title, pos_left='center', pos_top='top'),
                         legend_opts=opts.LegendOpts(pos_top='bottom'))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return chart


def samples_per_type() -> Pie:
    return generate_pie_chart(StatisticsManager().get_sample_count_per_file_type(), 'Samples per type')


def samples_per_status_for_file_type(file_type: str) -> Pie:
    return generate_pie_chart(StatisticsManager().get_sample_count_per_status_for_type(file_type),
                              f'{file_type[0].upper()}{file_type[1:].lower()} samples per status')
