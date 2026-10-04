from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import CommentForm, PostDescriptionForm, PostForm
from .models import Comment, Like, Post


class PostListMixin(LoginRequiredMixin):
    template_name = "posts/post_list.html"
    context_object_name = "posts"
    paginate_by = 12
    page_title = ""
    empty_message = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["empty_message"] = self.empty_message
        return context


class FeedView(PostListMixin, ListView):
    """Posts from the people the user follows."""

    page_title = "Attività"
    empty_message = "Non ci sono ancora post: segui qualcuno dalla pagina Cerca o da Scopri."

    def get_queryset(self):
        return (
            Post.objects.filter(author__follower_set__follower=self.request.user)
            .with_stats(self.request.user)
            .prefetch_comments()
        )


class DiscoverView(PostListMixin, ListView):
    """Latest posts from everybody else."""

    page_title = "Scopri"
    empty_message = "Nessun post da scoprire per ora."

    def get_queryset(self):
        return (
            Post.objects.exclude(author=self.request.user)
            .with_stats(self.request.user)
            .prefetch_comments()
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = "posts/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Post pubblicato!")
        return response

    def get_success_url(self):
        return reverse_lazy("accounts:profile", args=[self.request.user.username])


class OwnPostsMixin(LoginRequiredMixin, UserPassesTestMixin):
    model = Post
    success_url = reverse_lazy("posts:manage")

    def test_func(self):
        return self.get_object().author_id == self.request.user.id


class PostManageView(LoginRequiredMixin, ListView):
    """Lets the author edit descriptions, delete posts and moderate comments."""

    template_name = "posts/post_manage.html"
    context_object_name = "posts"

    def get_queryset(self):
        return self.request.user.posts.prefetch_comments()


class PostUpdateView(OwnPostsMixin, UpdateView):
    form_class = PostDescriptionForm
    template_name = "posts/post_edit.html"

    def form_valid(self, form):
        messages.success(self.request, "Descrizione aggiornata.")
        return super().form_valid(form)


class PostDeleteView(OwnPostsMixin, DeleteView):
    template_name = "posts/post_confirm_delete.html"

    def form_valid(self, form):
        messages.info(self.request, "Post eliminato.")
        return super().form_valid(form)


@login_required
@require_POST
def like_toggle(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return JsonResponse({"liked": created, "count": post.likes.count()})


@login_required
@require_POST
def comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
    comment = form.save(commit=False)
    comment.post, comment.author = post, request.user
    comment.save()
    html = render_to_string("posts/_comment.html", {"comment": comment}, request=request)
    return JsonResponse({"html": html, "count": post.comments.count()}, status=201)


@login_required
@require_POST
def comment_delete(request, pk):
    """The comment's author and the post's owner may delete a comment."""
    comment = get_object_or_404(Comment.objects.select_related("post"), pk=pk)
    if request.user.id not in (comment.author_id, comment.post.author_id):
        return JsonResponse({"error": "Non autorizzato."}, status=403)
    comment.delete()
    messages.info(request, "Commento eliminato.")
    return redirect("posts:manage")
