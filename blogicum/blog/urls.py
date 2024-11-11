"""Urls.py для приложения blog."""
from django.urls import path, include

from . import views

app_name = 'blog'

post_urls = [
    path(
        '<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'),
    path('create/',
         views.PostCreateView.as_view(),
         name='create_post'),
    path('<int:post_id>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'),
    path(
        '<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'),
    path('<int:post_id>/comment/',
         views.add_comment,
         name='add_comment'),
    path('<int:post_id>/edit_comment/<int:comment_id>/',
         views.edit_comment,
         name='edit_comment'),
    path(
        '<int:post_id>/delete_comment/<int:comment_id>/',
        views.delete_comment,
        name='delete_comment'),
]

profile_urls = [
    path(
        'edit/',
        views.ProfileUpdateView.as_view(),
        name='edit_profile'),
    path('<str:username>/',
         views.ProfileList.as_view(),
         name='profile'),
]

urlpatterns = [
    path('', views.PostsList.as_view(), name='index'),
    path('posts/', include(post_urls)),
    path('profile/', include(profile_urls)),
    path(
        'category/<slug:category_slug>/',
        views.CategoryList.as_view(),
        name='category_posts'),
]
