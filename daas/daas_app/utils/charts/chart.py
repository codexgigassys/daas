import datetime
import logging

from ...config import CHART_TIMEOUT


class Chart:
    def __init__(self, name, title, echart_type, echart_theme=None, full_width=True):
        """
        :param name: <str> chart name. Use only lowercase and '_'.
        :param title: <str> title to display above the chart on the front end.
        :param full_width: <bool> if True, the chart will take the whole width of the page,
                           otherwise, it will take only half of the page.
        """
        self.name = name
        self.title = title
        self.timeout = datetime.timedelta(0, CHART_TIMEOUT)  # 0 days, <timeout> seconds.
        self.cached_chart = None
        self.last_update = None
        self.echart_type = echart_type
        self.echart_theme = echart_theme
        self.full_width = full_width
        self.update()

    def get_content(self):
        if self.should_update():
            self.update()
        return self.cached_chart

    @property
    def time_since_last_update(self):
        return datetime.datetime.now() - self.last_update

    def should_update(self):
        return self.time_since_last_update > self.timeout

    def update(self):
        logging.debug('updating chart: %s' % self.name)
        self.cached_chart = self.generate()
        self.last_update = datetime.datetime.now()

    def updated(self):
        self.update()
        return self

    def to_dictionary(self):
        dictionary = {'content': self.get_content(),
                      'name': self.name,
                      'title': self.title,
                      'full_width': self.full_width,
                      'echart_required_chart': self.echart_type}
        if self.echart_theme is not None:
            dictionary['echart_theme'] = self.echart_theme
        return dictionary
