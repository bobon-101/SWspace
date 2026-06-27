from datetime import timedelta
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from portal.models import (
    Competition, News, PointActivity, PointSubmission,
    ProblemReport, StudyNote, UserPointProfile, VolunteerLink,
)

User = get_user_model()
_STUDENT_EMAIL = 'student.test@satriwit.ac.th'
_COMMITTEE_EMAIL = 'committee.test@satriwit.ac.th'


def _image_file(name, color=(100, 149, 237)):
    from PIL import Image
    img = Image.new('RGB', (400, 300), color=color)
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return ContentFile(buf.getvalue(), name=name)


class Command(BaseCommand):
    help = 'Seed mock data for demo/presentation (idempotent).'

    def handle(self, *args, **options):
        now = timezone.now()

        try:
            committee = User.objects.get(email=_COMMITTEE_EMAIL)
            student = User.objects.get(email=_STUDENT_EMAIL)
        except User.DoesNotExist:
            self.stderr.write('Run "python manage.py create_test_accounts" first.')
            return

        # ── News ──────────────────────────────────────────────────────────────
        news_items = [
            ('กำหนดการสอบกลางภาคเรียนที่ 1/2567',
             'การสอบกลางภาคจะจัดขึ้นในวันที่ 15–19 กรกฎาคม 2567 '
             'นักเรียนทุกคนต้องเตรียมตัวให้พร้อมและนำบัตรนักเรียนมาด้วย',
             News.CATEGORY_INTERNAL),
            ('ทุนการศึกษา ก.พ. ปีการศึกษา 2567',
             'สำนักงาน ก.พ. เปิดรับสมัครทุนรัฐบาลสำหรับนักเรียนที่มีผลการเรียนดีเด่น '
             'GPA ไม่ต่ำกว่า 3.50 สนใจติดต่อฝ่ายวิชาการ',
             News.CATEGORY_EXTERNAL),
            ('ประชาสัมพันธ์ กิจกรรมวันภาษาไทยแห่งชาติ',
             'ขอเชิญนักเรียนทุกคนร่วมกิจกรรมวันภาษาไทยแห่งชาติ '
             'วันที่ 29 กรกฎาคม พบกับการประกวดกลอน เรียงความ และคัดลายมือ',
             News.CATEGORY_ANNOUNCEMENT),
        ]
        for title, desc, cat in news_items:
            News.objects.get_or_create(
                title=title,
                defaults=dict(description=desc, category=cat, is_published=True, created_by=committee),
            )
        self.stdout.write(f'News:          {len(news_items)} records')

        # ── VolunteerLink ─────────────────────────────────────────────────────
        volunteer_items = [
            ('ปลูกป่าชายเลนกับมูลนิธิสืบ นาคะเสถียร',
             'ร่วมปลูกป่าชายเลนเพื่ออนุรักษ์ธรรมชาติ รับจำนวนจำกัด 50 คน',
             'https://www.seub.or.th', 'มูลนิธิสืบ นาคะเสถียร',
             (now + timedelta(days=30)).date()),
            ('อาสาสมัครสอนน้องในชุมชน',
             'ช่วยสอนวิชาคณิตศาสตร์และภาษาอังกฤษให้นักเรียนในชุมชนรอบโรงเรียน ทุกวันเสาร์',
             'https://www.facebook.com', 'ชมรมจิตอาสาสตรีวิทยา',
             (now + timedelta(days=45)).date()),
        ]
        for title, desc, url, org, deadline in volunteer_items:
            VolunteerLink.objects.get_or_create(
                title=title,
                defaults=dict(
                    description=desc, external_url=url, organizer=org,
                    deadline=deadline, is_published=True, created_by=committee,
                ),
            )
        self.stdout.write(f'VolunteerLink: {len(volunteer_items)} records')

        # ── Competition ───────────────────────────────────────────────────────
        competition_items = [
            ('สัปดาห์วิทยาศาสตร์แห่งชาติ 2567',
             'การแสดงนิทรรศการและแข่งขันทักษะวิทยาศาสตร์ระดับมัธยมศึกษา '
             'เปิดรับทีมละ 3 คน ทุกระดับชั้น',
             'อพวช.', (now + timedelta(days=20)).date()),
            ('การแข่งขันคณิตศาสตร์เพชรยอดมงกุฎ ครั้งที่ 20',
             'แข่งขันคณิตศาสตร์ระดับประเทศ เหมาะสำหรับ ม.4–ม.6 ที่มีความสามารถพิเศษ '
             'รางวัลทุนการศึกษารวมกว่า 1 ล้านบาท',
             'มูลนิธิร่มฉัตร', (now + timedelta(days=60)).date()),
            ('TOT Young Coder 2567',
             'แข่งขันเขียนโปรแกรมสำหรับนักเรียนมัธยมศึกษา ภาษา Python / C++ '
             'ชนะเลิศได้ทุนการศึกษาและโล่รางวัล',
             'บริษัท ทีโอที จำกัด (มหาชน)', (now + timedelta(days=15)).date()),
        ]
        for title, desc, org, deadline in competition_items:
            Competition.objects.get_or_create(
                title=title,
                defaults=dict(
                    description=desc, organizer=org, deadline=deadline,
                    is_published=True, created_by=committee,
                ),
            )
        self.stdout.write(f'Competition:   {len(competition_items)} records')

        # ── StudyNote ─────────────────────────────────────────────────────────
        note_items = [
            ('สรุปแคลคูลัส บทที่ 1–3', 'ม.5', 'คณิตศาสตร์',
             'https://drive.google.com/file/d/mock_calc', 'น้องมิ้นท์'),
            ('ไฟฟ้าและแม่เหล็ก ฉบับสมบูรณ์', 'ม.6', 'ฟิสิกส์',
             'https://drive.google.com/file/d/mock_phys', ''),
            ('ตารางธาตุ + สมการเคมีพื้นฐาน', 'ม.4', 'เคมี',
             'https://drive.google.com/file/d/mock_chem', 'น้องปลา'),
            ('Grammar ครบทุก Tense พร้อมตัวอย่าง', 'ม.5', 'ภาษาอังกฤษ',
             'https://drive.google.com/file/d/mock_eng', ''),
        ]
        for title, grade, subj, url, credit in note_items:
            StudyNote.objects.get_or_create(
                title=title,
                defaults=dict(
                    grade_level=grade, subject=subj, drive_url=url,
                    credit_name=credit, is_approved=True, submitted_by=student,
                ),
            )
        self.stdout.write(f'StudyNote:     {len(note_items)} records')

        # ── ProblemReport ─────────────────────────────────────────────────────
        report_items = [
            ('ไฟในห้องน้ำชั้น 3 อาคาร 1 ดับทั้งหมด',
             'ห้องน้ำชั้น 3 อาคาร 1 ไฟดับทุกดวงมาตั้งแต่วันจันทร์ ทำให้ใช้งานไม่ได้',
             'ห้องน้ำ อาคาร 1 ชั้น 3', ProblemReport.STATUS_PENDING, ''),
            ('โต๊ะเรียนในห้อง 305 ชำรุด 3 ตัว',
             'โต๊ะเรียนชำรุด ขาหัก 3 ตัว นักเรียนต้องนั่งพื้น กรุณาซ่อมด่วน',
             'ห้อง 305 อาคาร 3', ProblemReport.STATUS_APPROVED,
             'รับเรื่องแล้ว อยู่ระหว่างการจัดซื้อโต๊ะใหม่ คาดว่าจะแล้วเสร็จภายใน 2 สัปดาห์'),
            ('ระบบ Wi-Fi อาคาร 2 ช้ามากในชั่วโมงพัก',
             'ช่วงพักกลางวัน Wi-Fi อาคาร 2 ช้ามากจนใช้งานไม่ได้เลย ขอให้ตรวจสอบด้วย',
             'อาคาร 2 ทุกชั้น', ProblemReport.STATUS_REJECTED,
             'Wi-Fi เป็นระบบของทางโรงเรียนโดยตรง กรุณาติดต่อฝ่ายเทคโนโลยีสารสนเทศแทน'),
        ]
        for title, desc, loc, status, note in report_items:
            ProblemReport.objects.get_or_create(
                title=title,
                defaults=dict(
                    description=desc, location=loc,
                    status=status, admin_note=note, submitted_by=student,
                ),
            )
        self.stdout.write(f'ProblemReport: {len(report_items)} records')

        # ── PointActivity ─────────────────────────────────────────────────────
        activity_data = [
            ('เข้าร่วมกิจกรรมกีฬาสี 2567',
             'นักเรียนที่เข้าร่วมกิจกรรมกีฬาสีครบทุกวันจะได้รับแต้ม', 50),
            ('อาสาสมัครงานวันเด็ก',
             'ช่วยจัดงานวันเด็กให้น้องๆ ในชุมชนใกล้โรงเรียน', 30),
            ('ส่งสรุปวิชาเพื่อน้อง',
             'อัปโหลดสรุปวิชาคุณภาพเข้าระบบเพื่อแชร์ให้เพื่อนและน้อง', 20),
        ]
        activities = []
        for title, desc, pts in activity_data:
            act, _ = PointActivity.objects.get_or_create(
                title=title,
                defaults=dict(description=desc, points=pts, is_active=True, created_by=committee),
            )
            activities.append(act)
        self.stdout.write(f'PointActivity: {len(activity_data)} records')

        # ── PointSubmission ───────────────────────────────────────────────────
        sub_approved, created_approved = PointSubmission.objects.get_or_create(
            submitted_by=student,
            activity=activities[0],
            defaults=dict(
                status=PointSubmission.STATUS_APPROVED,
                admin_note='หลักฐานชัดเจน อนุมัติ',
                approved_by=committee,
                approved_at=now,
                proof_image=_image_file('mock_proof_approved.jpg', (76, 175, 80)),
            ),
        )
        sub_pending, _ = PointSubmission.objects.get_or_create(
            submitted_by=student,
            activity=activities[2],
            defaults=dict(
                status=PointSubmission.STATUS_PENDING,
                proof_image=_image_file('mock_proof_pending.jpg', (255, 152, 0)),
            ),
        )
        self.stdout.write('PointSubmission: 2 records (1 approved, 1 pending)')

        # ── UserPointProfile ──────────────────────────────────────────────────
        profile, _ = UserPointProfile.objects.get_or_create(user=student)
        if created_approved and profile.total_points == 0:
            profile.total_points = activities[0].points
            profile.save()
        self.stdout.write(f'UserPointProfile: {profile.total_points} points (student)')

        self.stdout.write(self.style.SUCCESS('Mock data seeded successfully.'))
