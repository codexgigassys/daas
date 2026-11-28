from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from daas_app.models.result import Result
from daas_app.models.sample import Sample
from daas_app.models.task import Task


class Command(BaseCommand):
    help = "Remove tasks, results and samples (plus GridFS binaries) older than N days."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=3,
            help="Number of days to retain (default: 3).",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Number of rows fetched per DB chunk (default: 500).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be removed without deleting anything.",
        )

    def _delete_results_queryset(self, queryset, batch_size, dry_run=False):
        deleted = 0
        for result in queryset.iterator(chunk_size=batch_size):
            if not dry_run:
                result.delete()
            deleted += 1
        return deleted

    def _delete_samples_queryset(self, queryset, batch_size, dry_run=False):
        deleted_samples = 0
        deleted_linked_results = 0
        for sample in queryset.iterator(chunk_size=batch_size):
            linked_results_qs = Result.objects.filter(sample=sample)
            deleted_linked_results += self._delete_results_queryset(
                linked_results_qs,
                batch_size=batch_size,
                dry_run=dry_run,
            )
            if not dry_run:
                sample.delete()
            deleted_samples += 1
        return deleted_samples, deleted_linked_results

    def _delete_tasks_queryset(self, queryset, batch_size, dry_run=False):
        deleted = 0
        for task in queryset.iterator(chunk_size=batch_size):
            if not dry_run:
                task.delete()
            deleted += 1
        return deleted

    def handle(self, *args, **kwargs):
        days = kwargs["days"]
        batch_size = kwargs["batch_size"]
        dry_run = kwargs["dry_run"]
        cutoff = timezone.now() - timedelta(days=days)

        if days < 1:
            raise CommandError("--days must be >= 1")
        if batch_size < 1:
            raise CommandError("--batch-size must be >= 1")

        old_results = Result.objects.filter(processed_on__lt=cutoff).order_by("id")
        old_samples = Sample.objects.filter(uploaded_on__lt=cutoff).order_by("id")
        old_tasks = Task.objects.filter(created_on__lt=cutoff).order_by("id")

        deleted_results = self._delete_results_queryset(
            old_results,
            batch_size=batch_size,
            dry_run=dry_run,
        )
        deleted_samples, deleted_results_from_samples = self._delete_samples_queryset(
            old_samples,
            batch_size=batch_size,
            dry_run=dry_run,
        )
        deleted_tasks = self._delete_tasks_queryset(
            old_tasks,
            batch_size=batch_size,
            dry_run=dry_run,
        )

        mode = "DRY-RUN" if dry_run else "DONE"
        self.stdout.write(
            self.style.SUCCESS(
                f"[{mode}] cutoff={cutoff.isoformat()} "
                f"deleted_results={deleted_results} "
                f"deleted_results_linked_to_samples={deleted_results_from_samples} "
                f"deleted_samples={deleted_samples} "
                f"deleted_tasks={deleted_tasks} "
                f"batch_size={batch_size}"
            )
        )
