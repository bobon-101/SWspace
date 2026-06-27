import calendar
import io
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from portal.models import Competition, News, PointSubmission

ARCHIVE_MAX_DIMENSION = 800
ARCHIVE_JPEG_QUALITY = 75


def _subtract_months(dt, months):
    idx = dt.month - 1 - months
    year = dt.year + idx // 12
    month = idx % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def _compress(image_field):
    from PIL import Image
    image_field.open('rb')
    img = Image.open(image_field)
    img.load()
    image_field.close()
    if img.mode in ('RGBA', 'P', 'LA'):
        img = img.convert('RGB')
    w, h = img.size
    if max(w, h) > ARCHIVE_MAX_DIMENSION:
        scale = ARCHIVE_MAX_DIMENSION / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=ARCHIVE_JPEG_QUALITY, optimize=True)
    return buf.getvalue()


def _save_local(image_field, data):
    path = os.path.join(settings.MEDIA_ROOT, image_field.name)
    with open(path, 'wb') as fh:
        fh.write(data)


def _save_cloudinary(image_field, data):
    import cloudinary.uploader
    public_id = os.path.splitext(image_field.name)[0]
    cloudinary.uploader.upload(
        io.BytesIO(data),
        public_id=public_id,
        overwrite=True,
        resource_type='image',
        tags=['archived'],
    )


class Command(BaseCommand):
    help = 'Replace images older than ARCHIVE_AFTER_MONTHS with compressed versions.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')

    def handle(self, *args, **options):
        months = getattr(settings, 'ARCHIVE_AFTER_MONTHS', 3)
        cutoff = _subtract_months(timezone.now(), months)
        dry_run = options['dry_run']
        use_cloudinary = bool(getattr(settings, 'CLOUDINARY_STORAGE', {}).get('CLOUD_NAME'))

        self.stdout.write(f'Archive threshold: {months} months (cutoff: {cutoff.date()})')
        if dry_run:
            self.stdout.write('DRY RUN — no changes will be made')

        specs = [
            (News, 'image'),
            (Competition, 'image'),
            (PointSubmission, 'proof_image'),
        ]

        total = 0
        for Model, field_name in specs:
            qs = Model.objects.filter(created_at__lt=cutoff, is_archived=False)
            candidates = [obj for obj in qs.iterator() if getattr(obj, field_name)]
            self.stdout.write(f'{Model.__name__}: {len(candidates)} record(s) to archive')

            if dry_run:
                total += len(candidates)
                continue

            ok = 0
            for obj in candidates:
                field = getattr(obj, field_name)
                try:
                    data = _compress(field)
                    if use_cloudinary:
                        _save_cloudinary(field, data)
                    else:
                        _save_local(field, data)
                    obj.is_archived = True
                    obj.save(update_fields=['is_archived'])
                    ok += 1
                except Exception as exc:
                    self.stderr.write(f'  [{Model.__name__} id={obj.pk}] {exc}')

            self.stdout.write(f'  Done: {ok}/{len(candidates)}')
            total += ok

        suffix = 'would be archived' if dry_run else 'archived'
        if dry_run:
            self.stdout.write(self.style.WARNING(f'Total: {total} record(s) {suffix}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Total: {total} record(s) {suffix}'))
