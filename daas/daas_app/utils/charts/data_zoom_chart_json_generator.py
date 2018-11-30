import datetime

from ...models import Sample
from ...utils.configuration_manager import ConfigurationManager


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


def generate_single_series(identifier, queryset, dates):
    """
    :param identifier: ie: 'flash'
    :param counts_by_date: ie: [{'date': datetime(2018,11,01), 'count':1}, ...]
    :param dates: [datetime] with all the dates from the date of the first uploaded sample.
    :return: list of series for the data zoom chart.
    """
    counts = []
    for date in dates:
        count_found = False
        for element in queryset:
            if element['date'] == date:
                counts.append(element['count'])
                count_found = True
                break
        if not count_found:
            counts.append(0)
    return {'name': identifier, 'type': 'line', 'data': counts}


def generate_multiple_series(classified_counts, dates):
    return [generate_single_series(identifier, queryset, dates) for (identifier, queryset) in classified_counts.items()]


def generate_zoom_chart(classified_counts):
    """
    :param classified_counts: {'pe': [{'date': datetime(2018,11,01), 'count':1}, ...],
                               'flash': [...]}
    :return:
    """
    dates = generate_dates()
    series = generate_multiple_series(classified_counts, dates)
    option = {'tooltip': {'trigger': 'axis'},
              'legend': {'data': ConfigurationManager().get_identifiers()},
              'toolbox': {'show': True,
                          'feature': {'magicType': {'show': True, 'type': ['line', 'bar']},
                                      'saveAsImage': {'show': True}}},
              'dataZoom': {'show': True,
                           'realtime': True,
                           # show only last 30 days by default.
                           'start': int((len(dates) - 30)/len(dates)) if len(dates) > 30 else 0,
                           'end': 100},
              'xAxis': [{'type': 'category',
                         'boundaryGap': False,
                         'data': [date.__str__() for date in dates]}],
              'yAxis': [{'type': 'value'}],
              'series': series}
    return option
