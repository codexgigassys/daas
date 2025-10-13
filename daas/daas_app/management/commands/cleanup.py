from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from daas_app.models.result import Result
from daas_app.models.sample import Sample
from daas_app.models.task import Task


class Command(BaseCommand):
    help = "Delete objects older than specified days from models Results, Samples, and Tasks"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to keep objects (default: 7)'
        )

    def handle(self, *args, **kwargs):
        days = kwargs['days']
        cutoff = timezone.now() - timedelta(days=days)

        # assuming you have a DateTimeField like created_at or updated_at
        deleted_results, _ = Result.objects.filter(processed_on__lt=cutoff).delete()
        deleted_samples, _ = Sample.objects.filter(uploaded_on__lt=cutoff).delete()
        deleted_tasks, _ = Task.objects.filter(created_on__lt=cutoff).delete()

        self.stdout.write(self.style.SUCCESS(
            f"Deleted {deleted_results} from Result, {deleted_samples} from Sample, {deleted_tasks} from Task"
        ))
