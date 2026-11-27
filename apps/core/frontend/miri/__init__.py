"""Miri's faculty communications, announcements, and general services."""

from .pages import PAGES


def build(slug, student, term, request):
    from .selectors import build as build_page

    return build_page(slug, student, term, request)
