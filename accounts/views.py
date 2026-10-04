from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, ListView, RedirectView, UpdateView
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from posts.models import Post

from .forms import AccountDeleteForm, LoginForm, ProfileForm, SignUpForm
from .models import Follow, User


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:me")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Benvenuto su InstaPy!")
        return redirect("accounts:me")


class LoginView(DjangoLoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class MeView(LoginRequiredMixin, RedirectView):
    """/accounts/me/ → the profile of the logged-in user."""

    def get_redirect_url(self, *args, **kwargs):
        return reverse("accounts:profile", args=[self.request.user.username])


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "accounts/profile.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        posts = profile.posts.with_stats(self.request.user).prefetch_comments()
        page = Paginator(posts, settings.POSTS_PER_PAGE).get_page(self.request.GET.get("page"))
        context.update(
            page_obj=page,
            posts=page.object_list,
            post_count=page.paginator.count,
            followers_count=profile.follower_set.count(),
            following_count=profile.following_set.count(),
            is_own_profile=profile == self.request.user,
            is_following=Follow.objects.filter(follower=self.request.user, following=profile).exists(),
        )
        return context


@login_required
@require_POST
def follow_toggle(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({"error": "Non puoi seguire te stesso."}, status=400)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        follow.delete()
    return JsonResponse({"following": created, "followers": target.follower_set.count()})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = "accounts/settings.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, "Profilo aggiornato.")
        return reverse("accounts:profile", args=[self.object.username])


class AccountDeleteView(LoginRequiredMixin, FormView):
    form_class = AccountDeleteForm
    template_name = "accounts/delete.html"
    success_url = reverse_lazy("core:home")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        logout(self.request)
        user.delete()
        messages.info(self.request, "Il tuo account è stato eliminato.")
        return super().form_valid(form)


class UserSearchView(LoginRequiredMixin, ListView):
    template_name = "accounts/search.html"
    context_object_name = "results"
    paginate_by = 20

    def get_queryset(self):
        self.query = self.request.GET.get("q", "").strip()
        if not self.query:
            return User.objects.none()
        return (
            User.objects.filter(username__icontains=self.query)
            .annotate(num_followers=Count("follower_set"))
            .order_by("username")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.query
        return context
