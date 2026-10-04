from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("feed/", views.FeedView.as_view(), name="feed"),
    path("discover/", views.DiscoverView.as_view(), name="discover"),
    path("posts/new/", views.PostCreateView.as_view(), name="create"),
    path("posts/manage/", views.PostManageView.as_view(), name="manage"),
    path("posts/<int:pk>/edit/", views.PostUpdateView.as_view(), name="edit"),
    path("posts/<int:pk>/delete/", views.PostDeleteView.as_view(), name="delete"),
    path("posts/<int:pk>/like/", views.like_toggle, name="like"),
    path("posts/<int:pk>/comments/", views.comment_create, name="comment"),
    path("comments/<int:pk>/delete/", views.comment_delete, name="comment-delete"),
]
