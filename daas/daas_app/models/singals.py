from django.db.models.signals import post_save, pre_delete, ModelSignal
from django.dispatch import receiver
from typing import Type

from ..utils.charts import StatisticsManager
from .sample import Sample
from .result import Result


# Signals
@receiver(post_save, sender=Sample)
def report_created_sample_for_statistics(sender: Type, instance: Sample, created: bool, **kwargs) -> None:
    if created:
        StatisticsManager().report_uploaded_sample(instance)


@receiver(pre_delete, sender=Sample)
def delete_sample_result_for_statistics(sender: Type, instance: Sample, **kwargs) -> None:
    if instance.file_type is not None:
        StatisticsManager().delete_sample_by_type(instance.file_type)


@receiver(post_save, sender=Result)
def report_sample_result_for_statistics(sender: Type, instance: Result, created: bool, **kwargs) -> None:
    if created:
        StatisticsManager().report_processed_sample(instance.sample)


@receiver(pre_delete, sender=Result)
def revert_sample_result_for_statistics(sender: Type, instance: Result, **kwargs) -> None:
    # Result rows can be removed via queryset/cascade delete paths that bypass Result.delete().
    # Cleanup here guarantees SeaweedFS artifacts are deleted in all delete flows.
    instance.delete_seaweed_source_code_file()
    StatisticsManager().revert_processed_sample_report(instance.sample)
