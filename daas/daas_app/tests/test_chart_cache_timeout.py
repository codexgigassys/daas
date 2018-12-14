import time

from ..utils.charts.chart_cache import ChartCache
from .test_utils import CustomTestCase


class ChartCacheTest(CustomTestCase):
    def test_time_since_last_update(self):
        ChartCache().get_updated_charts()
        time_since_last_update = ChartCache().time_since_last_update
        self.assertLessEqual(time_since_last_update, 10)
        time.sleep(2)
        self.assertLess(time_since_last_update, ChartCache().time_since_last_update)
        time_since_last_update = ChartCache().time_since_last_update
        ChartCache().get_updated_charts()
        self.assertGreater(time_since_last_update, ChartCache().time_since_last_update)
