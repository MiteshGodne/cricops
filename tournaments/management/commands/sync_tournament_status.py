from django.core.management.base import BaseCommand
from django.utils import timezone
from tournaments.models import Tournament

class Command(BaseCommand):
    help = 'Syncs tournament status based on dates and match completion'

    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()

        # ACCEPTING_APPLICATIONS -> APPLICATIONS_CLOSED
        closed = Tournament.objects.filter(
            status='ACCEPTING_APPLICATIONS', application_deadline__lt=now
        ).update(status='APPLICATIONS_CLOSED')

        # UPCOMING/APPLICATIONS_CLOSED -> ONGOING (start_date reached)
        started = Tournament.objects.filter(
            status__in=['UPCOMING', 'APPLICATIONS_CLOSED'], start_date__lte=today
        ).update(status='ONGOING')

        # ONGOING -> COMPLETED (end_date passed AND all matches completed)
        ongoing = Tournament.objects.filter(status='ONGOING', end_date__lt=today)
        completed_count = 0
        for t in ongoing:
            if not t.matches.exclude(status='COMPLETED').exists():
                t.status = 'COMPLETED'
                t.save(update_fields=['status'])
                completed_count += 1

        self.stdout.write(f'Closed: {closed}, Started: {started}, Completed: {completed_count}')