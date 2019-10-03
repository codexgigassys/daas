from pyecharts.charts import Bar, Line
from pyecharts import options as opts
import bottleneck
import random


def simple_moving_average(series, window=7):
    """ Calculates the simple moving average. The <window> parameter indicates how much values to consider. """
    return [round(move_mean_value, 1) for move_mean_value in bottleneck.move_mean(series, window=window, min_count=1)]


def bar_datazoom_slider() -> Bar:
    values = [random.randint(200, 300) for i in range(33)]
    values2 = [random.randint(180, 240) for i in range(33)]
    values3 = [random.randint(100, 195) for i in range(33)]
    c = (
        Line()
        .add_xaxis(['2019-01-01', '2019-01-02', '2019-01-03', '2019-01-04', '2019-01-05', '2019-01-06',
                    '2019-01-07', '2019-01-08', '2019-01-09', '2019-01-10', '2019-01-11', '2019-01-12',
                    '2019-01-13', '2019-01-14', '2019-01-15', '2019-01-16', '2019-01-17', '2019-01-18',
                    '2019-01-19', '2019-01-20', '2019-01-21', '2019-01-22', '2019-01-23', '2019-01-24',
                    '2019-01-25', '2019-01-26', '2019-01-27', '2019-01-28', '2019-01-29', '2019-01-30',
                    '2019-02-01', '2019-02-02', '2019-02-03'])
        .add_yaxis("flash",
                   values,
                   linestyle_opts=opts.LineStyleOpts(width=2),
                   label_opts=opts.LabelOpts(is_show=False))
        .add_yaxis("pe",
                   values2,
                   linestyle_opts=opts.LineStyleOpts(width=2),
                   label_opts=opts.LabelOpts(is_show=False))
        .add_yaxis("java",
                   values3,
                   linestyle_opts=opts.LineStyleOpts(width=2),
                   label_opts=opts.LabelOpts(is_show=False))
        .add_yaxis("flash SMA 7d",
                   simple_moving_average(values),
                   linestyle_opts=opts.LineStyleOpts(width=2, type_='dashed'),
                   label_opts=opts.LabelOpts(color="black", background_color="white"))
        .add_yaxis("pe SMA 7d",
                   simple_moving_average(values2),
                   linestyle_opts=opts.LineStyleOpts(width=2, type_='dashed'),
                   label_opts=opts.LabelOpts(color="black", background_color="white"))
        .add_yaxis("java SMA 7d",
                   simple_moving_average(values3),
                   linestyle_opts=opts.LineStyleOpts(width=2, type_='dashed'),
                   label_opts=opts.LabelOpts(color="black", background_color="white"))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Bar-DataZoom（slider-水平）"),
            datazoom_opts=opts.DataZoomOpts()
        )
        #.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    )
    return c
