import shutil
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User
from core.testing import make_image, make_user

TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class AuthTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    signup_data = {
        "first_name": "Mario", "last_name": "Rossi", "email": "Mario@Example.com",
        "birth_date": "2000-05-01", "username": "Mario.Rossi", "gender": "M",
        "password1": "Sup3r-secret-pw", "password2": "Sup3r-secret-pw",
    }

    def test_signup_creates_lowercase_user_and_logs_in(self):
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertRedirects(response, reverse("accounts:me"), fetch_redirect_response=False)
        user = User.objects.get()
        self.assertEqual(user.username, "mario.rossi")
        self.assertEqual(user.email, "mario@example.com")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_signup_rejects_duplicate_nickname_case_insensitively(self):
        make_user("mario.rossi")
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(response, "già in uso")

    def test_signup_rejects_weak_password_and_future_birth_date(self):
        data = {**self.signup_data, "password1": "12345678", "password2": "12345678", "birth_date": "2999-01-01"}
        response = self.client.post(reverse("accounts:signup"), data)
        self.assertEqual(User.objects.count(), 0)
        self.assertTrue(response.context["form"].errors["password2"])
        self.assertTrue(response.context["form"].errors["birth_date"])

    def test_nickname_cannot_be_only_digits(self):
        response = self.client.post(reverse("accounts:signup"), {**self.signup_data, "username": "12345"})
        self.assertIn("username", response.context["form"].errors)

    def test_login_is_case_insensitive_and_shows_error_on_failure(self):
        make_user("mario", password="Sup3r-secret-pw")
        ok = self.client.post(reverse("accounts:login"), {"username": "MARIO", "password": "Sup3r-secret-pw"})
        self.assertEqual(ok.status_code, 302)
        self.client.logout()
        bad = self.client.post(reverse("accounts:login"), {"username": "mario", "password": "wrong"})
        self.assertEqual(bad.status_code, 200)
        self.assertTrue(bad.context["form"].non_field_errors())

    def test_logout_requires_post(self):
        make_user()
        self.client.login(username="mario", password="Sup3r-secret-pw")
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        self.client.post(reverse("accounts:logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_private_pages_redirect_anonymous_users_to_login(self):
        for name in ("accounts:me", "accounts:settings", "accounts:search", "posts:feed", "posts:discover", "posts:create"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, name)
            self.assertIn(reverse("accounts:login"), response["Location"], name)


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class ProfileTests(TestCase):
    def setUp(self):
        self.user = make_user("mario")
        self.other = make_user("luigi")
        self.client.force_login(self.user)

    def test_update_profile_with_avatar(self):
        response = self.client.post(reverse("accounts:settings"), {
            "first_name": "Mario", "last_name": "Bros", "username": "Mario2", "email": "m2@example.com",
            "bio": "ciao", "avatar": make_image(),
        })
        self.assertRedirects(response, reverse("accounts:profile", args=["mario2"]), fetch_redirect_response=False)
        self.user.refresh_from_db()
        self.assertEqual((self.user.username, self.user.bio), ("mario2", "ciao"))
        self.assertTrue(self.user.avatar.name.startswith("avatars/"))

    def test_cannot_take_someone_elses_nickname_or_email(self):
        response = self.client.post(reverse("accounts:settings"), {
            "first_name": "M", "last_name": "B", "username": "LUIGI", "email": self.other.email.upper(),
        })
        errors = response.context["form"].errors
        self.assertIn("username", errors)
        self.assertIn("email", errors)

    def test_search_finds_users_by_partial_nickname(self):
        response = self.client.get(reverse("accounts:search"), {"q": "UIG"})
        self.assertEqual([u.username for u in response.context["results"]], ["luigi"])

    def test_delete_account_requires_correct_password(self):
        bad = self.client.post(reverse("accounts:delete"), {"password": "nope"})
        self.assertEqual(bad.status_code, 200)
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
        self.client.post(reverse("accounts:delete"), {"password": "Sup3r-secret-pw"})
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_default_avatar_is_used_when_none_uploaded(self):
        self.assertIn("default-avatar", self.user.avatar_url)


class FollowTests(TestCase):
    def setUp(self):
        self.user = make_user("mario")
        self.other = make_user("luigi")
        self.client.force_login(self.user)
        self.url = reverse("accounts:follow", args=["luigi"])

    def test_follow_toggle(self):
        first = self.client.post(self.url).json()
        self.assertEqual(first, {"following": True, "followers": 1})
        second = self.client.post(self.url).json()
        self.assertEqual(second, {"following": False, "followers": 0})

    def test_cannot_follow_yourself(self):
        response = self.client.post(reverse("accounts:follow", args=["mario"]))
        self.assertEqual(response.status_code, 400)

    def test_follow_requires_post(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
