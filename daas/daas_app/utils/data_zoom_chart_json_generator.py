from ..models import Sample
from ..decompilers.decompiler_config import get_identifiers
import datetime


def get_next_date(date):
    return date + datetime.timedelta(days=1)


def generate_dates():
    date = Sample.objects.first_date()
    today = datetime.date.today()
    dates = []
    while date <= today:
        dates.append(date)
        date = get_next_date(date)
    return dates


def generate_single_series(identifier, counts_by_date, dates):
    counts = [(counts_by_date[date] if date in counts_by_date.keys() else 0) for date in dates]
    return {'name': identifier, 'type': 'line', 'data': counts}


def generate_stacked_bar_chart(date_counts):
    """
    :param date_counts: [{'date': datetime.date, 'count': int}, ...]
    :return:
    """
    dates = generate_dates()
    series = generate_single_series('c#[hardcoded]', date_counts, dates)
    option = {'tooltip': {'trigger': 'axis'},
              'legend': {'data': get_identifiers()},
              'toolbox': {'show': True,
                          'feature': {'mark': {'show': True},
                                      'dataZoom': {'show': True},
                                      'dataView': {'show': True},
                                      'magicType': {'show': True, 'type': ['line', 'bar', 'stack', 'tiled']},
                                      'restore': {'show': True},
                                      'saveAsImage': {'show': True}}},
              'calculable': True,
              'dataZoom': {'show': True,
                           'realtime': True,
                           'start': 20,
                           'end': 80},
              'xAxis': [{'type': 'category',
                         'boundaryGap': False,
                         'data': series}],
              'yAxis': [{'type': 'value'}],
              'series': series}
    return option
