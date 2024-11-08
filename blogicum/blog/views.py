from django.db.models import Count

from django.db.models.query import QuerySet
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect

from django.contrib.auth.decorators import login_required

from django.utils import timezone

from django.urls import reverse

from django.urls import reverse_lazy

from django.views.generic import (
    CreateView, DeleteView, UpdateView,
    DetailView, ListView
)

from .forms import PostForm, UserForm, CommentForm

from blog.models import Category, Post, User, Comment

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.mixins import UserPassesTestMixin


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


def get_posts():
    """Функция определяющая базовые запросы для view-функций."""
    return Post.objects.select_related(
        'category',
        'author',
        'location').filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True)

def get_posts_all():
    """Функция определяющая базовые запросы для view-функций."""
    return Post.objects.select_related(
        'category',
        'author',
        'location')

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.all().filter(
            post=self.kwargs['pk']
        ).order_by('created_at')
        return context

    def get_queryset(self):
        post = get_object_or_404(get_posts_all(), pk=self.kwargs['pk'])
        if (post.author == self.request.user):
            return get_posts_all().filter(pk=self.kwargs['pk'])
        else:
            return get_posts().filter(pk=self.kwargs['pk'])


class PostsList(ListView):
    model = Post
    context_object_name = 'post_obj'
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return get_posts().annotate(
            comment_count=Count('comment')).order_by('-pub_date',)


class CategoryList(ListView):
    model = Post
    context_object_name = 'post_obj'
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        return get_posts().filter(category__slug=self.kwargs['category_slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class ProfileList(ListView):
    model = Post
    context_object_name = 'post_obj'
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        if str(self.request.user) == str(self.kwargs['slug']):
            return Post.objects.select_related(
                'category', 'author', 'location'
            ).filter(
                author__username=self.kwargs['slug']).annotate(
                    comment_count=Count('comment')).order_by('-pub_date')
        else:
            return Post.objects.select_related(
                'category', 'author', 'location'
            ).filter(
                author__username=self.kwargs['slug'],
                is_published=True).annotate(
                    comment_count=Count('comment')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['slug']
        )
        return context


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BlogUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.kwargs['pk'])


class BlogDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.kwargs['pk'])
        form = PostForm(instance=instance)
        context['form'] = form
        return context

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'slug': self.request.user})

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.kwargs['pk'])


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserForm
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'slug': self.request.user})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(request.POST or None, instance=instance)
    context = {'form': form, 'comment': instance}
    if form.is_valid() and request.user == instance.author:
        form.save()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, pk=comment_id)
    context = {'comment': instance}
    if request.method == 'POST' and request.user == instance.author:
        instance.delete()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)
