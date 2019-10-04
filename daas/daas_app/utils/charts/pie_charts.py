from pyecharts.faker import Faker
from pyecharts import options as opts
from pyecharts.charts import Pie

from .statistics_manager import StatisticsManager


def samples_per_type() -> Pie:
    chart = (
        Pie(init_opts=opts.InitOpts(width="1400px", height="720px"))
        .add("", StatisticsManager().get_sample_count_per_file_type())
        .set_global_opts(title_opts=opts.TitleOpts(title='Samples per type', pos_left='center', pos_top='top'),
                         legend_opts=opts.LegendOpts(pos_top='bottom'))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return chart
