from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

_STUDENT_EMAIL = 'student.test@satriwit.ac.th'
_STUDENT_PASSWORD = 'Student1234!'
_COMMITTEE_EMAIL = 'committee.test@satriwit.ac.th'
_COMMITTEE_PASSWORD = 'Committee1234!'


class Command(BaseCommand):
    help = 'Create default test accounts for local development and UAT (idempotent).'

    def handle(self, *args, **options):
        student, created = User.objects.get_or_create(
            email=_STUDENT_EMAIL,
            defaults={
                'full_name': 'นักเรียนทดสอบ',
                'role': 'student',
                'grade_level': 'ม.5',
            },
        )
        if created:
            student.set_password(_STUDENT_PASSWORD)
            student.save()
            self.stdout.write(self.style.SUCCESS(f'Created  student:   {_STUDENT_EMAIL}'))
        else:
            self.stdout.write(f'Exists   student:   {_STUDENT_EMAIL}')

        committee, created = User.objects.get_or_create(
            email=_COMMITTEE_EMAIL,
            defaults={
                'full_name': 'กรรมการทดสอบ',
                'role': 'committee',
                'is_staff': True,
            },
        )
        if created:
            committee.set_password(_COMMITTEE_PASSWORD)
            committee.save()
            self.stdout.write(self.style.SUCCESS(f'Created  committee: {_COMMITTEE_EMAIL}'))
        else:
            self.stdout.write(f'Exists   committee: {_COMMITTEE_EMAIL}')

        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write(f'  Student:   {_STUDENT_EMAIL}  /  {_STUDENT_PASSWORD}')
        self.stdout.write(f'  Committee: {_COMMITTEE_EMAIL}  /  {_COMMITTEE_PASSWORD}')
        self.stdout.write(self.style.WARNING('For local testing only — do not use in production.'))
