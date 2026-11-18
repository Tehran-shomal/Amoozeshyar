"""
ساخت داده‌ی تستی برای جدول‌های پروژه.

اجرا:
    python manage.py seed
"""

from datetime import date, time, timedelta
from decimal import Decimal

from django.apps import apps
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.core import models as m

# ----------------------------------------------------------------------
# مقادیر ثابت (Constant): category -> [(code, label), ...]
# ----------------------------------------------------------------------
CONSTANTS = {
    "gender": [("male", "مرد"), ("female", "زن")],
    "language": [("fa", "فارسی"), ("en", "انگلیسی")],
    "academic_rank": [
        ("instructor", "مربی"),
        ("assistant_professor", "استادیار"),
        ("associate_professor", "دانشیار"),
        ("professor", "استاد"),
    ],
    "educational_level": [
        ("associate", "کاردانی"),
        ("bachelor", "کارشناسی"),
        ("master", "ارشد"),
        ("phd", "دکتری"),
    ],
    "student_status": [
        ("active", "فعال"),
        ("on_leave", "مرخصی"),
        ("probation", "مشروط"),
        ("graduated", "فارغ‌التحصیل"),
        ("withdrawn", "انصراف"),
    ],
    "enrollment_status": [
        ("registered", "ثبت‌نام‌شده"),
        ("dropped", "حذف‌شده"),
    ],
    "admission_type": [("with_exam", "با آزمون"), ("without_exam", "بدون آزمون")],
    "lesson_type": [
        ("specialized", "تخصصی"),
        ("general", "عمومی"),
        ("basic", "پایه"),
        ("elective", "اختیاری"),
    ],
    "semester": [("mehr", "مهر"), ("bahman", "بهمن"), ("summer", "تابستان")],
    "day_of_week": [
        ("saturday", "شنبه"),
        ("sunday", "یکشنبه"),
        ("monday", "دوشنبه"),
        ("tuesday", "سه‌شنبه"),
        ("wednesday", "چهارشنبه"),
        ("thursday", "پنجشنبه"),
        ("friday", "جمعه"),
    ],
    "exam_type": [("midterm", "میان‌ترم"), ("final", "پایان‌ترم"), ("online", "مجازی")],
    "prerequisite_type": [("prerequisite", "پیش‌نیاز"), ("co_requisite", "هم‌نیاز")],
    "appeal_status": [
        ("pending", "در انتظار بررسی"),
        ("approved", "تایید"),
        ("rejected", "رد"),
    ],
    "attendance_status": [("present", "حاضر"), ("absent", "غایب"), ("late", "تاخیر")],
    "ticket_creator_role": [
        ("student", "دانشجو"),
        ("teacher", "استاد"),
        ("staff", "کارمند"),
    ],
    "ticket_status": [
        ("open", "باز"),
        ("in_progress", "در حال بررسی"),
        ("closed", "بسته"),
    ],
    "review_status": [
        ("pending", "در انتظار بررسی"),
        ("approved", "تایید"),
        ("rejected", "رد"),
        ("issued", "صادر شد"),
    ],
    "service_request_type": [
        ("installment", "تقسیط بدهی"),
        ("withdrawal", "انصراف از تحصیل"),
        ("employment_certificate", "گواهی اشتغال"),
        ("internship_letter", "نامه کارآموزی"),
    ],
    "counseling_status": [
        ("scheduled", "برنامه‌ریزی شده"),
        ("completed", "انجام شده"),
        ("cancelled", "لغو شده"),
        ("rejected", "رد شده"),
    ],
    "proposal_status": [
        ("pending", "در انتظار بررسی"),
        ("approved", "تایید شده"),
        ("rejected", "رد شده"),
        ("needs_revision", "نیازمند اصلاح"),
    ],
    "thesis_review_status": [
        ("pending", "در انتظار بررسی"),
        ("approved", "تایید"),
        ("needs_revision", "نیازمند اصلاح"),
    ],
    "graduation_status": [
        ("eligible", "واجد شرایط"),
        ("not_eligible", "فاقد شرایط"),
        ("under_review", "در حال بررسی"),
    ],
    "change_type": [
        ("profile_change", "تغییر مشخصات فردی"),
        ("grade_change", "تغییر نمره"),
        ("course_drop", "حذف درس"),
        ("status_change", "تغییر وضعیت تحصیلی"),
    ],
    "requirement_type": [
        ("mandatory", "اجباری"),
        ("elective", "اختیاری"),
        ("basic", "پایه"),
    ],
    "communication_type": [
        ("official", "رسمی"),
        ("informal", "غیررسمی"),
        ("request", "درخواست"),
        ("announcement", "اطلاعیه"),
    ],
    "communication_status": [
        ("unread", "خوانده نشده"),
        ("read", "خوانده شده"),
        ("replied", "پاسخ داده شده"),
    ],
    "data_type": [
        ("integer", "عدد صحیح"),
        ("decimal", "عدد اعشار"),
        ("string", "رشته"),
        ("boolean", "مقدار منطقی"),
        ("date", "تاریخ"),
    ],
    "notification_type": [
        ("grade", "نمره"),
        ("announcement", "اطلاعیه"),
        ("class_change", "تغییر کلاس"),
        ("system", "سیستمی"),
    ],
    "internship_request_type": [
        ("internship_letter", "نامه کارآموزی"),
        ("introduction_letter", "معرفی‌نامه"),
    ],
}


class Command(BaseCommand):
    help = "ساخت داده‌ی تستی برای محیط توسعه"

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="Test@12345",
            help="رمز کاربران تستی (پیش‌فرض: Test@12345)",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("این دستور فقط وقتی DEBUG=True باشد اجرا می‌شود.")

        self.default_password = options["password"]
        self.created = {}
        self.K = {}

        with transaction.atomic():
            self.seed()

        self.report()

    def make(self, model, lookup, **defaults):
        obj, created = model.objects.get_or_create(defaults=defaults, **lookup)
        if created:
            name = model.__name__
            self.created[name] = self.created.get(name, 0) + 1
        return obj

    def k(self, category, code):
        return self.K[(category, code)]

    def person(self, username, first, last, national_id, birth, place, gender, superuser=False):
        obj = m.Person.objects.filter(username=username).first()
        if obj:
            return obj
        extra = dict(
            email=f"{username}@example.com",
            first_name=first,
            last_name=last,
            national_id=national_id,
            birth_date=birth,
            birth_place=place,
            gender=self.k("gender", gender),
            preferred_language=self.k("language", "fa"),
        )
        if superuser:
            obj = m.Person.objects.create_superuser(
                username=username, password=self.default_password, **extra
            )
        else:
            obj = m.Person.objects.create_user(
                username=username, password=self.default_password, **extra
            )
        self.created["Person"] = self.created.get("Person", 0) + 1
        return obj

    def seed(self):
        now = timezone.now()
        today = date.today()
        day = timedelta(days=1)

        # مقادیر ثابت
        for category, items in CONSTANTS.items():
            for code, label in items:
                self.K[(category, code)] = self.make(
                    m.Constant,
                    {"category": category, "code": code},
                    label=label,
                )

        # اشخاص
        admin = self.person("admin", "مدیر", "سیستم", "0010000001",
                            date(1985, 3, 21), "تهران", "male", superuser=True)
        t_person1 = self.person("teacher1", "علی", "رضایی", "0010000002",
                                date(1980, 5, 10), "اصفهان", "male")
        t_person2 = self.person("teacher2", "مریم", "کریمی", "0010000003",
                                date(1978, 8, 2), "شیراز", "female")
        s_person1 = self.person("student1", "سارا", "احمدی", "0010000004",
                                date(2002, 1, 15), "تهران", "female")
        s_person2 = self.person("student2", "محمد", "حسینی", "0010000005",
                                date(2001, 11, 3), "مشهد", "male")

        # نقش‌ها و حساب‌های کاربری
        role_student = self.make(m.Role, {"role_name": "دانشجو"}, description="دسترسی دانشجو")
        role_teacher = self.make(m.Role, {"role_name": "استاد"}, description="دسترسی استاد")

        ua_teacher = self.make(
            m.UserAccount, {"username": "ua_teacher1"},
            person=t_person1, role=role_teacher,
            password=make_password(self.default_password),
        )
        ua_student = self.make(
            m.UserAccount, {"username": "ua_student1"},
            person=s_person1, role=role_student,
            password=make_password(self.default_password),
        )

        # دانشکده، گروه، رشته
        fac_eng = self.make(m.Faculty, {"faculty_code": "ENG"}, faculty_name="دانشکده فنی و مهندسی")
        fac_sci = self.make(m.Faculty, {"faculty_code": "SCI"}, faculty_name="دانشکده علوم پایه")

        dep_ce = self.make(m.Department, {"faculty": fac_eng, "department_code": "CE"}, department_name="گروه مهندسی کامپیوتر")
        dep_math = self.make(m.Department, {"faculty": fac_sci, "department_code": "MATH"}, department_name="گروه ریاضی")

        field_ce = self.make(m.Field, {"department": dep_ce, "field_code": "CE-BS"}, field_name="مهندسی کامپیوتر")
        field_am = self.make(m.Field, {"department": dep_math, "field_code": "AM-BS"}, field_name="ریاضی کاربردی")

        # استاد و دانشجو
        teacher1 = self.make(
            m.Teacher, {"teacher_code": "T-1001"},
            person=t_person1, department=dep_ce,
            academic_rank=self.k("academic_rank", "assistant_professor"),
            hire_date=date(2015, 9, 1),
        )
        teacher2 = self.make(
            m.Teacher, {"teacher_code": "T-1002"},
            person=t_person2, department=dep_math,
            academic_rank=self.k("academic_rank", "professor"),
            hire_date=date(2010, 9, 1),
        )

        student1 = self.make(
            m.Student, {"student_code": "4011001"},
            person=s_person1, field=field_ce,
            educational_level=self.k("educational_level", "bachelor"),
            application_date=date(2022, 9, 23),
            status=self.k("student_status", "active"),
            admission_type=self.k("admission_type", "with_exam"),
            previous_term_gpa=Decimal("17.50"), total_gpa=Decimal("16.80"),
            passed_units=60, tuition_debt=Decimal("0"), completed_terms=4,
        )
        student2 = self.make(
            m.Student, {"student_code": "4011002"},
            person=s_person2, field=field_am,
            educational_level=self.k("educational_level", "bachelor"),
            application_date=date(2022, 9, 23),
            status=self.k("student_status", "probation"),
            admission_type=self.k("admission_type", "without_exam"),
            previous_term_gpa=Decimal("11.25"), total_gpa=Decimal("11.90"),
            passed_units=40, tuition_debt=Decimal("5000000"), completed_terms=4,
        )

        # دروس و چارت
        lesson_math = self.make(
            m.Lesson, {"lesson_code": "MATH101"},
            title="ریاضی عمومی ۱", theory_units=3, practical_units=0,
            lesson_type=self.k("lesson_type", "general"), department=dep_math,
        )
        lesson_prog = self.make(
            m.Lesson, {"lesson_code": "CE101"},
            title="مبانی برنامه‌نویسی", theory_units=2, practical_units=1,
            lesson_type=self.k("lesson_type", "specialized"), department=dep_ce,
        )
        lesson_ds = self.make(
            m.Lesson, {"lesson_code": "CE201"},
            title="ساختمان داده‌ها", theory_units=3, practical_units=0,
            lesson_type=self.k("lesson_type", "specialized"), department=dep_ce,
        )

        self.make(
            m.Prerequisite,
            {"lesson": lesson_ds, "prerequisite_lesson": lesson_prog},
            prerequisite_type=self.k("prerequisite_type", "prerequisite"),
        )
        self.make(
            m.Prerequisite,
            {"lesson": lesson_prog, "prerequisite_lesson": lesson_math},
            prerequisite_type=self.k("prerequisite_type", "co_requisite"),
        )

        curr1 = self.make(
            m.Curriculum, {"field": field_ce, "lesson": lesson_prog},
            requirement_type=self.k("requirement_type", "mandatory"),
            recommended_term=1, calculated_units=3,
        )
        curr2 = self.make(
            m.Curriculum, {"field": field_ce, "lesson": lesson_ds},
            requirement_type=self.k("requirement_type", "mandatory"),
            recommended_term=2, calculated_units=3,
        )

        room1 = self.make(
            m.Classroom, {"building_name": "ساختمان مرکزی", "room_number": "101"},
            capacity=40, classroom_type="کلاس معمولی",
        )
        room2 = self.make(
            m.Classroom, {"building_name": "ساختمان آزمایشگاه‌ها", "room_number": "L2"},
            capacity=25, classroom_type="آزمایشگاه",
        )

        # ترم‌ها
        term1 = self.make(
            m.Term, {"term_code": "14051"},
            semester=self.k("semester", "mehr"), academic_year="1405-1406",
            start_date=today - 30 * day, end_date=today + 90 * day,
            registration_start=now - 60 * day, registration_end=now - 40 * day,
            add_drop_start=now - 35 * day, add_drop_end=now - 25 * day,
            emergency_drop_start=now - 20 * day, emergency_drop_end=now - 10 * day,
            is_active=True,
        )
        term2 = self.make(
            m.Term, {"term_code": "14052"},
            semester=self.k("semester", "bahman"), academic_year="1405-1406",
            start_date=today + 120 * day, end_date=today + 250 * day,
            registration_start=now - 5 * day, registration_end=now + 10 * day,
            add_drop_start=now + 125 * day, add_drop_end=now + 135 * day,
            emergency_drop_start=now + 140 * day, emergency_drop_end=now + 150 * day,
            is_active=False,
        )

        # ارائه دروس (remaining_capacity حذف شده است چون @property است)
        offering1 = self.make(
            m.CourseOffering,
            {"lesson": lesson_prog, "term": term1, "teacher": teacher1},
            capacity=40,
            day_of_week=self.k("day_of_week", "saturday"),
            start_time=time(8, 0), end_time=time(10, 0), classroom=room1,
            exam_date=today + 60 * day, exam_time=time(9, 0), is_active=True,
        )
        offering2 = self.make(
            m.CourseOffering,
            {"lesson": lesson_ds, "term": term1, "teacher": teacher2},
            capacity=30,
            day_of_week=self.k("day_of_week", "monday"),
            start_time=time(10, 0), end_time=time(12, 0), classroom=room2,
            is_active=True,
        )

        # انتخاب واحد و امتحانات
        enroll1 = self.make(m.Enrollment, {"student": student1, "offering": offering1})
        enroll2 = self.make(m.Enrollment, {"student": student2, "offering": offering1})

        self.make(
            m.Exam, {"offering": offering1, "exam_type": self.k("exam_type", "midterm")},
            exam_date=today + 45 * day,
        )
        exam2 = self.make(
            m.Exam, {"offering": offering2, "exam_type": self.k("exam_type", "final")},
            exam_date=today + 70 * day,
        )

        self.make(
            m.GradeAppeal, {"enrollment": enroll1},
            appeal_reason="به نظر می‌رسد نمره ارزشیابی میان‌ترم اشتباه ثبت شده است.",
            appeal_date=now - 3 * day,
            appeal_status=self.k("appeal_status", "pending"),
        )
        self.make(
            m.GradeAppeal, {"enrollment": enroll2},
            appeal_reason="درخواست بازبینی برگه امتحانی.",
            appeal_date=now - 5 * day,
            appeal_status=self.k("appeal_status", "approved"),
        )

        self.make(
            m.Attendance, {"enrollment": enroll1, "session_number": 1},
            session_date=today - 7 * day, attendance_time=time(8, 5),
            attendance_status=self.k("attendance_status", "present"),
            description="حاضر در کلاس", recorded_by=ua_teacher,
        )
        self.make(
            m.Attendance, {"enrollment": enroll2, "session_number": 1},
            session_date=today - 7 * day, attendance_time=time(8, 0),
            attendance_status=self.k("attendance_status", "absent"),
            description="غیبت بدون اطلاع قبلی", recorded_by=ua_teacher,
        )

        self.make(
            m.TeacherSurvey, {"enrollment": enroll1},
            overall_rating=5, teaching_quality=4, behavior=5,
            comment="تدریس روان و کلاس منظم بود.",
        )
        self.make(
            m.TeacherSurvey, {"enrollment": enroll2},
            overall_rating=3, behavior=4,
            comment="سرعت تدریس کمی بالا بود.",
        )

        # کلاس مجازی
        self.make(
            m.OnlineClass, {"offering": offering1, "title": "جلسه ۱ - معرفی درس"},
            teacher=teacher1,
            start_at=now - timedelta(hours=1), end_at=now + timedelta(hours=1),
            meeting_link="https://meet.example.com/ce101-session1",
        )
        self.make(
            m.OnlineClass, {"offering": offering2, "title": "جلسه ۱ - لیست پیوندی"},
            teacher=teacher2,
            start_at=now + 2 * day, end_at=now + 2 * day + timedelta(hours=2),
            meeting_link="https://meet.example.com/ce201-session1",
        )

        # مالی
        pay1 = self.make(
            m.Payment, {"tracking_code": "TRK-1001"},
            student=student1, term=term1, amount=Decimal("12000000.00"),
            payment_date=now - 20 * day, status=self.k("appeal_status", "approved"),
        )
        pay2 = self.make(
            m.Payment, {"tracking_code": "TRK-1002"},
            student=student2, term=term1, amount=Decimal("3000000.00"),
            payment_date=now - 18 * day, status=self.k("appeal_status", "approved"),
        )
        self.make(m.TuitionReceipt, {"receipt_serial_code": "RCP-1001"},
                  receipt_payment_link=pay1,
                  receipt_document_uri="/media/receipts/RCP-1001.pdf")
        self.make(m.TuitionReceipt, {"receipt_serial_code": "RCP-1002"},
                  receipt_payment_link=pay2,
                  receipt_document_uri="/media/receipts/RCP-1002.pdf")

        self.make(
            m.RefundRequest,
            {"refund_payment_link": pay1,
             "refund_justification_text": "انصراف از یکی از دروس انتخابی"},
            refund_value_requested=Decimal("2000000.00"),
            refund_review_state=self.k("review_status", "pending"),
        )
        self.make(
            m.RefundRequest,
            {"refund_payment_link": pay2,
             "refund_justification_text": "پرداخت اضافه در ترم قبل"},
            refund_value_requested=Decimal("500000.00"),
            refund_review_state=self.k("review_status", "approved"),
        )

        # درخواست‌ها و فرایندهای آموزشی
        self.make(
            m.StudentServiceRequest,
            {"service_requester": student1,
             "service_request_kind": self.k("service_request_type", "installment")},
            service_request_data="درخواست تقسیط شهریه در ۴ قسط",
            service_decision_state=self.k("review_status", "pending"),
        )
        self.make(
            m.StudentServiceRequest,
            {"service_requester": student2,
             "service_request_kind": self.k("service_request_type", "employment_certificate")},
            service_request_data="گواهی اشتغال به تحصیل برای بیمه",
            service_decision_state=self.k("review_status", "approved"),
        )

        self.make(
            m.ScholarshipApplication,
            {"scholarship_applicant": student1, "scholarship_type": "بورسیه تحصیلی"},
            scholarship_reason="معدل بالا و فعالیت پژوهشی",
            scholarship_status=self.k("review_status", "pending"),
        )
        self.make(
            m.ScholarshipApplication,
            {"scholarship_applicant": student2, "scholarship_type": "بورسیه فرهنگی"},
            scholarship_reason="فعالیت فرهنگی در دانشگاه",
            scholarship_status=self.k("review_status", "rejected"),
        )

        self.make(
            m.CounselingAppointment,
            {"counseling_student_link": student1, "counseling_teacher_link": teacher1,
             "counseling_topic": "مشاوره انتخاب گرایش"},
            counseling_date=now + 3 * day,
            counseling_description="بررسی گرایش‌های رشته",
            counseling_status=self.k("counseling_status", "scheduled"),
        )
        self.make(
            m.CounselingAppointment,
            {"counseling_student_link": student2, "counseling_teacher_link": teacher2,
             "counseling_topic": "مشاوره وضعیت مشروطی"},
            counseling_date=now - 5 * day,
            counseling_description="برنامه‌ریزی برای جبران معدل",
            counseling_status=self.k("counseling_status", "completed"),
        )

        self.make(
            m.Proposal,
            {"proposal_student_link": student1,
             "proposal_title": "سامانه مدیریت آموزش دانشگاهی"},
            proposal_description="طراحی و پیاده‌سازی سامانه آموزشی با جنگو",
            proposal_status=self.k("proposal_status", "pending"),
        )
        self.make(
            m.Proposal,
            {"proposal_student_link": student2,
             "proposal_title": "تحلیل داده‌های آموزشی"},
            proposal_description="تحلیل نمرات و پیش‌بینی عملکرد دانشجویان",
            proposal_status=self.k("proposal_status", "approved"),
        )

        self.make(
            m.TransferRequest,
            {"student": student1, "destination_university": "دانشگاه تهران"},
            review_status=self.k("review_status", "pending"),
            course_compatibility_result="در انتظار بررسی دروس",
        )
        self.make(
            m.TransferRequest,
            {"student": student2, "destination_university": "دانشگاه صنعتی شریف"},
            review_status=self.k("review_status", "rejected"),
            course_compatibility_result="دروس تطبیق نداشتند",
        )

        self.make(
            m.CreditTransferRequest,
            {"student": student1, "source_university": "دانشگاه شیراز"},
            status=self.k("review_status", "pending"),
        )
        self.make(
            m.CreditTransferRequest,
            {"student": student2, "source_university": "دانشگاه اصفهان"},
            status=self.k("review_status", "approved"),
        )

        self.make(
            m.InternshipRequest,
            {"student": student1, "organization_name": "شرکت داده‌پردازان"},
            start_date=today + 30 * day,
            status=self.k("review_status", "pending"),
        )
        self.make(
            m.InternshipRequest,
            {"student": student2, "organization_name": "شرکت نرم‌افزاری پارس"},
            start_date=today + 45 * day,
            status=self.k("review_status", "approved"),
        )

        self.make(
            m.Internship,
            {"student": student1, "company_name": "شرکت داده‌پردازان"},
            request_type=self.k("internship_request_type", "internship_letter"),
            intern_start_date=today + 30 * day, duration_hours=240,
            status=self.k("review_status", "pending"),
        )
        self.make(
            m.Internship,
            {"student": student2, "company_name": "شرکت نرم‌افزاری پارس"},
            request_type=self.k("internship_request_type", "introduction_letter"),
            intern_start_date=today + 45 * day, duration_hours=180,
            status=self.k("review_status", "approved"),
            reviewed_by=ua_teacher, reviewed_at=now - 2 * day,
        )

        self.make(
            m.ThesisProgressReport,
            {"student": student1, "teacher": teacher1,
             "report_content": "گزارش پیشرفت ماه اول: مرور منابع تکمیل شد."},
            review_status=self.k("thesis_review_status", "pending"),
        )
        self.make(
            m.ThesisProgressReport,
            {"student": student2, "teacher": teacher2,
             "report_content": "گزارش پیشرفت ماه دوم: جمع‌آوری داده."},
            review_status=self.k("thesis_review_status", "needs_revision"),
        )

        self.make(
            m.GraduationAudit, {"student": student1, "curriculum": curr1},
            graduation_status=self.k("graduation_status", "under_review"),
        )
        self.make(
            m.GraduationAudit, {"student": student2, "curriculum": curr2},
            graduation_status=self.k("graduation_status", "not_eligible"),
        )

        self.make(
            m.EducationalChangeLog,
            {"student": student1, "changed_by": ua_teacher,
             "description": "اصلاح نمره درس مبانی برنامه‌نویسی"},
            change_type=self.k("change_type", "grade_change"),
        )
        self.make(
            m.EducationalChangeLog,
            {"student": student2, "changed_by": ua_teacher,
             "description": "تغییر وضعیت به مشروط"},
            change_type=self.k("change_type", "status_change"),
        )

        # ارتباطات، تنظیمات و اعلان‌ها
        self.make(
            m.Communication,
            {"sender": ua_teacher, "receiver": ua_student, "subject": "اطلاعیه امتحان"},
            message_body="امتحان میان‌ترم هفته آینده برگزار می‌شود.",
            communication_type=self.k("communication_type", "announcement"),
            status=self.k("communication_status", "unread"),
        )
        self.make(
            m.Communication,
            {"sender": ua_student, "receiver": ua_teacher,
             "subject": "پرسش درباره تکلیف"},
            message_body="سلام استاد، مهلت تحویل تکلیف تمدید می‌شود؟",
            communication_type=self.k("communication_type", "request"),
            status=self.k("communication_status", "replied"),
            is_read=True, read_at=now - day,
        )

        self.make(
            m.SystemSetting, {"setting_key": "max_units_per_term"},
            setting_value="20", data_type=self.k("data_type", "integer"),
            description="سقف واحد مجاز در هر ترم", updated_by=ua_teacher,
        )
        self.make(
            m.SystemSetting, {"setting_key": "university_name"},
            setting_value="دانشگاه نمونه", data_type=self.k("data_type", "string"),
            description="نام دانشگاه برای نمایش در سامانه",
        )

        self.make(
            m.Notification, {"user": ua_student, "title": "ثبت نمره جدید"},
            message="نمره درس مبانی برنامه‌نویسی ثبت شد.",
            related_exam=exam2,
            notification_type=self.k("notification_type", "grade"),
            sent_at=now,
        )
        self.make(
            m.Notification, {"user": ua_teacher, "title": "شروع ترم جدید"},
            message="ترم جدید از هفته آینده آغاز می‌شود.",
            notification_type=self.k("notification_type", "announcement"),
            sent_at=now - day, is_read=True, read_at=now,
        )

        # گروه کلاسی و پارکینگ
        group1 = self.make(
            m.LessonGroups, {"id": 1},
            name="گروه درس مبانی برنامه‌نویسی",
            created_by=t_person1, teacher=teacher1,
        )
        group1.members.add(s_person1, s_person2)
        group2 = self.make(
            m.LessonGroups, {"id": 2},
            name="گروه درس ریاضی عمومی",
            created_by=t_person2, teacher=teacher2,
        )
        group2.members.add(s_person1)

        self.make(
            m.ParkingPasses, {"parking_pass_code": "PK-1001"},
            owner=t_person1, expiration_date=today + 180 * day, charge=500000,
        )
        self.make(
            m.ParkingPasses, {"parking_pass_code": "PK-1002"},
            owner=s_person1, expiration_date=today + 30 * day, charge=100000,
        )

        # تیکت‌ها
        cat_fin = self.make(m.TicketCategory, {"name": "مالی"})
        cat_edu = self.make(m.TicketCategory, {"name": "آموزشی"})
        self.make(m.TicketCategory, {"name": "اعتراض به نمره"}, parent=cat_edu)

        ticket1 = self.make(
            m.Ticket, {"subject": "مشکل در پرداخت شهریه", "creator": s_person1},
            creator_role=self.k("ticket_creator_role", "student"),
            category=cat_fin,
            content="پرداخت انجام شد ولی رسید صادر نشده است.",
            status=self.k("ticket_status", "in_progress"),
            assigned_to=admin,
        )
        self.make(
            m.Ticket, {"subject": "درخواست تغییر ساعت کلاس", "creator": t_person1},
            creator_role=self.k("ticket_creator_role", "teacher"),
            category=cat_edu,
            content="امکان جابه‌جایی کلاس شنبه به یکشنبه وجود دارد؟",
            status=self.k("ticket_status", "open"),
        )
        self.make(
            m.Ticket, {"subject": "Re: مشکل در پرداخت شهریه", "creator": admin},
            creator_role=self.k("ticket_creator_role", "staff"),
            category=cat_fin, parent=ticket1,
            content="رسید شما صادر شد. لطفاً بررسی کنید.",
            status=self.k("ticket_status", "open"),
        )

    def report(self):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("داده‌ی تستی آماده است."))
        self.stdout.write(f"{'مدل':32} {'تعداد کل':>9} {'جدید':>6}")
        self.stdout.write("-" * 50)
        low = []
        for model in apps.get_app_config("core").get_models():
            total = model.objects.count()
            new = self.created.get(model.__name__, 0)
            self.stdout.write(f"{model.__name__:32} {total:>9} {new:>6}")
            if total < 2:
                low.append(model.__name__)
        self.stdout.write("")
        if low:
            self.stdout.write(self.style.WARNING(
                "مدل‌های کمتر از دو رکورد: " + ", ".join(low)
            ))
        self.stdout.write(
            f"ورود به پنل ادمین:  admin  /  {self.default_password}   (آدرس: /admin/)"
        )
