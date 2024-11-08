"""Views.py для приложения pages."""

from django.shortcuts import render

from django.views.generic import TemplateView


class About(TemplateView):
    """CBV статичной страницы about."""

    template_name = 'pages/about.html'


class Rules(TemplateView):
    """CBV статичной страницы rules."""

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Функция страницы 404."""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Функция страницы 403."""
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request, *args, **argv):
    """Функция страницы 500."""
    return render(request, 'pages/500.html', status=500)
