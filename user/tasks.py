from celery import shared_task
from django.core.management import call_command


@shared_task
def clean_blacklisted_tokens():
    call_command("clean_blacklisted_tokens")
