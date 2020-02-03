from django.http import HttpRequest
from typing import Dict

from .utils.charts.statistics_manager import StatisticsManager
# Increase this number after every release to force browsers to download the latest static files
RELEASE_NUMBER = 10


def release_number(request: HttpRequest) -> Dict[str, str]:
    return {'release_number': f'?v={RELEASE_NUMBER}'}


def sample_count_context(request: HttpRequest) -> Dict[str, int]:
    return {'samples_count': StatisticsManager().get_total_sample_count()}
