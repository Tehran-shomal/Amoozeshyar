"""صفحه‌های زندهٔ پرتال؛ فرم و خواندن داده در پوشهٔ گروه مسئول است."""
from urllib.parse import urlencode
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import OperationalError, transaction
from django.http import Http404, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from apps.core import models as m
from apps.core.api import APIError
from apps.core.accounts.services import (
    authenticate_person,
    store_authenticated_account,
)
from .common import term_code_display
from .registry import PAGES, NAV_GROUPS, SIDEBAR_FOOTER, LOGIN_COPY, build_page
from .mobina.selectors import dashboard

_PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def _term_options(terms, selected_term):
    """Build display-only semester labels from the actual term records."""
    options = []
    for term in terms:
        code = term_code_display(term)
        semester = term.semester.label if term.semester_id else "نیمسال"
        academic_year = term.academic_year.translate(_PERSIAN_DIGITS)
        options.append({
            "value": term.term_code,
            "display_label": f"{code} / {semester} {academic_year}",
            "selected": term.pk == getattr(selected_term, "pk", None),
        })
    return options


class LoginPreviewView(View):
    """ورود با سرویس احراز هویت موجود؛ فرم بدون JavaScript هم کار می‌کند."""
    def get(self, request):
        return render(request, "mobina/login.html", {"page_title": "ورود به سامانه", "login": LOGIN_COPY,
                      "owner": "mobina", "module_js": "mobina/section.js"})

    def post(self, request):
        try:
            person = authenticate_person(request.POST.get("username", ""), request.POST.get("password", ""), request)
            if person is not None:
                login(request, person)
                store_authenticated_account(request)
                request.session.set_expiry(None if request.POST.get("remember_me") == "on" else 0)
                return redirect("core:home")
            error = "نام کاربری یا گذرواژه نادرست است."
        except APIError:
            error = "ورود انجام نشد؛ وضعیت حساب و اطلاعات ورود را بررسی کنید."
        except OperationalError:
            return render(request, "core/database_unavailable.html", status=503)
        return render(request, "mobina/login.html", {"page_title": "ورود به سامانه", "login": LOGIN_COPY,
                     "owner": "mobina", "module_js": "mobina/section.js",
                     "login_error": error}, status=400)


class PortalView(LoginRequiredMixin, View):
    login_url = "/login/"

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except OperationalError:
            return render(request, "core/database_unavailable.html", status=503)

    def context(self, request, slug=None):
        if slug is not None and slug not in PAGES:
            raise Http404("این صفحه وجود ندارد.")
        profiles = list(m.Student.objects.filter(person=request.user).select_related("person", "field", "status", "educational_level"))
        code = request.GET.get("student_code")
        student = next((x for x in profiles if x.student_code == code), None) if code else (profiles[0] if len(profiles) == 1 else None)
        if code and student is None:
            raise PermissionDenied("پروندهٔ دانشجویی متعلق به این حساب نیست.")
        terms = list(m.Term.objects.select_related("semester").all())
        term_code = request.GET.get("term")
        term = next((x for x in terms if x.term_code == term_code), None) if term_code else next((x for x in terms if x.is_active), None)
        if term_code and term is None:
            raise Http404("نیمسال انتخاب‌شده وجود ندارد.")
        term_display_code = term_code_display(term)
        query = {}
        if student:
            query["student_code"] = student.student_code
        if term:
            query["term"] = term.term_code
        section = dict(PAGES[slug]) if slug else {}
        owner = section.get("owner", "mobina")
        data = {"page_title": section.get("title", "داشبورد"), "section": section,
            "owner": owner, "module_template": section.get("template", "core/live_content.html"),
            "module_js": section.get("script"), "active_slug": slug or "home", "is_home": slug is None,
            "nav_groups": NAV_GROUPS, "sidebar_footer": SIDEBAR_FOOTER, "profiles": profiles, "terms": terms,
            "term_options": _term_options(terms, term), "term_display_code": term_display_code,
            "selected_term": term, "current_student": student,
            "query_suffix": "?"+urlencode(query) if query else "",
            "api_profile": {"student_code": student.student_code} if student else {},
            "student": {"name": request.user.full_name, "avatar_initials": request.user.first_name[:1],
                "student_code": student.student_code if student else "—", "term": term_display_code}}
        if not profiles:
            data["profile_notice"] = "برای این حساب پروندهٔ دانشجویی ثبت نشده است."
        elif student is None:
            data["profile_notice"] = "پروندهٔ دانشجویی موردنظر را از بالای صفحه انتخاب کنید."
        if slug:
            if student or slug in {"notifications", "announcements", "settings", "guide"}:
                data.update(build_page(slug, student, term, request))
        else:
            data["dashboard"] = dashboard(student, term, request.user)
        return data

    def shell_context(self, request, slug=None):
        """Build presentation-only context; all record data comes from the page API."""
        if slug is not None and slug not in PAGES:
            raise Http404("این صفحه وجود ندارد.")
        section = dict(PAGES[slug]) if slug else {}
        active_slug = slug or "home"
        query = {}
        for key in ("student_code", "term"):
            value = request.GET.get(key)
            if value:
                query[key] = value
        return {
            "page_title": section.get("title", "داشبورد"),
            "section": section,
            "owner": section.get("owner", "mobina"),
            "module_template": section.get("template", "core/live_content.html"),
            "module_js": section.get("script"),
            "active_slug": active_slug,
            "is_home": slug is None,
            "nav_groups": NAV_GROUPS,
            "sidebar_footer": SIDEBAR_FOOTER,
            "profiles": [],
            "terms": [],
            "term_options": [],
            "term_display_code": "در حال دریافت…",
            "selected_term": None,
            "current_student": None,
            "query_suffix": "?" + urlencode(query) if query else "",
            "api_profile": {},
            "student": {
                "name": "دانشجوی گرامی",
                "avatar_initials": "د",
                "student_code": "در حال دریافت…",
                "term": "در حال دریافت…",
            },
            "portal_loading": True,
        }

    def get(self, request, slug=None):
        context = self.shell_context(request, slug)
        return render(request, "core/section.html" if slug else "mobina/home.html", context)

    def post(self, request, slug=None):
        context = self.context(request, slug)
        if slug in {"notifications", "announcements"}:
            try:
                key = int(request.POST.get("notification_id", ""))
            except (ValueError, TypeError):
                raise Http404("اعلان پیدا نشد.")
            changed = m.Notification.objects.filter(pk=key, user__person=request.user).update(is_read=True, read_at=timezone.now())
            if not changed:
                raise Http404("اعلان پیدا نشد.")
        else:
            form = context.get("form")
            if form is None:
                return HttpResponseNotAllowed(["GET"])
            if form.is_valid():
                try:
                    with transaction.atomic():
                        form.save()
                except ValidationError as error:
                    form.add_error(None, error)
                else:
                    messages.success(request, "اطلاعات با موفقیت ثبت شد.")
                    return redirect(request.path + context["query_suffix"])
            return render(request, "core/section.html", context, status=400)
        return redirect(request.path + context["query_suffix"])


class PortalLogoutView(View):
    """CSRF-protected browser fallback for logging out when JavaScript is disabled."""
    http_method_names = ["post", "options"]

    def post(self, request):
        logout(request)
        return redirect("core:login-preview")


class HomeView(PortalView):
    pass


class PortalSectionView(PortalView):
    pass
