import shutil
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Follow
from core.testing import make_image, make_post, make_user
from posts.models import Comment, Like, Post

TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class PostTestCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.user = make_user("mario")
        self.other = make_user("luigi")
        self.client.force_login(self.user)


class PostCrudTests(PostTestCase):
    def test_create_post_sets_author(self):
        response = self.client.post(reverse("posts:create"), {"image": make_image(), "description": "ciao"})
        self.assertRedirects(response, reverse("accounts:profile", args=["mario"]), fetch_redirect_response=False)
        post = Post.objects.get()
        self.assertEqual((post.author, post.description), (self.user, "ciao"))

    def test_create_rejects_non_images(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        fake = SimpleUploadedFile("evil.jpg", b"not an image", content_type="image/jpeg")
        response = self.client.post(reverse("posts:create"), {"image": fake})
        self.assertEqual(Post.objects.count(), 0)
        self.assertIn("image", response.context["form"].errors)

    def test_owner_can_edit_and_delete(self):
        post = make_post(self.user)
        self.client.post(reverse("posts:edit", args=[post.pk]), {"description": "nuova"})
        post.refresh_from_db()
        self.assertEqual(post.description, "nuova")
        self.client.post(reverse("posts:delete", args=[post.pk]))
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())

    def test_others_cannot_edit_or_delete(self):
        post = make_post(self.other)
        self.assertEqual(self.client.get(reverse("posts:edit", args=[post.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse("posts:edit", args=[post.pk]), {"description": "x"}).status_code, 403)
        self.assertEqual(self.client.post(reverse("posts:delete", args=[post.pk])).status_code, 403)
        self.assertTrue(Post.objects.filter(pk=post.pk).exists())


class FeedTests(PostTestCase):
    def test_feed_only_contains_followed_users(self):
        third = make_user("peach")
        followed, not_followed = make_post(self.other), make_post(third)
        Follow.objects.create(follower=self.user, following=self.other)
        posts = list(self.client.get(reverse("posts:feed")).context["posts"])
        self.assertEqual(posts, [followed])
        self.assertNotIn(not_followed, posts)

    def test_discover_excludes_own_posts(self):
        make_post(self.user)
        theirs = make_post(self.other)
        self.assertEqual(list(self.client.get(reverse("posts:discover")).context["posts"]), [theirs])

    def test_listing_uses_a_constant_number_of_queries(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        Follow.objects.create(follower=self.user, following=self.other)
        for _ in range(2):
            make_post(self.other)
        with CaptureQueriesContext(connection) as small:
            self.client.get(reverse("posts:feed"))
        for _ in range(6):
            post = make_post(self.other)
            Like.objects.create(user=self.user, post=post)
            Comment.objects.create(author=self.user, post=post, text="x")
        with CaptureQueriesContext(connection) as big:
            self.client.get(reverse("posts:feed"))
        self.assertEqual(len(small), len(big))  # no N+1

    def test_feed_is_newest_first(self):
        Follow.objects.create(follower=self.user, following=self.other)
        old, new = make_post(self.other, "old"), make_post(self.other, "new")
        self.assertEqual(list(self.client.get(reverse("posts:feed")).context["posts"]), [new, old])


class InteractionTests(PostTestCase):
    def setUp(self):
        super().setUp()
        self.post = make_post(self.other)

    def test_like_toggle_returns_state_and_count(self):
        url = reverse("posts:like", args=[self.post.pk])
        self.assertEqual(self.client.post(url).json(), {"liked": True, "count": 1})
        self.assertEqual(self.client.post(url).json(), {"liked": False, "count": 0})

    def test_like_requires_post_and_login(self):
        url = reverse("posts:like", args=[self.post.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.logout()
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertEqual(Like.objects.count(), 0)

    def test_comment_create_returns_rendered_html(self):
        response = self.client.post(reverse("posts:comment", args=[self.post.pk]), {"text": "bella <b>foto</b>"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("bella &lt;b&gt;foto&lt;/b&gt;", response.json()["html"])  # escaped, no XSS
        self.assertEqual(self.post.comments.count(), 1)

    def test_empty_or_too_long_comment_is_rejected(self):
        url = reverse("posts:comment", args=[self.post.pk])
        self.assertEqual(self.client.post(url, {"text": ""}).status_code, 400)
        self.assertEqual(self.client.post(url, {"text": "x" * 201}).status_code, 400)

    def test_comment_deletion_permissions(self):
        mine = Comment.objects.create(author=self.user, post=self.post, text="mine")
        stranger = make_user("peach")
        theirs = Comment.objects.create(author=stranger, post=self.post, text="peach's")
        # Mario is neither author of `theirs` nor owner of the post -> forbidden
        self.assertEqual(self.client.post(reverse("posts:comment-delete", args=[theirs.pk])).status_code, 403)
        # ...but may delete his own comment
        self.client.post(reverse("posts:comment-delete", args=[mine.pk]))
        self.assertFalse(Comment.objects.filter(pk=mine.pk).exists())
        # the post owner may delete anyone's comment on their post
        self.client.force_login(self.other)
        self.client.post(reverse("posts:comment-delete", args=[theirs.pk]))
        self.assertFalse(Comment.objects.filter(pk=theirs.pk).exists())


class HomeTests(PostTestCase):
    def test_home_redirects_logged_in_users_to_feed(self):
        self.assertRedirects(self.client.get(reverse("core:home")), reverse("posts:feed"), fetch_redirect_response=False)

    def test_landing_page_works_with_an_empty_database(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("core:home")).status_code, 200)

    def test_landing_page_with_posts(self):
        for _ in range(5):
            make_post(self.other)
        self.client.logout()
        self.assertEqual(self.client.get(reverse("core:home")).status_code, 200)
