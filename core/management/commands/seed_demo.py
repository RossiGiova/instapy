"""Fill the database with invented demo profiles, photos, likes, comments and follows.

    python manage.py seed_demo            # add the demo data (idempotent)
    python manage.py seed_demo --reset    # delete the demo users first, then recreate

All images are generated locally (see core/demo_images.py): no downloads needed.
"""

import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Follow, User
from core import demo_images
from core.demo_data import LEGACY_USERNAMES, PERSONAS
from posts.models import Comment, Like, Post

DEMO_PASSWORD = "demo-pass-123"


class Command(BaseCommand):
    help = "Create demo users with posts, follows, likes and comments."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete the demo users (and their data) first.")

    @transaction.atomic
    def handle(self, *args, **options):
        usernames = [p["username"] for p in PERSONAS]
        if options["reset"]:
            User.objects.filter(username__in=usernames + LEGACY_USERNAMES).delete()

        rng = random.Random(42)
        now = timezone.now()
        users, created_posts = {}, []

        for index, persona in enumerate(PERSONAS):
            user, created = User.objects.get_or_create(
                username=persona["username"],
                defaults=dict(
                    first_name=persona["first_name"], last_name=persona["last_name"],
                    email=f"{persona['username']}@example.com", bio=persona["bio"],
                    verified=persona["verified"], birth_date="1998-05-20",
                ),
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.avatar.save(f"{persona['username']}.jpg", demo_images.avatar(persona["avatar"], index), save=False)
                user.save()
            users[persona["username"]] = user

            if user.posts.exists():
                continue
            for number, (scene, options_, description) in enumerate(persona["posts"]):
                post = Post.objects.create(
                    author=user, description=description,
                    image=demo_images.render(scene, seed=index * 100 + number, **options_),
                )
                # Spread the posts over the last weeks so feeds look natural.
                stamp = now - timedelta(days=rng.randint(0, 30), hours=rng.randint(0, 23))
                Post.objects.filter(pk=post.pk).update(created_at=stamp)
                created_posts.append((post, persona))

        everyone = list(users.values())
        for user in everyone:
            others = [u for u in everyone if u != user]
            for other in rng.sample(others, k=rng.randint(3, 5)):
                Follow.objects.get_or_create(follower=user, following=other)

        for post, persona in created_posts:
            others = [u for u in everyone if u != post.author]
            for liker in rng.sample(others, k=rng.randint(2, len(others))):
                Like.objects.get_or_create(user=liker, post=post)
            for commenter, text in zip(rng.sample(others, k=rng.randint(1, 3)), rng.sample(persona["reactions"], k=3)):
                comment = Comment.objects.create(author=commenter, post=post, text=text)
                stamp = post.created_at + timedelta(hours=rng.randint(1, 48))
                Comment.objects.filter(pk=comment.pk).update(created_at=min(stamp, now))

        self.stdout.write(self.style.SUCCESS(
            f"Demo data ready: {len(everyone)} profiles. Log in as {', '.join(usernames)} "
            f"with password '{DEMO_PASSWORD}'."
        ))
