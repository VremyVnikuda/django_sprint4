from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import (DeleteView, DetailView, CreateView,
                                  ListView, UpdateView)
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import Http404

from .models import Post, Category, Comment
from .forms import CustomUserForm, CommentForm, PostForm

POST_PER_PAGE: int = 10

User = get_user_model()


class CommentSuccessUrlMixin:
    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.object.post.pk])


class IndexListView(ListView):
    paginate_by = POST_PER_PAGE
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')


class PostDetailView(UserPassesTestMixin, DetailView):
    template_name = 'blog/detail.html'
    model = Post
    pk_url_kwarg = 'id'

    def test_func(self):
        self.object = get_object_or_404(self.model,
                                        pk=self.kwargs[self.pk_url_kwarg])
        return (self.object.author == self.request.user
                or (self.object.is_published
                    and self.object.category.is_published
                    and self.object.pub_date <= timezone.now()))

    def handle_no_permission(self):
        raise Http404("This post is not available.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(
            post=context['post']).order_by('created_at')
        context['form'] = CommentForm()

        return context


class CategoryPostsListView(ListView):
    paginate_by = POST_PER_PAGE
    template_name = 'blog/category.html'
    model = Post

    def get_queryset(self, **kwargs):
        category_slug = self.kwargs['category_slug']
        self.category = get_object_or_404(Category,
                                          slug=category_slug,
                                          is_published=True)

        return Post.objects.filter(
            category=self.category,
            is_published=True,
            pub_date__lte=timezone.now()
        ).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileListView(ListView):
    template_name = 'blog/profile.html'
    model = Post
    paginate_by = POST_PER_PAGE

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(author=user).annotate(
            comment_count=Count('comments')).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username'])
        return context


class EditProfileListView(UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = CustomUserForm

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.request.user.username)

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.title = form.cleaned_data['title']
        post.save()
        return redirect('blog:profile', username=self.request.user.username)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username})


class EditPostView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        post = self.get_object()
        return HttpResponseRedirect(reverse_lazy('blog:post_detail',
                                                 args=[post.pk]))

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs[self.pk_url_kwarg])

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.object.pk])


class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=[self.request.user.username])

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id, author=self.request.user)
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=context['post'])
        return context


class CommentCreateView(LoginRequiredMixin, CommentSuccessUrlMixin,
                        CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, CommentSuccessUrlMixin,
                        UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        post_id = self.kwargs.get('post_id')
        comment_id = self.kwargs.get('comment_id')
        comment = get_object_or_404(
            Comment, post__pk=post_id, pk=comment_id, author=self.request.user)
        return comment


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return (self.request.user == comment.author
                or self.request.user.is_staff)

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse_lazy('blog:post_detail', args=[post_id])
