
import datetime
import decimal
import itertools
import random

from django.apps import apps
from django.core import validators as V
from django.core.management.base import BaseCommand
from django.db import models, transaction
from django.utils import timezone

APP = "core"
SKIP_MODELS = {"Constant", "StudentAcademicRules"}  # Constant با سیدر migration پر شده
_uid = itertools.count(1)


# ---------- ترتیب مدل‌ها بر اساس وابستگی ----------
def sorted_models(model_list):
    def deps(m, with_nullable=True):
        out = set()
        for f in m._meta.concrete_fields:
            if f.is_relation and f.related_model in model_list and f.related_model is not m:
                if with_nullable or not f.null:
                    out.add(f.related_model)
        return out

    done, order, left = set(), [], list(model_list)
    while left:
        progress = False
        for m in list(left):
            if deps(m) <= done:
                order.append(m); done.add(m); left.remove(m); progress = True
        if not progress:  # حلقه: فقط وابستگی‌های اجباری را رعایت کن
            for m in list(left):
                if deps(m, False) <= done:
                    order.append(m); done.add(m); left.remove(m); progress = True
                    break
        if not progress:
            order.extend(left); break
    return order


# ---------- ساخت مقدار برای هر نوع فیلد ----------
def int_range(f):
    lo, hi = 1, 5
    for v in f.validators:
        if isinstance(v, V.MinValueValidator): lo = max(lo, v.limit_value) if v.limit_value > 1 else lo
        if isinstance(v, V.MaxValueValidator): hi = min(hi, v.limit_value)
    for v in f.validators:
        if isinstance(v, V.MinValueValidator): lo = v.limit_value
    return int(lo), int(max(lo, hi))


def text_value(f, i):
    n = f.name.lower()
    u = next(_uid)
    if "email" in n: s = f"user{u}@example.com"
    elif "national" in n: s = f"{1000000000 + u}"
    elif "phone" in n or "mobile" in n: s = f"0912{1000000 + u}"
    elif "code" in n or "number" in n or "plate" in n or "serial" in n or "tracking" in n:
        s = f"{u:06d}"
    elif "url" in n or "link" in n: s = f"https://example.com/{u}"
    elif "ip" == n: s = "127.0.0.1"
    else: s = f"نمونه {f.model.__name__} {u}"
    if f.max_length: s = s[: f.max_length]
    return s


def value_for(f, i, attempt):
    if isinstance(f, models.BooleanField): return bool(i % 2) if attempt == 0 else True
    if isinstance(f, models.IntegerField):  # شامل PositiveInteger و BigInteger
        lo, hi = int_range(f)
        if isinstance(f, models.PositiveIntegerField) or lo >= 0:
            lo = max(lo, 0)
        return min(hi, max(lo, 1 + (i + attempt) % 5)) if hi - lo < 100 else lo + i
    if isinstance(f, models.DecimalField):
        return decimal.Decimal(10 + i + attempt).quantize(decimal.Decimal(1).scaleb(-f.decimal_places))
    if isinstance(f, models.FloatField): return float(10 + i)
    if isinstance(f, models.DateTimeField):
        return timezone.now() + datetime.timedelta(days=i + attempt * 30)
    if isinstance(f, models.DateField):
        return datetime.date.today() + datetime.timedelta(days=i + attempt * 30)
    if isinstance(f, models.TimeField):
        return datetime.time(8 + (i * 2) % 10, 0) if attempt == 0 else datetime.time(8, 0)
    if isinstance(f, models.DurationField): return datetime.timedelta(minutes=30 + i)
    if isinstance(f, models.JSONField): return {}
    if isinstance(f, models.UUIDField):
        import uuid; return uuid.uuid4()
    if isinstance(f, (models.FileField,)): return ""
    if isinstance(f, models.GenericIPAddressField): return "127.0.0.1"
    if isinstance(f, (models.CharField, models.TextField, models.SlugField)):
        return text_value(f, i)
    return None


# ---------- انتخاب مقدار کلید خارجی ----------
def fk_value(f, i, used_o2o):
    rel = f.related_model
    qs = rel.objects.all()
    lim = f.get_limit_choices_to() if hasattr(f, "get_limit_choices_to") else {}
    if rel.__name__ == "Constant" and lim.get("category"):
        cat = lim["category"]
        qs = rel.objects.filter(category=cat)
        if not qs.exists():  # دسته‌ای که سیدر نداشته (مثل rating, payment_status)
            for k in range(1, 6):
                rel.objects.get_or_create(category=cat, code=str(k), defaults={"label": f"{cat} {k}", "is_active": True})
            qs = rel.objects.filter(category=cat)
    elif lim:
        qs = qs.filter(**lim)
    objs = list(qs.order_by("pk"))
    if not objs: return None
    if f.one_to_one or f.unique:
        free = [o for o in objs if o.pk not in used_o2o.setdefault(f, set())]
        if not free: return None
        pick = free[0]; used_o2o[f].add(pick.pk); return pick
    return objs[i % len(objs)]


class Command(BaseCommand):
    help = "برای هر مدل ادمین چند رکورد نمونه با رعایت وابستگی‌ها می‌سازد"

    def add_arguments(self, p):
        p.add_argument("--count", type=int, default=5)

    def handle(self, *a, **o):
        count = o["count"]
        random.seed(1)
        mods = [m for m in apps.get_app_config(APP).get_models()
                if m.__name__ not in SKIP_MODELS and not m._meta.auto_created]
        report, used_o2o = [], {}
        for m in sorted_models(mods):
            made, errors = 0, []
            for i in range(count):
                if m.__name__ == "Person" and not m.objects.filter(username=f"seed_user{i+1}").exists():
                    pass
                ok = False
                for attempt in range(4):
                    try:
                        with transaction.atomic():
                            obj = self.build(m, i, attempt, used_o2o)
                            if obj is None: raise ValueError("وابستگی (رکورد والد) پیدا نشد")
                            obj.save()
                            self.fill_m2m(obj, m, i)
                        made += 1; ok = True; break
                    except Exception as e:
                        err = f"{type(e).__name__}: {e}"
                if not ok: errors.append(err)
            report.append((m.__name__, made, errors))
            style = self.style.SUCCESS if made == count else self.style.WARNING
            self.stdout.write(style(f"{m.__name__}: {made}/{count}"))
        self.stdout.write("\n--- خطاها ---")
        for name, made, errs in report:
            if errs: self.stdout.write(self.style.ERROR(f"{name}: {errs[0][:300]}"))

    def build(self, m, i, attempt, used_o2o):
        data = {}
        for f in m._meta.concrete_fields:
            if f.primary_key and (f.auto_created or isinstance(f, models.AutoField)): continue
            if isinstance(f, models.AutoField): continue
            if f.is_relation:
                if f.related_model is m:  # ارجاع به خود (مثل parent)
                    continue
                v = fk_value(f, i, used_o2o)
                if v is None and not f.null: return None
                data[f.name] = v
                continue
            if f.choices:
                data[f.name] = f.choices[(i + attempt) % len(f.choices)][0]; continue
            if f.has_default() and not f.unique and not isinstance(f, models.IntegerField):
                continue
            if f.null or f.blank:
                if not f.unique and not isinstance(f, (models.DateField, models.DecimalField, models.IntegerField)):
                    if f.blank: continue
            v = value_for(f, i, attempt)
            if v is not None: data[f.name] = v
        if m.__name__ == "Term":
            y = 1400 + i // 3
            data["academic_year"] = f"{y}-{y+1}"
            data["term_code"] = f"{y}{i % 3 + 1}"
        if m.__name__ == "CourseOffering":
            import datetime as _dt
            data["start_time"] = _dt.time(8 + i, 0)
            data["end_time"] = _dt.time(9 + i, 30)
            data["capacity"] = 30
            data["remaining_capacity"] = 30
            data.pop("exam_date", None); data.pop("exam_time", None)
        obj = m(**data)
        if m.__name__ == "Person":
            obj.username = f"seed_user{i+1}"
            obj.set_password("Test@12345")
        return obj

    def fill_m2m(self, obj, m, i):
        for f in m._meta.many_to_many:
            if f.remote_field.through._meta.auto_created:
                items = list(f.related_model.objects.all()[:2])
                if items: getattr(obj, f.name).add(*items)
