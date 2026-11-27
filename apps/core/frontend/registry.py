"""Assemble each team's page manifest into the portal's safe route registry."""
from django.core.exceptions import ImproperlyConfigured

from . import miri, mobina, niousha, omid, parsa, shahsvand, shaghayegh
from .metadata import LOGIN_COPY, NAV_GROUPS, SIDEBAR_FOOTER

GROUPS = {
    "mobina": ("مبینا", mobina),
    "shaghayegh": ("شقایق", shaghayegh),
    "parsa": ("پارسا", parsa),
    "omid": ("امید", omid),
    "niousha": ("نیوشا (لید فرانت)", niousha),
    "shahsvand": ("شاهسوند", shahsvand),
    "miri": ("میری (هماهنگ‌کنندهٔ مشترک)", miri),
}

# These pages are opened from their parent workflow rather than the main menu.
HIDDEN_PAGE_SLUGS = frozenset({"selected-courses", "evaluation-form"})


def _collect_pages():
    """Reject duplicate, missing, or stray route declarations at startup."""
    pages = {}
    duplicates = set()
    for owner, (_, module) in GROUPS.items():
        for slug, definition in module.PAGES.items():
            if slug in pages:
                duplicates.add(slug)
            else:
                pages[slug] = {**definition, "owner": owner}

    visible_slugs = {
        item["slug"]
        for group in NAV_GROUPS
        for item in group["items"]
        if item["slug"]
    }
    expected_slugs = visible_slugs | HIDDEN_PAGE_SLUGS
    missing = expected_slugs - pages.keys()
    stray = pages.keys() - expected_slugs
    if duplicates or missing or stray:
        details = []
        if duplicates:
            details.append(f"duplicate pages: {sorted(duplicates)}")
        if missing:
            details.append(f"unassigned pages: {sorted(missing)}")
        if stray:
            details.append(f"pages absent from navigation: {sorted(stray)}")
        raise ImproperlyConfigured("Invalid frontend page ownership; " + "; ".join(details))
    return pages


PAGES = _collect_pages()
OWNERS = {owner: tuple(module.PAGES) for owner, (_, module) in GROUPS.items()}


def build_page(slug, student, term, request):
    owner = PAGES[slug]["owner"]
    return GROUPS[owner][1].build(slug, student, term, request)
