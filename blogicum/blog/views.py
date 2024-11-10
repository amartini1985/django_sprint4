"""Views.py для приложения blog."""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView
from django.views.generic import ListView, UpdateView

from blogicum.settings import NUMBER_OF_POSTS

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User
from .utils import get_posts


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин для проверки авторства."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class PostDetailView(DetailView):
    """CBV вывода отдельных постов."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = get_object_or_404(
            get_posts(),
            pk=self.kwargs[self.pk_url_kwarg]
        )
        if post.author == self.request.user:
            post = get_object_or_404(
                get_posts(),
                pk=self.kwargs[self.pk_url_kwarg]
            )
        else:
            post = get_object_or_404(
                get_posts(filter_flag=True),
                pk=self.kwargs[self.pk_url_kwarg]
            )
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.all().filter(
            post=self.kwargs['post_id']
        ).order_by('created_at')
        return context


class PostsList(ListView):
    """CBV вывода постов на главную страницу."""

    model = Post
    context_object_name = 'post_obj'
    template_name = 'blog/index.html'
    paginate_by = NUMBER_OF_POSTS

    def get_queryset(self):
        return get_posts(filter_flag=True, annotate_flag=True)


class CategoryList(ListView):
    """CBV вывода постов в категории."""

    model = Post
    context_object_name = 'post_obj'
    template_name = 'blog/category.html'
    paginate_by = NUMBER_OF_POSTS

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return get_posts(filter_flag=True).filter(
            category__slug=category.slug
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class ProfileList(ListView):
    """CBV вывода постов на странице профиле пользователя."""

    model = Post
    context_object_name = 'post_obj'
    template_name = 'blog/profile.html'
    paginate_by = NUMBER_OF_POSTS

# Не уверен что это оптимальный вариант, но по другому не придумал
    def get_queryset(self):
        profile = get_object_or_404(
            User,
            username=self.kwargs['slug']
        )
        if str(self.request.user) == self.kwargs['slug']:
            return get_posts(annotate_flag=True).filter(
                author__username=profile.username)
        else:
            return get_posts(annotate_flag=True).filter(
                author__username=profile.username,
                is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['slug']
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """CBV создания поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """CBV редактирования поста."""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """CBV удаления поста."""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.get_object()
        form = PostForm(instance=instance)
        context['form'] = form
        return context

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'slug': self.request.user})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """CBV редактирования профиля."""

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
    """Функция для добавления комментариев."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Функция для редактирования комментариев."""
    instance = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(request.POST or None, instance=instance)
    context = {'form': form, 'comment': instance}
    if form.is_valid() and request.user == instance.author:
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    elif request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Функция для удаления комментариев."""
    instance = get_object_or_404(Comment, pk=comment_id)
    context = {'comment': instance}
    if request.method == 'POST' and request.user == instance.author:
        instance.delete()
        return redirect('blog:post_detail', post_id=post_id)
    elif request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)
