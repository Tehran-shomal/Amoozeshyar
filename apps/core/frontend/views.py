"""صفحه‌های زندهٔ پرتال؛ فرم و خواندن داده در پوشهٔ گروه مسئول است."""
from urllib.parse import urlencode
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import OperationalError, transaction
from django.http import Http404, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from apps.core import models as m
from apps.core.api import APIError
from apps.core.accounts.services import authenticate_person
from .common import term_code_display
from .registry import PAGES, NAV_GROUPS, SIDEBAR_FOOTER, LOGIN_COPY, build_page
from .mobina.selectors import dashboard

_PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def _term_options(terms, selected_term):
    """Build display-only semester labels from the actual term records."""
    options = []
    for term in sorted(terms, key=lambda item: not item.is_active):
        code = term_code_display(term)
        semester = term.semester.label if term.semester_id else "نیمسال"
        academic_year = term.academic_year.translate(_PERSIAN_DIGITS)
        options.append({
            "value": term.term_code,
            "display_label": f"{code} / {semester} {academic_year}",
            "selected": term.pk == getattr(selected_term, "pk", None),
        })
    return options


def _render_react_login(request, login_error="", status=200):
    context = {
        "page_title": "ورود به سامانه",
        "login": LOGIN_COPY,
        "login_error": login_error,
        "login_bootstrap": {
            "kind": "login",
            "page": "login",
            "apiUrl": "",
            "submitUrl": "",
            "loginUrl": reverse("core:login-preview"),
            "logoutUrl": reverse("core:web-logout"),
            "homeUrl": reverse("core:home"),
            "sectionUrlTemplate": reverse("core:section", kwargs={"slug": "__slug__"}),
            "loginCopy": LOGIN_COPY,
            "loginError": login_error,
        },
    }
    return render(request, "core/login_react.html", context, status=status)


class LoginPreviewView(View):
    """ورود با سرویس احراز هویت موجود؛ فرم بدون JavaScript هم کار می‌کند."""
    def get(self, request):
        if request.GET.get("legacy") != "1":
            return _render_react_login(request)
        return render(request, "mobina/login.html", {"page_title": "ورود به سامانه", "login": LOGIN_COPY,
                      "owner": "mobina", "module_js": "mobina/login.js"})

    def post(self, request):
        try:
            person = authenticate_person(request.POST.get("username", ""), request.POST.get("password", ""), request)
            if person is not None:
                login(request, person)
                request.session.set_expiry(None if request.POST.get("remember_me") == "on" else 0)
                destination = reverse("core:home")
                preview_flags = {
                    key: "1" for key in ("react", "legacy")
                    if request.GET.get(key) == "1"
                }
                if preview_flags:
                    destination += "?" + urlencode(preview_flags)
                return redirect(destination)
            error = "نام کاربری یا گذرواژه نادرست است."
        except APIError:
            error = "ورود انجام نشد؛ وضعیت حساب و اطلاعات ورود را بررسی کنید."
        except OperationalError:
            if request.GET.get("legacy") != "1":
                return _render_react_login(
                    request,
                    login_error="پایگاه داده آمادهٔ پاسخ‌گویی نیست؛ ساختار یا دسترسی آن باید توسط مسئول سامانه بررسی شود.",
                    status=503,
                )
            return render(request, "core/database_unavailable.html", status=503)
        if request.GET.get("legacy") != "1":
            return _render_react_login(request, login_error=error, status=400)
        return render(request, "mobina/login.html", {"page_title": "ورود به سامانه", "login": LOGIN_COPY,
                     "owner": "mobina", "module_js": "mobina/login.js",
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
        for key in ("react", "legacy"):
            if request.GET.get(key) == "1":
                query[key] = "1"
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
            if student or slug in {
                "notifications", "announcements", "settings", "guide", "support"
            }:
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
        for key in ("react", "legacy"):
            if request.GET.get(key) == "1":
                query[key] = "1"
        api_query = request.GET.copy()
        api_url = reverse("portal_api:ui-page", kwargs={"slug": active_slug})
        submit_url = reverse("portal_api:page", kwargs={"slug": active_slug})
        if api_query:
            query_string = api_query.urlencode()
            api_url += "?" + query_string
            submit_url += "?" + query_string
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
            "portal_bootstrap": {
                "page": active_slug,
                "apiUrl": api_url,
                "submitUrl": submit_url,
                "loginUrl": reverse("core:login-preview"),
                "logoutUrl": reverse("core:web-logout"),
                "homeUrl": reverse("core:home"),
                "sectionUrlTemplate": reverse(
                    "core:section", kwargs={"slug": "__slug__"}
                ),
            },
        }

    def get(self, request, slug=None):
        context = self.shell_context(request, slug)
        if request.GET.get("legacy") != "1":
            return render(request, "core/react_shell.html", context)
        return render(request, "core/section.html" if slug else "mobina/home.html", context)

    def post(self, request, slug=None):
        context = self.context(request, slug)
        if slug in {"notifications", "announcements"}:
            try:
                field_name = "communication_id" if slug == "announcements" else "notification_id"
                raw_id = request.POST.get(field_name, "")
                if slug == "announcements" and not raw_id:
                    raw_id = request.POST.get("notification_id", "")
                key = int(raw_id)
            except (ValueError, TypeError):
                raise Http404("اعلان پیدا نشد.")
            if slug == "announcements":
                updates = {"is_read": True, "read_at": timezone.now()}
                read_status = m.Constant.objects.filter(
                    category="communication_status", code="read", is_active=True
                ).first()
                if read_status:
                    updates["status"] = read_status
                changed = m.Communication.objects.filter(
                    communication_id=key,
                    receiver__person=request.user,
                    communication_type__category="communication_type",
                    communication_type__code="announcement",
                ).update(**updates)
            else:
                changed = m.Notification.objects.filter(
                    pk=key, user__person=request.user
                ).update(is_read=True, read_at=timezone.now())
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
                    if slug == "evaluation-form":
                        enrollment = form.instance.enrollment
                        query = {
                            "student_code": enrollment.student.student_code,
                            "term": enrollment.offering.term.term_code,
                            "enrollment": enrollment.pk,
                        }
                        return redirect(request.path + "?" + urlencode(query))
                    if slug == "settings":
                        result_query = context["query_suffix"]
                        separator = "&" if result_query else "?"
                        result_query += separator + urlencode({"settings_saved": 1})
                        return redirect(request.path + result_query)
                    if slug in {"internship", "guest-request", "messages", "grade-appeal", "financial-aid", "requests", "education-certificate", "support"}:
                        result_query = context["query_suffix"]
                        separator = "&" if result_query else "?"
                        result_query += separator + urlencode({"request_id": form.instance.pk})
                        return redirect(request.path + result_query)
                    return redirect(request.path + context["query_suffix"])
            return render(request, "core/section.html", context, status=400)
        query_suffix = context["query_suffix"]
        if slug == "notifications" and context.get("notification_filter_code"):
            separator = "&" if query_suffix else "?"
            query_suffix += separator + urlencode({
                "notification_type": context["notification_filter_code"]
            })
        return redirect(request.path + query_suffix)


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
