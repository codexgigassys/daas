from ..models import Sample
from ..decompilers.decompiler_config import get_identifiers


def generate_data_for_multiple_series(querysets):
    series_data = {}
    for queryset in querysets:
        count_by_file_type = Sample.objects.count_by_file_type(queryset)
        for identifier, count in count_by_file_type.items():
            if identifier in series_data:
                series_data[identifier].append(count)
            else:
                series_data[identifier] = [count]
    return series_data


def generate_one_series(identifier, counts):
    return {'name': identifier,
            'type': 'bar',
            'stack': 'stack',  # it creates one "bar" (literally, one stack) per different stack name.
            'itemStyle': {'normal': {'label': {'show': False, 'position': 'insideRight'}}},
            'data': counts}


def generate_multiple_series(series_data):
    return [generate_one_series(identifier, counts) for identifier, counts in series_data.items()]


def generate_stacked_bar_chart(main_axis_legend, querysets, count_on_x_axis=False):
    """
    :param main_axis_legend: [str]
    :param data: [<QuerySet>, <QuerySet>, <QuerySet>, ...]. Each queryset should be a group of samples. For example:
                if you are classifying samples by size, the first queryset could be samples with size between 0 and 10,
                the second a queryset of samples with size between 11 and 20, and so on ...
    :param count_on_x_axis: boolean. If it is True, the count would be on the X axis. Otherwise, it will be on the Y axis.
    :return:
    """
    series_data = generate_data_for_multiple_series(querysets)
    series = generate_multiple_series(series_data)

    main_axis = 'yAxis' if count_on_x_axis else 'xAxis'
    other_axis = 'yAxis' if not count_on_x_axis else 'xAxis'
    option = {'tooltip': {'trigger': 'axis',
                          'axisPointer': {'type': 'shadow'}},
              'legend': {'data': get_identifiers()},
              'toolbox': {'show': True,

                          'feature': {'dataView': {'show': True, 'readOnly': True},
                                      'magicType': {'show': True, 'type': ['line', 'bar', 'stack', 'tiled']},
                                      'restore': {'show': True},
                                      'saveAsImage': {'show': True}}},
              'calculable': False,
              other_axis: [{'type': 'value'}],
              main_axis: [{'type': 'category',
                        'data': main_axis_legend}],
              'series': series}
    # data [csharp1kb, chsarp1mb, ....]
    return option
