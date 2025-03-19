from django.contrib import admin
from daas_app.models.sample import Sample
from daas_app.models.task import Task
from daas_app.models.result import Result


# Register your models here.
@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'sha1', 'file_name', 'size', 'seaweedfs_file_id', 'uploaded_on')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'task_id', '_status', 'created_on', 'sample')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'timeout', 'elapsed_time', 'exit_status', 'status', 'output', 'seaweed_result_id', 'decompiler', 'sample', 'processed_on', 'version', 'extension')
