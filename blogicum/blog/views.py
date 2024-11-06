from django.db.models import Count

from django.shortcuts import get_object_or_404, render, redirect

from django.contrib.auth.decorators import login_required

from django.utils import timezone

from django.urls import reverse_lazy

from django.views.generic import (
    CreateView, DeleteView, UpdateView,
    DetailView, ListView
)

from .forms import PostForm, UserForm, CommentForm

from blog.models import Category, Post, User, Comment

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.mixins import UserPassesTestMixin

COUNT_POSTS = 5  # Число постов при выводе


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

'''
def post_detail(request, pk):
    post = get_object_or_404(
        get_posts(),
        pk=pk)
    comments = Comment.objects.all()
    context = {'post': post, 'form': CommentForm(), 'comments': comments}
    return render(request, 'blog/detail.html', context)
'''
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.all().filter(
            post=self.kwargs['pk']
        )
        return context

class PostsList(ListView):
    model = Post
    context_object_name = 'post_obj'
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return get_posts().annotate(comment_count=Count('comment')).order_by('-pub_date')

'''
def index(request):
    paginator = Paginator(get_posts(), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)
'''

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
''''
def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    page_list = get_posts().filter(category__slug=category_slug)
    paginator = Paginator(page_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, 'blog/category.html', context)
'''
class ProfileList(ListView):
    model = Post
    context_object_name = 'post_obj'
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.select_related(
        'category',
        'author',
        'location').filter(author__username=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['slug']
        )
        return context        
'''
def profile(request, slug):
    profile = get_object_or_404(
        User,
        username=slug
    )
    profile_list = Post.objects.select_related(
        'category',
        'author',
        'location').filter(author__username=slug)
    paginator = Paginator(profile_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'profile': profile}
    return render(request, 'blog/profile.html', context)
'''

class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    #success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    

class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm



class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserForm
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(request.POST or None, instance=instance)
    context = {'form': form, 'comment': instance}
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(instance=instance)
    context = {'form': form, 'comment': instance}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)
