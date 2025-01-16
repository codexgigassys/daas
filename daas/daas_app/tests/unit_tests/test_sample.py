from django.test import TestCase
from daas_app.models.sample import Sample
from daas_app.models.sample import SampleQuerySet


class TestSample(TestCase):
    def test_sample_query_set_with_size_between(self):
        # Test SampleQuerySet: with_size_between
        tmp_sample_query_set = Sample.objects.with_size_between(0, 2)
        assert isinstance(tmp_sample_query_set, SampleQuerySet)
        assert tmp_sample_query_set.count() == 0

    def test_sample_query_set_with_elapsed_time_between(self):
        # Test SampleQuerySet: with_elapsed_time_between
        tmp_sample_query_set = Sample.objects.with_elapsed_time_between(0, 2)
        assert isinstance(tmp_sample_query_set, SampleQuerySet)
        assert tmp_sample_query_set.count() == 0

    def test_sample_query_set_failed(self):
        # Test SampleQuerySet: failed
        tmp_sample_query_set = Sample.objects.failed()
        assert isinstance(tmp_sample_query_set, SampleQuerySet)
        assert tmp_sample_query_set.count() == 0

    def test_sample_query_set_decompiled(self):
        # Test SampleQuerySet: decompiled
        tmp_sample_query_set = Sample.objects.decompiled()
        assert isinstance(tmp_sample_query_set, SampleQuerySet)
        assert tmp_sample_query_set.count() == 0

    def test_sample_query_set_timed_out(self):
        # Test SampleQuerySet: timed_out
        tmp_sample_query_set = Sample.objects.timed_out()
        assert isinstance(tmp_sample_query_set, SampleQuerySet)
        assert tmp_sample_query_set.count() == 0

    def test_sample_query_set_finished(self):
        # Test SampleQuerySet: finished
        tmp_sample_query_set = Sample.objects.finished()
        assert isinstance(tmp_sample_query_set, SampleQuerySet)
        assert tmp_sample_query_set.count() == 0

    def test_sample_query_set_with_file_type(self):
        # Test SampleQuerySet: with_file_type
        tmp_sample_query_set = Sample.objects.with_file_type('java')
        assert isinstance(tmp_sample_query_set, SampleQuerySet)
        assert tmp_sample_query_set.count() == 0

    def test_sample_query_set_with_file_type_in(self):
        # Test SampleQuerySet: with_file_type_in
        tmp_sample_query_set = Sample.objects.with_file_type_in([
                                                                'java', 'flash'])
        assert isinstance(tmp_sample_query_set, SampleQuerySet)
        assert tmp_sample_query_set.count() == 0
