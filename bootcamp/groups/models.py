from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models
from django.db.models.signals import m2m_changed
from django.utils import timezone

from slugify import UniqueSlugify


class Group(models.Model):
    """
    Model that represents a group.
    """
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, null=True, blank=True)
    description = models.TextField(max_length=500)
    cover = models.ImageField(
        upload_to='group_covers/', blank=True, null=True
    )
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='inspected_groups')
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='subscribed_groups')
    banned_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='forbidden_groups')
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    # New fields to enhance group functionality
    category = models.CharField(max_length=50, blank=True, null=True,
                                choices=[
                                    ('technology', 'Technology'),
                                    ('arts_culture', 'Arts & Culture'),
                                    ('sports', 'Sports'),
                                    ('science', 'Science'),
                                    ('business', 'Business'),
                                    ('lifestyle', 'Lifestyle'),
                                    ('other', 'Other'),
                                ], default='other')
    is_private = models.BooleanField(default=False,
                                     help_text="Private groups are only visible to members")

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        """Unicode representation for a group model."""
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = group_slugify(f"{self.title}")

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return absolute url for a group."""
        return reverse('groups:group',
                       args=[self.slug])

    def get_admins(self):
        """Return admins of a group."""
        return self.admins.all()

    def get_picture(self):
        """Return cover url (if any) of a group."""
        default_picture = settings.STATIC_URL + 'img/cover.png'
        if self.cover:
            return self.cover.url
        else:
            return default_picture

    def recent_posts(self):
        """
        Counts number of posts posted within last 3 days in a group.
        """
        return self.subjects.filter(created__gte=timezone.now() - timedelta(days=3)).count()

    def total_posts(self):
        """Return total number of posts in the group."""
        return self.subjects.count()

    def get_subscribers_count(self):
        """Return number of subscribers to the group."""
        return self.subscribers.count()

    def get_similar_groups(self, limit=5):
        """Return similar groups based on category."""
        return Group.objects.filter(category=self.category).exclude(id=self.id)[:limit]


class GroupSubject(models.Model):
    """
    Model to represent posts/subjects within a group.
    """
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, null=True, blank=True)
    description = models.TextField(max_length=2000)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='subjects')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='group_posts')
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_subjects', blank=True)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = subject_slugify(f"{self.title}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('groups:subject_detail', args=[self.group.slug, self.slug])

    def get_likes_count(self):
        return self.likes.count()

    def get_comments_count(self):
        return self.comments.count()


class Comment(models.Model):
    """
    Model to represent comments on group subjects.
    """
    subject = models.ForeignKey(GroupSubject, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.subject.title}'


def admins_changed(sender, **kwargs):
    """
    Signals the Group to not assign more than 3 admins to a group.
    """
    if kwargs['instance'].admins.count() > 3:
        raise ValidationError("You can't assign more than three admins.")


m2m_changed.connect(admins_changed, sender=Group.admins.through)  # noqa: E305


def group_unique_check(text, uids):
    if text in uids:
        return False
    return not Group.objects.filter(slug=text).exists()


group_slugify = UniqueSlugify(
    unique_check=group_unique_check,
    to_lower=True,
    max_length=80,
    separator='_',
    capitalize=False
)


def subject_unique_check(text, uids):
    if text in uids:
        return False
    return not GroupSubject.objects.filter(slug=text).exists()


subject_slugify = UniqueSlugify(
    unique_check=subject_unique_check,
    to_lower=True,
    max_length=80,
    separator='_',
    capitalize=False
)