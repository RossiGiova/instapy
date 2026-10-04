from django.shortcuts import redirect
from django.views.generic import TemplateView

from posts.models import Post


class HomeView(TemplateView):
    """Landing page for visitors; logged-in users go straight to their feed."""

    template_name = "core/home.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("posts:feed")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest = list(Post.objects.with_stats().prefetch_comments()[:5])
        context["hero_post"] = latest[0] if latest else None
        context["featured_post"] = latest[1] if len(latest) > 1 else None
        context["gallery"] = latest[2:5]
        return context
