from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from .models import Group, GroupSubject


def user_is_group_admin(f):
    """
    Decorator to ensure a user is a group admin.
    """
    def wrap(request, *args, **kwargs):
        group_slug = kwargs.get('group')
        try:
            group = Group.objects.get(slug=group_slug)
            if request.user in group.admins.all():
                return f(request, *args, **kwargs)
            else:
                messages.error(request, _("You don't have permission to perform this action."))
                return redirect(group.get_absolute_url())
        except Group.DoesNotExist:
            raise PermissionDenied

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def user_is_not_banned_from_group(f):
    """
    Decorator to ensure a user is not banned from a group.
    """
    def wrap(request, *args, **kwargs):
        group_slug = kwargs.get('group')
        try:
            group = Group.objects.get(slug=group_slug)
            if request.user not in group.banned_users.all():
                return f(request, *args, **kwargs)
            else:
                messages.error(request, _("You've been banned from this group."))
                return redirect('groups:list')
        except Group.DoesNotExist:
            raise PermissionDenied

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def user_is_group_member(f):
    """
    Decorator to ensure a user is a member of the group.
    """
    def wrap(request, *args, **kwargs):
        group_slug = kwargs.get('group')
        try:
            group = Group.objects.get(slug=group_slug)
            if request.user in group.subscribers.all():
                return f(request, *args, **kwargs)
            else:
                messages.error(request, _("You must be a member of this group to perform this action."))
                return redirect(group.get_absolute_url())
        except Group.DoesNotExist:
            raise PermissionDenied

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def user_is_subject_author(f):
    """
    Decorator to ensure a user is the author of a subject.
    """
    def wrap(request, *args, **kwargs):
        group_slug = kwargs.get('group')
        subject_slug = kwargs.get('subject')
        try:
            subject = GroupSubject.objects.get(group__slug=group_slug, slug=subject_slug)
            if request.user == subject.author:
                return f(request, *args, **kwargs)
            else:
                messages.error(request, _("You don't have permission to perform this action."))
                return redirect(subject.get_absolute_url())
        except GroupSubject.DoesNotExist:
            raise PermissionDenied

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap