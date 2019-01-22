import datetime
import logging
import json

from ...config import CHART_TIMEOUT


class Chart:
    def __init__(self, name, title, echart_type, full_width=True):
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
        self.full_width = full_width
        self.update()

    @property
    def content(self):
        if self.should_update():
            self.update()
        return json.dumps(self.cached_chart)

    @property
    def content_as_json(self):
        return json.dumps(self.content)

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
