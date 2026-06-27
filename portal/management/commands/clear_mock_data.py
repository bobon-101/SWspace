from django.core.management.base import BaseCommand

from portal.models import (
    Competition, News, PointActivity, PointSubmission,
    ProblemReport, StudyNote, UserPointProfile, VolunteerLink,
)


def _delete_file(field):
    if field:
        try:
            field.delete(save=False)
        except Exception:
            pass


class Command(BaseCommand):
    help = 'Delete all portal content and reset point totals. User accounts are kept.'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true', help='Skip confirmation prompt')

    def handle(self, *args, **options):
        counts = {
            'News': News.objects.count(),
            'VolunteerLink': VolunteerLink.objects.count(),
            'Competition': Competition.objects.count(),
            'StudyNote': StudyNote.objects.count(),
            'ProblemReport': ProblemReport.objects.count(),
            'PointSubmission': PointSubmission.objects.count(),
            'PointActivity': PointActivity.objects.count(),
            'UserPointProfile': UserPointProfile.objects.count(),
        }
        total = sum(counts.values())

        if total == 0:
            self.stdout.write('Nothing to delete.')
            return

        for model, count in counts.items():
            self.stdout.write(f'  {model}: {count}')

        if not options['yes']:
            confirm = input(f'\nDelete all {total} records? [y/N] ')
            if confirm.strip().lower() != 'y':
                self.stdout.write('Cancelled.')
                return

        # Delete media files before removing DB records
        for obj in PointSubmission.objects.all():
            _delete_file(obj.proof_image)
        for obj in News.objects.all():
            _delete_file(obj.image)
        for obj in Competition.objects.all():
            _delete_file(obj.image)

        # Delete in FK-safe order
        UserPointProfile.objects.all().delete()
        PointSubmission.objects.all().delete()
        PointActivity.objects.all().delete()
        ProblemReport.objects.all().delete()
        StudyNote.objects.all().delete()
        Competition.objects.all().delete()
        VolunteerLink.objects.all().delete()
        News.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f'Deleted {total} records. User accounts untouched.'))
