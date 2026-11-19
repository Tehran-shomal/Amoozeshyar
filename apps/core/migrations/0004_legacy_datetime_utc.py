"""Convert retained naive timestamps to UTC after their source timezone is set."""

from datetime import timezone as datetime_timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
from django.db import migrations, models
from django.db.migrations.recorder import MigrationRecorder
from django.utils import timezone


STATUS_ROWS_CREATED_BY_BRANCH_MIGRATIONS = {
    "0002_enrollment_statuses": {
        ("enrollment_status", "registered"),
        ("enrollment_status", "dropped"),
    },
    "0003_request_workflow_statuses": {
        (category, code)
        for category in (
            "review_status",
            "proposal_status",
            "appeal_status",
            "thesis_review_status",
        )
        for code in ("submitted", "in_review", "approved", "rejected")
    },
}


def _created_with_migration(created_at, applied_at):
    """Identify rows created by a data migration rather than the legacy app."""
    if timezone.is_naive(created_at) or timezone.is_naive(applied_at):
        return False
    seconds = (applied_at - created_at).total_seconds()
    return 0 <= seconds <= 60


def _to_utc(value, source_timezone):
    """Interpret a pre-USE_TZ database value in its old timezone and return UTC."""
    if value is None:
        return None

    local_zone = ZoneInfo(source_timezone)
    local_wall_time = value.replace(tzinfo=None)
    local_value = local_wall_time.replace(tzinfo=local_zone, fold=0)
    alternate_fold = local_wall_time.replace(tzinfo=local_zone, fold=1)

    if local_value.utcoffset() != alternate_fold.utcoffset():
        raise RuntimeError(
            f"Ambiguous legacy datetime {local_wall_time!s} in {source_timezone}; "
            "resolve it before applying this migration."
        )

    round_trip = (
        local_value.astimezone(datetime_timezone.utc)
        .astimezone(local_zone)
        .replace(tzinfo=None)
    )
    if round_trip != local_wall_time:
        raise RuntimeError(
            f"Nonexistent legacy datetime {local_wall_time!s} in {source_timezone}; "
            "resolve it before applying this migration."
        )
    return local_value.astimezone(datetime_timezone.utc)


def _branch_status_ids(apps, schema_editor):
    Constant = apps.get_model("core", "Constant")
    database = schema_editor.connection.alias
    recorder = MigrationRecorder(schema_editor.connection)
    applied_at = dict(
        recorder.migration_qs.filter(
            app="core", name__in=STATUS_ROWS_CREATED_BY_BRANCH_MIGRATIONS
        ).values_list("name", "applied")
    )
    if not applied_at:
        return set()

    ids = set()
    for migration_name, pairs in STATUS_ROWS_CREATED_BY_BRANCH_MIGRATIONS.items():
        migration_time = applied_at.get(migration_name)
        if migration_time is None:
            continue
        for category, code in pairs:
            rows = Constant.objects.using(database).filter(category=category, code=code)
            ids.update(
                row.pk
                for row in rows.only("pk", "created_at").iterator()
                if _created_with_migration(row.created_at, migration_time)
            )
    return ids


def forwards(apps, schema_editor):
    database = schema_editor.connection.alias
    connection = schema_editor.connection
    branch_status_ids = _branch_status_ids(apps, schema_editor)
    date_fields = []
    with connection.cursor() as cursor:
        tables = set(connection.introspection.table_names(cursor))
        columns_by_table = {
            table: {
                column.name
                for column in connection.introspection.get_table_description(cursor, table)
            }
            for table in tables
        }

    for model in apps.get_models():
        table = model._meta.db_table
        if table not in tables:
            continue
        for field in model._meta.local_fields:
            if not isinstance(field, models.DateTimeField):
                continue
            if field.column not in columns_by_table[table]:
                continue
            queryset = model._base_manager.using(database)
            if model._meta.label_lower == "core.constant" and field.name == "created_at":
                queryset = queryset.exclude(pk__in=branch_status_ids)
            if queryset.exclude(**{f"{field.name}__isnull": True}).exists():
                date_fields.append((model, field))

    if not date_fields:
        return

    source_timezone = getattr(settings, "LEGACY_DATETIME_TIME_ZONE", "").strip()
    if not source_timezone:
        raise RuntimeError(
            "Existing DateTimeField values were found while converting to UTC. "
            "Set LEGACY_DATETIME_TIME_ZONE to the timezone used by the old database "
            "before running migrate; no values have been changed."
        )
    try:
        ZoneInfo(source_timezone)
    except ZoneInfoNotFoundError as error:
        raise RuntimeError(
            f"LEGACY_DATETIME_TIME_ZONE={source_timezone!r} is not a valid IANA timezone."
        ) from error

    for model, field in date_fields:
        queryset = model._base_manager.using(database)
        if model._meta.label_lower == "core.constant" and field.name == "created_at":
            queryset = queryset.exclude(pk__in=branch_status_ids)
        queryset = queryset.exclude(**{f"{field.name}__isnull": True}).only("pk", field.name)
        batch = []
        for instance in queryset.iterator(chunk_size=500):
            value = getattr(instance, field.name)
            setattr(instance, field.name, _to_utc(value, source_timezone))
            batch.append(instance)
            if len(batch) == 500:
                model._base_manager.using(database).bulk_update(
                    batch, [field.name], batch_size=500
                )
                batch.clear()
        if batch:
            model._base_manager.using(database).bulk_update(
                batch, [field.name], batch_size=500
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0003_request_workflow_statuses")]

    operations = [migrations.RunPython(forwards)]
