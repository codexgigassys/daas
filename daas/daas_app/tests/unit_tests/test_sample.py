from django.test import TestCase
from daas_app.models.sample import Sample
from daas_app.models.sample import SampleQuerySet


class TestSample(TestCase):
    def test_sample(self):
        # create Sample with random content (asdf)
        w = Sample(md5="912ec803b2ce49e4a541068d495ab570",
                   sha1="3da541559918a808c2402bba5012f6c60b27661c",
                   sha2="f0e4c2f76c58916ec258f246851bea091d14d4247a2fc3e18694461b1816e13b",
                   size=4, file_name="test.txt", file_type='txt')
        w.save()
        # Source code is no available because it is not saved in weedfs
        assert w.source_code is None
        assert w.finished() is False
        assert w.unfinished() is True
        assert w.downloadable() is True
        assert w.is_possible_to_reprocess() is False

    def test_sample_query_set_with_id_in(self):
        # Test SampleQuerySet: with_id_in
        tmp_sample_query_set = Sample.objects.with_id_in([1, 2])
        assert isinstance(tmp_sample_query_set, SampleQuerySet)
        assert tmp_sample_query_set.count() == 0

    def test_sample_query_set_decompiler_version(self):
        # Test SampleQuerySet: processed_with_old_decompiler_version
        tmp_sample_query_set = Sample.objects.processed_with_old_decompiler_version()
        assert isinstance(tmp_sample_query_set, SampleQuerySet)
        assert tmp_sample_query_set.count() == 0
        tmp_sample_query_set = Sample.objects.processed_with_current_decompiler_version()
        assert isinstance(tmp_sample_query_set, SampleQuerySet)
        assert tmp_sample_query_set.count() == 0

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
