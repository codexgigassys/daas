from django.db.models.signals import post_save, post_delete, ModelSignal
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


@receiver(post_save, sender=Result)
def report_sample_result_for_statistics(sender: Type, instance: Result, created: bool, **kwargs) -> None:
    if created:
        StatisticsManager().report_processed_sample(instance.sample)


@receiver(post_delete, sender=Result)
def revert_sample_result_for_statistics(sender: Type, instance: Result, **kwargs) -> None:
    StatisticsManager().revert_processed_sample_report(instance.sample)
