"""Shahsvand's student request workflows."""

from .pages import PAGES


def build(slug, student, term, request):
    from .selectors import build as build_page

    return build_page(slug, student, term, request)
