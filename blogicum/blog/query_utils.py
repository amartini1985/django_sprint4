"""Агрегирующие функции для запросов."""
from django.db.models import Count
from django.utils import timezone

from .models import Post


def get_posts(manager=Post.objects, filter_flag=False, annotate_flag=False):
    """Функция определяющая базовый запрос для всех пользователей."""
    queryset = manager.select_related(
        'category',
        'author',
        'location')
    if filter_flag:
        queryset = queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True)
    if annotate_flag:
        queryset = queryset.annotate(
            comment_count=Count('comments')).order_by('-pub_date',)
    return queryset
