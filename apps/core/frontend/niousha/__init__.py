"""Niousha's schedule, classes, and exam pages; frontend lead module."""

from .pages import COMPONENTS, PAGES


def build(slug, student, term, request):
    from .selectors import build as build_page

    return build_page(slug, student, term, request)
