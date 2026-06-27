# SWspace — ระบบเว็บไซต์กลางสำหรับนักเรียนสตรีวิทยา

ระบบศูนย์กลางข้อมูลสำหรับนักเรียนโรงเรียนสตรีวิทยา ครอบคลุมฟีเจอร์ข่าวสาร, จิตอาสา, การแข่งขัน, แชร์สรุป, แจ้งปัญหา และระบบสะสมแต้ม สร้างด้วย Django 4.2 มี 2 roles คือ student และ committee

---

## Tech Stack

| ส่วน | เทคโนโลยี |
|------|-----------|
| Backend | Django 4.2, Python |
| Database | SQLite (local dev) |
| Auth | Custom AbstractUser (email เป็น login field) |
| Frontend | Bootstrap 5 (CDN), custom CSS |
| Image processing | Pillow |
| Media storage | Local filesystem (`media/`) |
| Env config | python-dotenv |

---

## วิธีรันโปรเจกต์ (How to Run Locally)

### 1. ติดตั้ง dependencies

```bash
pip install -r requirements.txt
```

### 2. สร้างฐานข้อมูล

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. สร้างบัญชีทดสอบ

```bash
python manage.py create_test_accounts
```

คำสั่งนี้สร้างบัญชีทดสอบสำเร็จรูปสำหรับ student และ committee (idempotent — รันซ้ำได้ปลอดภัย)

### 4. รันเซิร์ฟเวอร์

```bash
python manage.py runserver
```

เปิดเบราว์เซอร์ที่ http://127.0.0.1:8000/

---

ถ้า server ค้างบน Windows ให้รัน:

```powershell
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
Stop-Process -Id <PID> -Force
```

---

## บัญชีทดสอบ (Test Accounts)

สร้างด้วย `python manage.py create_test_accounts`

| Role | Email | Password |
|------|-------|----------|
| student | student.test@satriwit.ac.th | Student1234! |
| committee | committee.test@satriwit.ac.th | Committee1234! |

> **หมายเหตุ:** รหัสผ่านเหล่านี้สำหรับทดสอบ local เท่านั้น อย่าใช้ใน production

---

## รหัสยืนยันตัวตน (Verification Codes)

ใช้ตอนสมัครสมาชิกที่ `/accounts/register/`

| รหัส | Role | ระดับชั้น |
|------|------|-----------|
| `SW127` | student | ม.1 |
| `SW126` | student | ม.2 |
| `SW125` | student | ม.3 |
| `SW124` | student | ม.4 |
| `SW123` | student | ม.5 |
| `SW122` | student | ม.6 |

รหัสสำหรับ committee role — ผู้ดูแลระบบจะแจ้งแยกต่างหาก

---

## ฟีเจอร์ทั้งหมด (Feature List)

| ฟีเจอร์ | ผู้ใช้ | คำอธิบาย |
|---------|--------|----------|
| ข่าวสาร | ทุกคน (อ่าน) / committee (จัดการ) | ข่าวภายใน, ข่าวภายนอก, ประชาสัมพันธ์ |
| จิตอาสา | ทุกคน (อ่าน) / committee (จัดการ) | ลิงก์กิจกรรมพร้อม deadline |
| การแข่งขัน | ทุกคน (อ่าน) / committee (จัดการ) | โพสต์การแข่งขันพร้อมรูปและลิงก์ |
| แชร์สรุป | นักเรียน (โพสต์ / อ่าน) / committee (ลบ) | แชร์ลิงก์ Google Drive |
| แจ้งปัญหา | นักเรียน (โพสต์) / committee (จัดการ) | สถานะ pending / approved / rejected |
| สะสมแต้ม | นักเรียน (ส่งหลักฐาน) / committee (อนุมัติ/ปฏิเสธ) | ส่งภาพหลักฐาน, ตรวจสอบแต้มสะสม |
| Committee Dashboard | committee only | จัดการทุกฟีเจอร์ข้างต้น |
| Django Admin | is_staff only | จัดการฐานข้อมูลทั้งหมด |

---

## Tester Checklist

ตรวจสอบ flow หลักตามลำดับ:

**บัญชีและการเข้าสู่ระบบ**
- [ ] สมัครสมาชิกด้วยรหัส student ทุก 6 ระดับ — ตรวจว่า grade_level ถูกต้อง
- [ ] สมัครด้วยรหัสผิด — ต้องไม่ผ่าน
- [ ] สมัครด้วย email ที่ไม่ใช่ @satriwit.ac.th — ต้องไม่ผ่าน
- [ ] login สำเร็จ → redirect ไป /dashboard/
- [ ] logout → redirect ไป /accounts/login/

**Student**
- [ ] อ่านข่าวสาร, จิตอาสา, การแข่งขัน ได้
- [ ] โพสต์สรุปการเรียนด้วย Google Drive URL
- [ ] แจ้งปัญหา (ต้องมีรายละเอียด ≥ 10 ตัวอักษร)
- [ ] ส่งหลักฐานสะสมแต้ม (JPG/PNG/WEBP, ≤5MB)
- [ ] ส่งซ้ำกิจกรรมที่ pending อยู่ — ต้องถูกบล็อก
- [ ] ส่งซ้ำกิจกรรมที่ approved แล้ว — ต้องถูกบล็อก
- [ ] ส่งซ้ำกิจกรรมที่ rejected — ต้องทำได้
- [ ] เข้า /committee/ — ต้องถูก redirect (ไม่ใช่ 403)

**Committee**
- [ ] เข้า /committee/ ได้ และเห็น dashboard
- [ ] สร้าง / แก้ไข / ลบ ข่าวสาร
- [ ] สร้างข่าวพร้อมรูป JPG/PNG/WEBP — ต้องผ่าน
- [ ] อัปโหลดไฟล์ประเภทอื่น (เช่น .exe, .pdf) — ต้องถูกบล็อก
- [ ] อัปโหลดรูปขนาด >5MB — ต้องถูกบล็อก
- [ ] จัดการจิตอาสา, การแข่งขัน, แจ้งปัญหา
- [ ] อนุมัติหลักฐานแต้ม — แต้มนักเรียนเพิ่ม
- [ ] อนุมัติซ้ำ — แต้มต้องไม่บวกเพิ่ม
- [ ] ปฏิเสธ submission ที่ approved แล้ว — ต้องถูกบล็อก

---

## Known Limitations / ข้อจำกัดที่ทราบ

- **Media URL access:** ไฟล์ใน `media/` ถูก serve โดยตรง — ใครก็ตามที่ทราบ URL สามารถเปิดได้ (ไม่มี per-file ACL) เป็นข้อจำกัดของ local dev setup; ใน production ควรใช้ signed URL หรือ private bucket
- **Footer IG link:** `href="#"` เป็น placeholder — ยังไม่มี URL จริง
- **SQLite:** ใช้สำหรับ local dev เท่านั้น; deployment จริงควรเปลี่ยนเป็น PostgreSQL ผ่าน `DATABASE_URL`
- **UI flow testing:** ฟีเจอร์ทั้งหมดถูกตรวจสอบผ่าน code-reading และ automated test suite (38 tests) — ไม่ได้ผ่าน live browser session

---

## Local Media Storage

รูปภาพที่อัปโหลดจะถูกเก็บใน `media/` ซึ่ง `.gitignore` จะไม่ commit ไป repository

```
MEDIA_URL  = /media/
MEDIA_ROOT = <project_root>/media/
```

Django serve media files อัตโนมัติเมื่อ `DEBUG=True` ผ่าน `urlpatterns += static(...)` ใน `config/urls.py`

> ใน production (`DEBUG=False`) ต้องจัดการ serve media แยกต่างหาก (nginx หรือ cloud storage)

---

## การรัน Tests

```bash
# รันทุก test
python manage.py test

# รัน test เฉพาะ app
python manage.py test accounts
python manage.py test portal
```

### สิ่งที่ครอบคลุมใน test suite (38 tests)

| Class | จำนวน | สิ่งที่ทดสอบ |
|-------|--------|--------------|
| `RegisterTest` | 10 | สมัครสมาชิก, mapping รหัส grade ทั้ง 6, role committee, รหัสผิด, email ไม่ใช่ school, email ซ้ำ, password ไม่ตรง, redirect เมื่อ login อยู่แล้ว |
| `LoginTest` | 6 | login สำเร็จ, password ผิด, email ไม่มี, redirect เมื่อ login อยู่แล้ว, safe `?next=` ตาม, unsafe `?next=` ถูก block |
| `LogoutTest` | 2 | POST logout ไป login, GET ไป dashboard |
| `ImageUploadTest` | 9 | committee อัปโหลดรูป News/Competition ได้, นักเรียนถูกบล็อก, form render |
| `ImageValidationTest` | 2 | server-side reject wrong content-type, reject oversized file |
| `PointsTest` | 9 | ส่งหลักฐาน, อนุมัติ, อนุมัติซ้ำไม่บวกแต้ม, ปฏิเสธ, ปฏิเสธ approved ถูกบล็อก, rejected อนุญาตส่งซ้ำ |

---

## การ Archive รูปภาพเก่า

ระบบมี management command สำหรับบีบอัดรูปภาพที่เก่าเกิน N เดือน (ค่า default: 3 เดือน) เพื่อลด storage

**ผลลัพธ์:** รูปถูกแทนที่ด้วยเวอร์ชัน JPEG ความละเอียดไม่เกิน 800px, quality 75 ยังดูได้และค้นหาจาก DB ได้ปกติ

```bash
# ดูจำนวน record ที่จะถูก archive โดยไม่แก้ไขอะไร
python manage.py archive_old_media --dry-run

# รัน archive จริง
python manage.py archive_old_media
```

**ตั้งค่า threshold ผ่าน environment variable:**

```bash
# .env
ARCHIVE_AFTER_MONTHS=6   # เปลี่ยนเป็น 6 เดือน (default คือ 3)
```

Model ที่ถูก archive: `News.image`, `Competition.image`, `PointSubmission.proof_image`

> **Cloudinary:** เมื่อ `CLOUDINARY_CLOUD_NAME` ถูกตั้งไว้ คำสั่งจะ re-upload รูปบีบอัดทับ public_id เดิมและติด tag `archived`

---

## URL Routes

| URL | หน้า | สิทธิ์ |
|-----|------|--------|
| `/accounts/login/` | เข้าสู่ระบบ | ทุกคน |
| `/accounts/register/` | สมัครสมาชิก | ทุกคน |
| `/accounts/logout/` | ออกจากระบบ (POST) | login |
| `/dashboard/` | หน้าหลัก | login |
| `/news/` | ข่าวสาร | login |
| `/volunteer/` | จิตอาสา | login |
| `/competitions/` | การแข่งขัน | login |
| `/study-notes/` | แชร์สรุป | login |
| `/problem-reports/` | แจ้งปัญหา | login |
| `/points/` | สะสมแต้ม | login |
| `/committee/` | Committee Dashboard | committee only |
| `/admin/` | Django Admin | is_staff only |

---

## โครงสร้างโปรเจกต์

```
SW Website/
├── config/          # Django settings & root URLs
├── accounts/        # Custom user model, auth views, forms, tests
├── portal/          # Feature models, views, forms, tests
│   └── management/
│       └── commands/
│           ├── archive_old_media.py
│           └── create_test_accounts.py
├── templates/
│   ├── base.html
│   ├── accounts/    # login.html, register.html
│   └── portal/      # dashboard, news, volunteer, competitions,
│                    # study_notes, problem_reports, committee/* , points
├── static/
├── media/           # uploaded files (gitignored)
├── manage.py
└── requirements.txt
```

---

## Deploy Notes

เมื่อ deploy ไป production:

1. **ต้องตั้ง environment variables ทุกตัวต่อไปนี้ — อย่าพึ่ง fallback ใน code:**

   | Variable | ค่าที่ต้องตั้ง |
   |----------|--------------|
   | `SECRET_KEY` | random string ≥ 50 ตัวอักษร |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | domain จริง เช่น `mysite.com` |
   | `COMMITTEE_VERIFICATION_CODE` | รหัสใหม่ที่ไม่ใช่ค่า default |
   | `DATABASE_URL` | PostgreSQL connection string |

2. **รัน migrations บน production DB:**
   ```bash
   python manage.py migrate
   ```

3. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

4. **Media files:** ใน production ต้องใช้ cloud storage หรือ nginx serve แทน Django (DEBUG=False จะไม่ serve `/media/` อัตโนมัติ)

5. **psycopg2-binary** ใน requirements.txt ใช้กับ PostgreSQL — ไม่มีผลกับ SQLite local dev
