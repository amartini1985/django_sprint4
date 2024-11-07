from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostsList.as_view(), name='index'),
    path(
        'posts/<int:pk>/',
        views.PostDetailView.as_view(),
        name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.CategoryList.as_view(),
        name='category_posts'),
    path('posts/create/',
         views.BlogCreateView.as_view(),
         name='create_post'),
    path('post/<int:pk>/edit/',
         views.BlogUpdateView.as_view(),
         name='edit_post'),
    path(
        'post/<int:pk>/delete/',
        views.BlogDeleteView.as_view(),
        name='delete_post'),
    path(
        'profile/edit/',
        views.ProfileUpdateView.as_view(),
        name='edit_profile'),
    path('profile/<slug:slug>/',
         views.ProfileList.as_view(),
         name='profile'),
    path('posts/<int:post_id>/comment/',
         views.add_comment,
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.edit_comment,
         name='edit_comment'),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.delete_comment,
        name='delete_comment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
