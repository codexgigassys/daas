import datetime
import logging
import json
from threading import Lock

from ...config import CHART_TIMEOUT

chart_update_lock = Lock()


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
        self.echart_type = echart_type
        self.full_width = full_width
