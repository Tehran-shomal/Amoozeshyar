"""Assemble each team's page manifest into the portal's safe route registry."""
from django.core.exceptions import ImproperlyConfigured

from . import academic_services, mobina, neyousha_pouya, parsa, shaghayegh
from .metadata import LOGIN_COPY, NAV_GROUPS, SIDEBAR_FOOTER

GROUPS = {
    "mobina": ("مبینا", mobina),
    "shaghayegh": ("شقایق", shaghayegh),
    "academic_services": ("خدمات آموزشی (شاهسوند و امید)", academic_services),
    "parsa": ("پارسا", parsa),
    "neyousha_pouya": ("پویا و نیوشا (لید فرانت)", neyousha_pouya),
}

# These two pages are reached from their owning page, not from the five nav groups.
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
