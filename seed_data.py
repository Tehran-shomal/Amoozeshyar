import os
import django
import random
from datetime import date, datetime

# تنظیمات جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.core.models import (
    Constant, Person, Teacher, Student, Lesson, Term, Payment, Exam,
    LessonGroups, ParkingPasses, Role, UserAccount, Prerequisite,
    Classroom, CourseOffering, Enrollment, Grade, GradeAppeal,
    Attendance, TicketCategory, Ticket, OnlineClass, TuitionReceipt,
    RefundRequest, StudentServiceRequest, ScholarshipApplication,
    CounselingAppointment, Proposal, TransferRequest, GraduationAudit,
    EducationalChangeLog, Curriculum, Communication, SystemSetting,
    CreditTransferRequest, InternshipRequest, ThesisProgressReport,
    Notification, TeacherSurvey, Internship, Faculty, Department, Field
)

def run():
    print("⏳ شروع ساخت دیتابیس جامع و واقعی...")

    # ۱. مقادیر ثابت (Constants)
    constants_data = [
        ("gender", "male", "مرد"), ("gender", "female", "زن"),
        ("language", "fa", "فارسی"), ("language", "en", "انگلیسی"),
        ("academic_rank", "instructor", "مربی"), ("academic_rank", "assistant", "استادیار"),
        ("academic_rank", "associate", "دانشیار"), ("academic_rank", "full", "استاد"),
        ("educational_level", "bachelor", "کارشناسی"), ("educational_level", "master", "ارشد"),
        ("student_status", "active", "فعال"), ("student_status", "probation", "مشروط"), ("student_status", "graduated", "فارغ‌التحصیل"),
        ("admission_type", "national", "کنکور"), ("admission_type", "quota", "سهمیه"),
        ("lesson_type", "theoretical", "نظری"), ("lesson_type", "practical", "عملی"), ("lesson_type", "combined", "نظری-عملی"),
        ("semester", "first", "نیمسال اول"), ("semester", "second", "نیمسال دوم"), ("semester", "summer", "تابستان"),
        ("exam_type", "midterm", "میان‌ترم"), ("exam_type", "final", "پایان‌ترم"),
        ("day_of_week", "saturday", "شنبه"), ("day_of_week", "sunday", "یکشنبه"),
        ("day_of_week", "monday", "دوشنبه"), ("day_of_week", "tuesday", "سه‌شنبه"),
        ("day_of_week", "wednesday", "چهارشنبه"), ("day_of_week", "thursday", "پنجشنبه"),
        ("prerequisite_type", "prerequisite", "پیش‌نیاز"), ("prerequisite_type", "corequisite", "هم‌نیاز"),
        ("appeal_status", "pending", "در انتظار"), ("appeal_status", "accepted", "پذیرفته"), ("appeal_status", "rejected", "رد شده"),
        ("attendance_status", "present", "حاضر"), ("attendance_status", "absent", "غایب"), ("attendance_status", "late", "تأخیر"),
        ("ticket_creator_role", "student", "دانشجو"), ("ticket_creator_role", "teacher", "استاد"),
        ("ticket_status", "open", "باز"), ("ticket_status", "in_progress", "در حال بررسی"), ("ticket_status", "closed", "بسته"),
        ("review_status", "pending", "در انتظار"), ("review_status", "approved", "تأیید"), ("review_status", "rejected", "رد"),
        ("service_request_type", "dorm", "خوابگاه"), ("service_request_type", "loan", "وام"), ("service_request_type", "certificate", "گواهی"),
        ("counseling_status", "pending", "در انتظار"), ("counseling_status", "done", "انجام شده"),
        ("proposal_status", "pending", "در انتظار"), ("proposal_status", "approved", "تأیید"),
        ("graduation_status", "eligible", "واجد شرایط"), ("graduation_status", "not_eligible", "فاقد شرایط"), ("graduation_status", "under_review", "در حال بررسی"),
        ("change_type", "grade_change", "تغییر نمره"), ("change_type", "course_delete", "حذف درس"),
        ("requirement_type", "mandatory", "اجباری"), ("requirement_type", "elective", "اختیاری"), ("requirement_type", "basic", "پایه"), ("requirement_type", "specialized", "تخصصی"),
        ("communication_type", "message", "پیام"), ("communication_type", "announcement", "اطلاعیه"),
        ("communication_status", "sent", "ارسال شده"), ("communication_status", "read", "خوانده شده"),
        ("data_type", "string", "متن"), ("data_type", "int", "عدد"), ("data_type", "bool", "بولی"),
        ("payment_status", "successful", "موفق"), ("payment_status", "failed", "ناموفق"),
        ("enrollment_status", "REGISTERED", "ثبت‌نام شده"), ("enrollment_status", "PASSED", "پاس شده"), ("enrollment_status", "DROPPED", "حذف شده"),
        ("enrollment_type", "NORMAL", "عادی"), ("enrollment_type", "GUEST", "مهمان"),
        ("thesis_review_status", "pending", "در انتظار"), ("thesis_review_status", "approved", "تأیید"),
        ("notification_type", "grade", "نمره"), ("notification_type", "system", "سیستمی"),
        ("internship_request_type", "letter", "نامه کارآموزی"), ("internship_request_type", "intro", "معرفی‌نامه"),
    ]
    for cat, code, label in constants_data:
        Constant.objects.get_or_create(category=cat, code=code, defaults={'label': label})
    print(" ۱. مقادیر ثابت (Constants) ساخته شدند.")

    # ۲. دانشکده‌ها، گروه‌ها و رشته‌ها
    faculties_data = ["دانشکده فنی و مهندسی", "دانشکده علوم پایه", "دانشکده علوم انسانی"]
    faculties = []
    for name in faculties_data:
        fac, _ = Faculty.objects.get_or_create(faculty_name=name, defaults={'faculty_code': f"F-{len(faculties)+1:02d}"})
        faculties.append(fac)

    departments_data = [
        (faculties[0], "مهندسی کامپیوتر"),
        (faculties[0], "مهندسی برق"),
        (faculties[0], "مهندسی مکانیک"),
        (faculties[1], "ریاضی"),
        (faculties[1], "فیزیک"),
        (faculties[2], "حسابداری"),
        (faculties[2], "مدیریت"),
    ]
    departments = []
    for fac, name in departments_data:
        dept, _ = Department.objects.get_or_create(faculty=fac, department_name=name, defaults={'department_code': f"D-{len(departments)+1:02d}"})
        departments.append(dept)

    fields_data = [
        (departments[0], "مهندسی نرم‌افزار", "FLD-CS"),
        (departments[0], "مهندسی فناوری اطلاعات", "FLD-IT"),
        (departments[1], "مهندسی برق", "FLD-EE"),
        (departments[2], "مهندسی مکانیک", "FLD-ME"),
        (departments[3], "ریاضی کاربردی", "FLD-MATH"),
        (departments[5], "حسابداری", "FLD-ACC"),
        (departments[6], "مدیریت بازرگانی", "FLD-MGT"),
    ]
    fields = []
    for dept, name, code in fields_data:
        fld, _ = Field.objects.get_or_create(department=dept, field_name=name, defaults={'field_code': code})
        fields.append(fld)
    print(" ۲. دانشکده‌ها، گروه‌ها و رشته‌ها ساخته شدند.")

    # ۳. نقش‌ها
    role_student, _ = Role.objects.get_or_create(role_name="دانشجو")
    role_teacher, _ = Role.objects.get_or_create(role_name="استاد")
    role_admin, _ = Role.objects.get_or_create(role_name="مدیر")

    # ۴. اساتید
    teachers = []
    teacher_names = ["علی رضایی", "مریم احمدی", "حسین کریمی", "زهرا موسوی", "محمد حسینی", 
                     "فاطمه صادقی", "رضا نوروزی", "سارا محمدی", "امیر تهرانی", "نازنین اکبری",
                     "بهرام قاسمی", "شیرین رحیمی", "کاوه نادری", "پریسا کیانی"]
    for i, fullname in enumerate(teacher_names):
        first, last = fullname.split()
        person, created = Person.objects.get_or_create(
            username=f"teacher{i+1}",
            defaults={
                'first_name': first, 'last_name': last, 'email': f"teacher{i+1}@example.com",
                'national_id': f"11111111{i+1:02d}", 'birth_date': f"1975-01-{i%28+1:02d}", 'birth_place': "تهران",
                'gender': Constant.objects.get(category='gender', code='male' if i%2==0 else 'female'),
            }
        )
        if created: person.set_password("password123"); person.save()
        teacher, _ = Teacher.objects.get_or_create(
            person=person, defaults={
                'teacher_code': f"T-{1001+i}", 'department': departments[i % len(departments)],
                'academic_rank': Constant.objects.get(category='academic_rank', code=random.choice(['assistant', 'associate', 'full'])),
                'hire_date': f"20{10+i%10}-09-01",
            }
        )
        teachers.append(teacher)
        UserAccount.objects.get_or_create(person=person, role=role_teacher, defaults={'username': f"teacher{i+1}_acc", 'password': "hashed_password"})
    print(f" ۴. {len(teachers)} استاد ساخته شدند.")

    # ۵. دانشجویان
    students = []
    student_names = ["سارا احمدی", "رضا کریمی", "زهرا رضایی", "امیر حسینی", "مریم صادقی",
                     "علی نوروزی", "فاطمه محمدی", "حسین اکبری", "نازنین قاسمی", "بهرام رحیمی",
                     "پریسا نادری", "کاوه کیانی", "شیرین موسوی", "محمد تهرانی", "الهام شریفی",
                     "سعید مرادی", "نگار جعفری", "پویا اسدی", "هستی رستمی", "سینا صالحی"]
    for i, fullname in enumerate(student_names):
        first, last = fullname.split()
        fld = fields[i % len(fields)]
        person, created = Person.objects.get_or_create(
            username=f"student{i+1}",
            defaults={
                'first_name': first, 'last_name': last, 'email': f"student{i+1}@example.com",
                'national_id': f"22222222{i+1:02d}", 'birth_date': f"2000-05-{i%28+1:02d}", 'birth_place': "شیراز",
                'gender': Constant.objects.get(category='gender', code='male' if i%2==0 else 'female'),
            }
        )
        if created or not person.has_usable_password():
            person.set_password("password123")
            person.save(update_fields=["password"])
        student, _ = Student.objects.get_or_create(
            person=person, educational_level=Constant.objects.get(category='educational_level', code='bachelor'),
            defaults={
                'student_code': f"S-{2001+i}", 'field': fld, 'application_date': "2020-09-01",
                'status': Constant.objects.get(category='student_status', code='active'),
                'admission_type': Constant.objects.get(category='admission_type', code='national'),
                'previous_term_gpa': round(random.uniform(12.0, 20.0), 2),
                'total_gpa': round(random.uniform(12.0, 20.0), 2),
                'passed_units': random.randint(0, 100),
                'tuition_debt': random.choice([0, 500000, 1000000]),
                'completed_terms': random.randint(1, 6),
            }
        )
        students.append(student)
        UserAccount.objects.get_or_create(person=person, role=role_student, defaults={'username': f"student{i+1}_acc", 'password': "hashed_password"})
    print(f" ۵. {len(students)} دانشجو ساخته شدند.")

    # ۶. ترم تحصیلی
    term, _ = Term.objects.get_or_create(
        term_code="14051", defaults={
            'semester': Constant.objects.get(category='semester', code='first'),
            'academic_year': "1405-1406",
            'start_date': "2026-09-01", 'end_date': "2027-01-15",
            'registration_start': "2026-08-01 08:00", 'registration_end': "2026-08-10 20:00",
            'add_drop_start': "2026-09-05 08:00", 'add_drop_end': "2026-09-15 20:00",
            'emergency_drop_start': "2026-09-20 08:00", 'emergency_drop_end': "2026-09-25 20:00",
            'is_active': True,
        }
    )

    # ۷. درس‌ها
    lessons_data = [
        ("CS101", "مقدمات برنامه‌نویسی", 2, 2, departments[0]),
        ("CS102", "برنامه‌نویسی پیشرفته", 2, 2, departments[0]),
        ("CS201", "ساختمان داده‌ها", 1, 3, departments[0]),
        ("CS202", "الگوریتم‌ها", 0, 3, departments[0]),
        ("CS301", "پایگاه داده‌ها", 2, 2, departments[0]),
        ("CS302", "مهندسی نرم‌افزار", 0, 3, departments[0]),
        ("CS401", "شبکه‌های کامپیوتری", 1, 3, departments[0]),
        ("CS402", "هوش مصنوعی", 0, 3, departments[0]),
        ("CS403", "سیستم‌های عامل", 1, 3, departments[0]),
        ("MATH101", "ریاضی عمومی ۱", 0, 3, departments[3]),
        ("MATH102", "ریاضی عمومی ۲", 0, 3, departments[3]),
        ("MATH201", "ریاضیات گسسته", 0, 3, departments[3]),
        ("STAT101", "آمار و احتمال", 0, 3, departments[3]),
        ("PHY101", "فیزیک عمومی ۱", 1, 2, departments[4]),
        ("PHY102", "فیزیک عمومی ۲", 1, 2, departments[4]),
        ("EE101", "مدارهای الکتریکی ۱", 1, 2, departments[1]),
        ("EE102", "مدارهای الکتریکی ۲", 1, 2, departments[1]),
        ("ME101", "استاتیک", 0, 3, departments[2]),
        ("ME102", "دینامیک", 0, 3, departments[2]),
        ("ACC101", "اصول حسابداری ۱", 0, 3, departments[5]),
        ("ACC102", "اصول حسابداری ۲", 0, 3, departments[5]),
        ("MGT101", "اصول مدیریت", 0, 3, departments[6]),
        ("MGT102", "مدیریت رفتار سازمانی", 0, 3, departments[6]),
        ("GEN101", "زبان تخصصی", 0, 2, departments[0]),
        ("GEN102", "اندیشه اسلامی ۱", 0, 2, departments[0]),
    ]
    lessons = {}
    for code, title, practical, theory, dept in lessons_data:
        lesson, _ = Lesson.objects.get_or_create(
            lesson_code=code, defaults={
                'title': title, 'practical_units': practical, 'theory_units': theory,
                'lesson_type': Constant.objects.get(category='lesson_type', code='theoretical' if practical == 0 else 'combined'),
                'department': dept,
            }
        )
        lessons[code] = lesson
    print(f" ۷. {len(lessons)} درس واقعی ساخته شد.")

    # ۸. پیش‌نیازها
    prerequisites_data = [
        ("CS102", "CS101"), ("CS201", "CS102"), ("CS202", "CS201"),
        ("CS301", "CS201"), ("CS302", "CS201"), ("CS401", "CS202"), ("CS403", "CS202"),
        ("MATH102", "MATH101"), ("MATH201", "MATH102"),
        ("PHY102", "PHY101"),
        ("EE102", "EE101"),
    ]
    for main_code, prereq_code in prerequisites_data:
        Prerequisite.objects.get_or_create(
            lesson=lessons[main_code], prerequisite_lesson=lessons[prereq_code],
            defaults={'prerequisite_type': Constant.objects.get(category='prerequisite_type', code='prerequisite')}
        )
    print(f" ۸. {len(prerequisites_data)} پیش‌نیاز ساخته شد.")

    # ۹. چارت درسی
    curriculums_data = {
        "FLD-CS": [
            ("MATH101", 1, "mandatory"), ("CS101", 1, "mandatory"), ("PHY101", 1, "basic"),
            ("GEN101", 1, "mandatory"), ("GEN102", 1, "mandatory"),
            ("MATH102", 2, "mandatory"), ("CS102", 2, "mandatory"), ("PHY102", 2, "basic"),
            ("CS201", 3, "mandatory"), ("MATH201", 3, "basic"), ("STAT101", 3, "basic"),
            ("CS202", 4, "mandatory"), ("CS302", 4, "mandatory"),
            ("CS301", 5, "mandatory"), ("CS401", 5, "specialized"),
            ("CS402", 6, "specialized"), ("CS403", 6, "specialized"),
        ],
        "FLD-IT": [
            ("MATH101", 1, "mandatory"), ("CS101", 1, "mandatory"), ("GEN101", 1, "mandatory"),
            ("MATH102", 2, "mandatory"), ("CS102", 2, "mandatory"),
            ("CS201", 3, "mandatory"), ("CS401", 4, "mandatory"), ("CS301", 4, "mandatory"),
            ("CS302", 5, "specialized"), ("CS403", 6, "specialized"),
        ],
        "FLD-EE": [
            ("MATH101", 1, "mandatory"), ("PHY101", 1, "basic"), ("EE101", 1, "specialized"),
            ("MATH102", 2, "mandatory"), ("PHY102", 2, "basic"), ("EE102", 2, "specialized"),
            ("MATH201", 3, "basic"), ("STAT101", 4, "basic"),
        ],
        "FLD-ME": [
            ("MATH101", 1, "mandatory"), ("PHY101", 1, "basic"), ("ME101", 1, "specialized"),
            ("MATH102", 2, "mandatory"), ("PHY102", 2, "basic"), ("ME102", 2, "specialized"),
            ("MATH201", 3, "basic"), ("STAT101", 4, "basic"),
        ],
        "FLD-MATH": [
            ("MATH101", 1, "mandatory"), ("MATH102", 2, "mandatory"),
            ("MATH201", 3, "mandatory"), ("STAT101", 4, "mandatory"),
        ],
        "FLD-ACC": [
            ("ACC101", 1, "mandatory"), ("ACC102", 2, "mandatory"),
            ("MGT101", 3, "mandatory"), ("MGT102", 4, "mandatory"),
            ("STAT101", 5, "basic"),
        ],
        "FLD-MGT": [
            ("MGT101", 1, "mandatory"), ("MGT102", 2, "mandatory"),
            ("ACC101", 3, "basic"), ("STAT101", 4, "basic"),
        ],
    }
    for fld_code, items in curriculums_data.items():
        fld = Field.objects.get(field_code=fld_code)
        for lesson_code, term_num, req_type in items:
            Curriculum.objects.get_or_create(
                field=fld, lesson=lessons[lesson_code],
                defaults={
                    'recommended_term': term_num,
                    'calculated_units': lessons[lesson_code].practical_units + lessons[lesson_code].theory_units,
                    'requirement_type': Constant.objects.get(category='requirement_type', code=req_type),
                }
            )
    print(" ۹. چارت درسی برای تمام رشته‌ها ساخته شد.")

    # ۱۰. کلاس‌ها
    classrooms = []
    for i in range(1, 11):
        classroom, _ = Classroom.objects.get_or_create(
            building_name=f"ساختمان {chr(64+i)}", room_number=f"۱۰{i}", defaults={'capacity': random.choice([30, 40, 50]), 'classroom_type': random.choice(["کلاس درس", "آزمایشگاه", "کارگاه"])}
        )
        classrooms.append(classroom)

    # ۱۱. ارائه دروس
    offerings = []
    days = ['saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday']
    times = [("08:00", "10:00"), ("10:00", "12:00"), ("13:00", "15:00"), ("15:00", "17:00")]
    for i, lesson in enumerate(lessons.values()):
        offering, _ = CourseOffering.objects.get_or_create(
            lesson=lesson, term=term, teacher=teachers[i % len(teachers)], defaults={
                'capacity': random.choice([25, 30, 35, 40]),
                'day_of_week': Constant.objects.get(category='day_of_week', code=days[i % len(days)]),
                'start_time': times[i % len(times)][0], 'end_time': times[i % len(times)][1],
                'classroom': classrooms[i % len(classrooms)],
                'exam_date': "2027-01-20", 'exam_time': "09:00",
            }
        )
        offerings.append(offering)
    print(f" ۱۱. {len(offerings)} ارائه درس ساخته شد.")

    # ۱۲. انتخاب واحد، نمره و حضور و غیاب
    enrollment_count = 0
    for student in students:
        student_curriculum = Curriculum.objects.filter(field=student.field)[:4]
        for cur in student_curriculum:
            offering = next((o for o in offerings if o.lesson == cur.lesson), None)
            if offering:
                enroll, _ = Enrollment.objects.get_or_create(
                    student=student, offering=offering,
                    defaults={'status': Constant.objects.get(category='enrollment_status', code='REGISTERED'), 'enrollment_type': Constant.objects.get(category='enrollment_type', code='NORMAL')}
                )
                enrollment_count += 1
                if random.random() < 0.8:
                    Grade.objects.get_or_create(enrollment=enroll, defaults={'score': round(random.uniform(10.0, 20.0), 2)})
                for session in range(1, 4):
                    Attendance.objects.get_or_create(
                        enrollment=enroll, session_number=session, session_date=f"2026-10-{session+10:02d}",
                        defaults={
                            'attendance_status': Constant.objects.get(category='attendance_status', code=random.choice(['present', 'absent', 'late'])),
                            'attendance_time': "10:00", 'description': "ثبت شده", 
                            'recorded_by': enroll.student.person.user_accounts.first(),
                        }
                    )
    print(f" ۱۲. {enrollment_count} انتخاب واحد با نمره و حضور و غیاب ساخته شد.")

    # ۱۳. تیکت‌ها و مکاتبات
    ticket_cats = ["مشکلات آموزشی", "مشکلات مالی", "مشکلات ثبت‌نام", "درخواست گواهی"]
    for cat_name in ticket_cats:
        TicketCategory.objects.get_or_create(name=cat_name)
    
    subjects = ["مشکل در انتخاب واحد", "درخواست بررسی نمره", "خطا در پرداخت شهریه", "درخواست گواهی اشتغال به تحصیل",
                "مشکل در ورود به سیستم", "درخواست حذف اضطراری", "سؤال در مورد پیش‌نیازها"]
    for i in range(20):
        creator = random.choice(students).person
        Ticket.objects.get_or_create(
            creator=creator, category=random.choice(TicketCategory.objects.all()), 
            subject=random.choice(subjects),
            defaults={
                'content': f"متن تیکت شماره {i+1}: لطفاً بررسی بفرمایید.",
                'creator_role': Constant.objects.get(category='ticket_creator_role', code='student'),
                'status': Constant.objects.get(category='ticket_status', code=random.choice(['open', 'in_progress', 'closed'])),
                'assigned_to': random.choice(teachers).person,
            }
        )

    for i in range(20):
        sender = random.choice(students).person.user_accounts.first()
        receiver = random.choice(teachers).person.user_accounts.first()
        Communication.objects.get_or_create(
            sender=sender, receiver=receiver, subject=f"پیام شماره {i+1}",
            defaults={
                'message_body': f"متن پیام شماره {i+1}، با سلام و احترام...",
                'communication_type': Constant.objects.get(category='communication_type', code='message'),
                'status': Constant.objects.get(category='communication_status', code='sent'),
            }
        )
    print(" ۱۳. تیکت‌ها و مکاتبات ساخته شدند.")

    # ۱۴. پرداخت‌ها، تنظیمات و اعلان‌ها
    for i, student in enumerate(students):
        payment, _ = Payment.objects.get_or_create(
            term=term, student=student, tracking_code=f"PAY-{3001+i}",
            defaults={
                'amount': random.choice([2000000, 3000000, 4000000, 5000000]), 
                'payment_date': "2026-09-02 10:00",
                'status': Constant.objects.get(category='payment_status', code='successful'),
            }
        )
        TuitionReceipt.objects.get_or_create(
            receipt_serial_code=f"REC-{3001+i}", receipt_payment_link=payment, defaults={'receipt_document_uri': f"/media/receipts/{i}.pdf"}
        )

    SystemSetting.objects.get_or_create(setting_key="SITE_TITLE", defaults={'setting_value': "آموزشیار", 'data_type': Constant.objects.get(category='data_type', code='string'), 'description': "عنوان اصلی سایت"})
    SystemSetting.objects.get_or_create(setting_key="MAX_LOGIN_ATTEMPTS", defaults={'setting_value': "5", 'data_type': Constant.objects.get(category='data_type', code='int'), 'description': "حداکثر تلاش برای ورود"})
    SystemSetting.objects.get_or_create(setting_key="ACADEMIC_YEAR", defaults={'setting_value': "1405-1406", 'data_type': Constant.objects.get(category='data_type', code='string'), 'description': "سال تحصیلی جاری"})
    
    for i in range(20):
        Notification.objects.get_or_create(
            user=random.choice(students).person.user_accounts.first(), title=f"اعلان شماره {i+1}",
            defaults={'message': f"متن اعلان شماره {i+1}", 'notification_type': Constant.objects.get(category='notification_type', code='system')}
        )

    # ۱۵. سایر درخواست‌ها
    for i in range(5):
        StudentServiceRequest.objects.get_or_create(
            service_requester=students[i], defaults={
                'service_request_kind': Constant.objects.get(category='service_request_type', code='loan'),
                'service_request_data': f"درخواست وام دانشجویی شماره {i+1}",
                'service_decision_state': Constant.objects.get(category='review_status', code='pending'),
            }
        )
    for i in range(5, 10):
        ScholarshipApplication.objects.get_or_create(
            scholarship_applicant=students[i], defaults={
                'scholarship_type': "بورسیه تحصیلی", 'scholarship_reason': f"رتبه برتر {i+1}",
                'scholarship_status': Constant.objects.get(category='review_status', code='pending'),
            }
        )
    for i in range(3):
        CounselingAppointment.objects.get_or_create(
            counseling_student_link=students[i], counseling_teacher_link=teachers[i],
            counseling_date=f"2026-12-{i+1:02d} 10:00", counseling_topic=f"مشاوره درسی {i+1}",
            defaults={'counseling_status': Constant.objects.get(category='counseling_status', code='pending')}
        )
    for i in range(3):
        Proposal.objects.get_or_create(
            proposal_student_link=students[i], proposal_title=f"پروژه شماره {i+1}",
            defaults={'proposal_description': f"شرح پروژه شماره {i+1}", 'proposal_status': Constant.objects.get(category='proposal_status', code='pending')}
        )
    for i in range(5):
        TransferRequest.objects.get_or_create(
            student=students[i], destination_university=f"دانشگاه {i+1}",
            defaults={'review_status': Constant.objects.get(category='review_status', code='pending')}
        )
    for i in range(3):
        curr = Curriculum.objects.filter(field=students[i].field).first()
        if curr:
            GraduationAudit.objects.get_or_create(
                student=students[i], curriculum=curr,
                defaults={'graduation_status': Constant.objects.get(category='graduation_status', code='under_review')}
            )
    for i in range(5):
        EducationalChangeLog.objects.get_or_create(
            student=students[i], change_type=Constant.objects.get(category='change_type', code='grade_change'),
            changed_by=teachers[i % len(teachers)].person.user_accounts.first(),
            defaults={'description': f"تغییر نمره در درس شماره {i+1}"}
        )
    for i in range(3):
        CreditTransferRequest.objects.get_or_create(
            student=students[i], source_university=f"دانشگاه {i+1}",
            defaults={'status': Constant.objects.get(category='review_status', code='pending')}
        )
    for i in range(3):
        InternshipRequest.objects.get_or_create(
            student=students[i], organization_name=f"شرکت {i+1}",
            defaults={'start_date': "2026-12-01", 'status': Constant.objects.get(category='review_status', code='pending')}
        )
    for i in range(3):
        ThesisProgressReport.objects.get_or_create(
            student=students[i], teacher=teachers[i], report_content=f"پیشرفت {i+1}",
            defaults={'review_status': Constant.objects.get(category='thesis_review_status', code='pending')}
        )
    
    # ۱۶. کارآموزی، نظرسنجی، کلاس آنلاین و پارکینگ
    for i in range(5):
        Internship.objects.get_or_create(
            student=students[i], company_name=f"شرکت {i+1}",
            defaults={
                'request_type': Constant.objects.get(category='internship_request_type', code='letter'),
                'intern_start_date': "2026-12-01", 'duration_hours': 30,
                'status': Constant.objects.get(category='review_status', code='pending'),
            }
        )
    
    for enroll in Enrollment.objects.all()[:10]:
        TeacherSurvey.objects.get_or_create(
            enrollment=enroll, defaults={'overall_rating': random.randint(3, 5), 'teaching_quality': random.randint(3, 5), 'behavior': random.randint(3, 5), 'comment': "نظرسنجی نمونه"}
        )
    
    for i in range(5):
        OnlineClass.objects.get_or_create(
            teacher=teachers[i], offering=offerings[i], title=f"جلسه آنلاین {i+1}",
            defaults={
                'start_at': f"2026-10-{i+1:02d} 10:00", 'end_at': f"2026-10-{i+1:02d} 12:00",
                'meeting_link': f"https://meet.google.com/abc-{i+1}"
            }
        )
    
    for i in range(3):
        ParkingPasses.objects.get_or_create(
            parking_pass_code=f"PARK-{i+1}", defaults={'expiration_date': "2027-01-01", 'owner': students[i].person}
        )
    
    print(" ۱۵. سایر مدل‌ها (درخواست‌ها، کارآموزی، نظرسنجی، کلاس آنلاین، پارکینگ) ساخته شدند.")

    print("\n دیتابیس شما با موفقیت و به صورت کامل پر شد!")

if __name__ == "__main__":
    run()
