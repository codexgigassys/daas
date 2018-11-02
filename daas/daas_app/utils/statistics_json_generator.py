from ..models import Sample


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
            'itemStyle': {'normal': {'label': {'show': True, 'position': 'insideRight'}}},
            'data': counts}


def generate_multiple_series(series_data):
    return [generate_one_series(identifier, counts) for identifier, counts in series_data.items()]


def generate_stacked_bar_chart(y_axis_legend, upper_legend, querysets):
    """
    :param y_axis_legend: [str]
    :param upper_legend: [str]
    :param data: [<QuerySet>, <QuerySet>, <QuerySet>, ...]
    :return:
    """
    series_data = generate_data_for_multiple_series(querysets)
    series = generate_multiple_series(series_data)

    option = {'tooltip': {'trigger': 'axis',
                          'axisPointer': {'type': 'shadow'}},
              'legend': {'data': upper_legend},
              'toolbox': {'show': True,
                          'feature': {'dataView': {'show': True, 'readOnly': True},
                                      'magicType': {'show': True, 'type': ['line', 'bar', 'stack', 'tiled']},
                                      'restore': {'show': True},
                                      'saveAsImage': {'show': True}}},
              'calculable': True,
              'xAxis': [{'type': 'value'}],
              'yAxis': [{'type': 'category',
                        'data': y_axis_legend}],
              'series': series}
    # data [csharp1kb, chsarp1mb, ....]
    return option
