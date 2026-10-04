import shutil
import tempfile

from django.core.management import call_command
from django.test import TestCase, override_settings

from accounts.models import Follow, User
from core.demo_data import PERSONAS
from posts.models import Comment, Like, Post

TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class SeedDemoTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def test_seed_creates_profiles_posts_and_interactions(self):
        call_command("seed_demo", verbosity=0)
        self.assertEqual(User.objects.count(), len(PERSONAS))
        self.assertEqual(Post.objects.count(), sum(len(p["posts"]) for p in PERSONAS))
        self.assertTrue(Comment.objects.exists() and Like.objects.exists() and Follow.objects.exists())
        self.assertTrue(all(u.avatar for u in User.objects.all()))
        self.assertTrue(User.objects.get(username=PERSONAS[0]["username"]).check_password("demo-pass-123"))

    def test_seed_is_idempotent_and_reset_recreates(self):
        call_command("seed_demo", verbosity=0)
        before = (User.objects.count(), Post.objects.count(), Comment.objects.count())
        call_command("seed_demo", verbosity=0)
        self.assertEqual((User.objects.count(), Post.objects.count(), Comment.objects.count()), before)
        call_command("seed_demo", "--reset", verbosity=0)
        self.assertEqual((User.objects.count(), Post.objects.count()), before[:2])
