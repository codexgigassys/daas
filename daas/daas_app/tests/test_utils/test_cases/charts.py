from .generic import TestCase


class PieChartCustomTestCase(TestCase):
    fixtures = ['charts.json']
    chart = None  # set it on setUpClass method

    def get_samples_of(self, sample_type):
        return [series['value'] for series in self.chart['series'][0]['data'] if series['name'] == sample_type].pop()


class StackedBarChartCustomTestCase(TestCase):
    fixtures = ['charts.json']
    chart = None  # set it on setUpClass method

    def get_series(self, name):
        return [series['data'] for series in self.chart['series'] if series['name'] == name].pop()

    def get_element_count_of_single_series(self, name):
        return sum(self.get_series(name))

    def get_element_count_of_multiple_series(self, names):
        return sum([self.get_element_count_of_single_series(name) for name in names])


class DataZoomChartCustomTestCase(StackedBarChartCustomTestCase):
    def assertListEqual(self, actual, expected, msg=None):
        number_of_expected_items = len(expected)
        number_of_unexpected_items = len(actual) - number_of_expected_items
        super().assertListEqual(actual[:number_of_expected_items], expected)
        # from the latest day to today, the data zoom chart will generate a date with zero items
        super().assertListEqual(actual[number_of_expected_items:], [0] * number_of_unexpected_items)

    def assertDateListEqual(self, actual, expected):
        length = len(expected)
        super().assertListEqual(actual[:length], expected)
