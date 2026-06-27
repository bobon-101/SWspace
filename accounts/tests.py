from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()

VALID_STUDENT_CODE = 'SW127'   # maps to ม.1
COMMITTEE_CODE = 'COMMITTEE2024'
VALID_EMAIL = 'test@satriwit.ac.th'
PASSWORD = 'Test123!'


def _post_register(client, **overrides):
    data = {
        'full_name': 'ทดสอบ ทดสอบ',
        'email': VALID_EMAIL,
        'password': PASSWORD,
        'confirm_password': PASSWORD,
        'verification_code': VALID_STUDENT_CODE,
    }
    data.update(overrides)
    return client.post(reverse('accounts:register'), data)


class RegisterTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_student_registration_succeeds(self):
        resp = _post_register(self.client)
        self.assertRedirects(resp, reverse('portal:dashboard'))
        user = User.objects.get(email=VALID_EMAIL)
        self.assertEqual(user.role, 'student')

    def test_student_grade_level_assigned(self):
        _post_register(self.client, verification_code='SW127')
        self.assertEqual(User.objects.get(email=VALID_EMAIL).grade_level, 'ม.1')

    def test_all_grade_codes_map_correctly(self):
        grade_map = {
            'SW127': 'ม.1',
            'SW126': 'ม.2',
            'SW125': 'ม.3',
            'SW124': 'ม.4',
            'SW123': 'ม.5',
            'SW122': 'ม.6',
        }
        for i, (code, grade) in enumerate(grade_map.items()):
            email = f'student{i}@satriwit.ac.th'
            _post_register(Client(), email=email, verification_code=code)
            self.assertEqual(User.objects.get(email=email).grade_level, grade)

    def test_committee_registration_sets_role(self):
        _post_register(self.client, verification_code=COMMITTEE_CODE)
        user = User.objects.get(email=VALID_EMAIL)
        self.assertEqual(user.role, 'committee')
        self.assertTrue(user.is_committee())

    def test_committee_grade_level_empty(self):
        _post_register(self.client, verification_code=COMMITTEE_CODE)
        self.assertEqual(User.objects.get(email=VALID_EMAIL).grade_level, '')

    def test_invalid_verification_code_rejected(self):
        resp = _post_register(self.client, verification_code='WRONG')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(email=VALID_EMAIL).exists())

    def test_non_school_email_rejected(self):
        resp = _post_register(self.client, email='test@gmail.com')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(email='test@gmail.com').exists())

    def test_duplicate_email_rejected(self):
        _post_register(self.client)
        resp = _post_register(Client(), email=VALID_EMAIL)  # fresh unauthenticated client
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(User.objects.filter(email=VALID_EMAIL).count(), 1)

    def test_password_mismatch_rejected(self):
        resp = _post_register(self.client, confirm_password='DifferentPass1!')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(email=VALID_EMAIL).exists())

    def test_authenticated_user_redirected_from_register(self):
        _post_register(self.client)
        resp = self.client.get(reverse('accounts:register'))
        self.assertRedirects(resp, reverse('portal:dashboard'))


class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email=VALID_EMAIL,
            password=PASSWORD,
            full_name='ทดสอบ',
            role='student',
        )

    def test_login_with_correct_credentials(self):
        resp = self.client.post(reverse('accounts:login'), {
            'username': VALID_EMAIL,
            'password': PASSWORD,
        })
        self.assertRedirects(resp, reverse('portal:dashboard'))

    def test_login_with_wrong_password(self):
        resp = self.client.post(reverse('accounts:login'), {
            'username': VALID_EMAIL,
            'password': 'wrongpass',
        })
        self.assertEqual(resp.status_code, 200)

    def test_login_with_unknown_email(self):
        resp = self.client.post(reverse('accounts:login'), {
            'username': 'nobody@satriwit.ac.th',
            'password': PASSWORD,
        })
        self.assertEqual(resp.status_code, 200)

    def test_authenticated_user_redirected_from_login(self):
        self.client.login(username=VALID_EMAIL, password=PASSWORD)
        resp = self.client.get(reverse('accounts:login'))
        self.assertRedirects(resp, reverse('portal:dashboard'))

    def test_safe_next_redirect_followed(self):
        resp = self.client.post(
            reverse('accounts:login') + '?next=/dashboard/',
            {'username': VALID_EMAIL, 'password': PASSWORD},
        )
        self.assertRedirects(resp, '/dashboard/', fetch_redirect_response=False)

    def test_unsafe_next_redirect_ignored(self):
        resp = self.client.post(
            reverse('accounts:login') + '?next=https://evil.com/steal',
            {'username': VALID_EMAIL, 'password': PASSWORD},
        )
        self.assertRedirects(resp, reverse('portal:dashboard'))


class LogoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(
            email=VALID_EMAIL, password=PASSWORD, full_name='ทดสอบ', role='student'
        )
        self.client.login(username=VALID_EMAIL, password=PASSWORD)

    def test_post_logout_redirects_to_login(self):
        resp = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(resp, reverse('accounts:login'))

    def test_get_logout_redirects_to_dashboard(self):
        resp = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(resp, reverse('portal:dashboard'))
