from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView

import requests
from PIL import Image

from .decorators import user_is_not_banned_from_group, user_is_group_admin
from .forms import GroupForm, GroupSubjectForm, CommentForm, GroupSettingsForm
from .models import Group, GroupSubject, Comment
from ..helpers import ajax_required
from ..news.models import News
from ..utils import check_image_extension


class GroupsPageView(ListView):
    """
    ListView implementation to show all available groups.
    """
    model = Group
    queryset = Group.objects.all()
    paginate_by = 20
    template_name = 'groups/group_list.html'
    context_object_name = 'groups'

    def get_queryset(self):
        """Filter out private groups unless user is a member."""
        queryset = super().get_queryset()

        # Filter by category if provided
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Filter by search term if provided
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        # Filter private groups
        if self.request.user.is_authenticated:
            # Include private groups the user is subscribed to
            private_groups = queryset.filter(is_private=True, subscribers=self.request.user)
            public_groups = queryset.filter(is_private=False)
            queryset = public_groups | private_groups
        else:
            # Only public groups for anonymous users
            queryset = queryset.filter(is_private=False)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get categories for filter
        context['categories'] = Group.objects.exclude(category='').values_list(
            'category', flat=True).distinct()
        # Get user's subscribed groups
        if self.request.user.is_authenticated:
            context['user_groups'] = self.request.user.subscribed_groups.all()[:5]
        return context


class GroupPageView(DetailView):
    """
    DetailView implementation to display group details and content using news templates.
    """
    model = Group
    template_name = 'news/news_list.html'  # Changed from 'groups/group.html'
    context_object_name = 'group'
    slug_url_kwarg = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()

        # Check if user is banned
        if self.request.user.is_authenticated and self.request.user in group.banned_users.all():
            context['is_banned'] = True
            return context

        # Check if group is private and user is not subscribed
        if group.is_private and (not self.request.user.is_authenticated or
                                self.request.user not in group.subscribers.all()):
            context['is_private'] = True
            return context

        # Get news for this group instead of subjects
        news_list = News.objects.filter(group=group, reply=False)
        paginator = Paginator(news_list, 10)
        page = self.request.GET.get('page')

        try:
            news_list = paginator.page(page)
        except PageNotAnInteger:
            news_list = paginator.page(1)
        except EmptyPage:
            news_list = paginator.page(paginator.num_pages)

        context['news_list'] = news_list
        context['page_obj'] = news_list  # For pagination
        context['admins'] = group.admins.all()
        context['is_group_context'] = True  # Flag to indicate group context
        context['groups_list'] = self.request.user.subscribed_groups.all()[:5] if self.request.user.is_authenticated else []

        # Check if user is member/admin
        if self.request.user.is_authenticated:
            context['is_member'] = self.request.user in group.subscribers.all()
            context['is_admin'] = self.request.user in group.admins.all()

        return context


class UserSubscriptionListView(LoginRequiredMixin, ListView):
    """
    ListView implementation to show subscribed groups for a user.
    """
    model = Group
    paginate_by = 10
    template_name = 'groups/user_subscription_list.html'
    context_object_name = 'subscriptions'

    def get_queryset(self, **kwargs):
        user = get_object_or_404(User, username=self.request.user)
        return user.subscribed_groups.all()


class UserCreatedGroupsPageView(LoginRequiredMixin, ListView):
    """
    ListView implementation to show groups created by a user.
    """
    model = Group
    paginate_by = 20
    template_name = 'groups/user_created_groups.html'
    context_object_name = 'user_groups'

    def get_queryset(self, **kwargs):
        username = self.kwargs.get('username', self.request.user.username)
        user = get_object_or_404(User, username=username)
        return user.inspected_groups.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get('username', self.request.user.username)
        context['profile_user'] = get_object_or_404(User, username=username)
        return context


@login_required
def new_group(request):
    """
    View that handles group creation.
    """
    if request.method == 'POST':
        group_form = GroupForm(request.POST, request.FILES)
        if group_form.is_valid():
            group = group_form.save()
            # Make creator an admin and subscriber
            group.admins.add(request.user)
            group.subscribers.add(request.user)
            messages.success(request, _('Your group has been created successfully!'))
            return redirect(group.get_absolute_url())
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        group_form = GroupForm()

    return render(request, 'groups/new_group.html', {
        'group_form': group_form,
    })


@login_required
@ajax_required
@user_is_not_banned_from_group
def subscribe(request, group):
    """
    View that handles subscribing/unsubscribing to groups.
    """
    group = get_object_or_404(Group, slug=group)
    user = request.user

    # Check if private group
    if group.is_private and user not in group.subscribers.all() and user not in group.admins.all():
        return JsonResponse({'status': 'error', 'message': _('This is a private group.')})

    if group in user.subscribed_groups.all():
        # Unsubscribe
        group.subscribers.remove(user)
        action = 'unsubscribe'
    else:
        # Subscribe
        group.subscribers.add(user)
        action = 'subscribe'

    return HttpResponse(group.subscribers.count())


@login_required
@user_is_group_admin
def edit_group_cover(request, group):
    """
    View that handles editing a group's cover image.
    """
    group = get_object_or_404(Group, slug=group)
    if request.method == 'POST':
        group_cover = request.FILES.get('cover')
        if group_cover:
            if check_image_extension(group_cover.name):
                if group_cover.size <= 2 * 1024 * 1024:  # 2MB limit
                    group.cover = group_cover
                    group.save()
                    messages.success(request, _('Group cover updated successfully!'))
                    return redirect('groups:group', group=group.slug)
                else:
                    messages.error(request, _('Image file too large. Please keep it under 2MB.'))
            else:
                messages.error(request, _('Unsupported file type. Please use JPEG, PNG or GIF.'))
        else:
            messages.error(request, _('No image file provided.'))

    return render(request, 'groups/edit_group_cover.html', {
        'group': group,
    })


@login_required
@user_is_group_admin
def banned_users(request, group):
    """
    View that displays banned users for group admins.
    """
    group = get_object_or_404(Group, slug=group)
    users = group.banned_users.all()

    paginator = Paginator(users, 20)
    page = request.GET.get('page')

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request, 'groups/banned_users.html', {
        'group': group,
        'users': users,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': users,
    })


@login_required
@user_is_group_admin
def ban_user(request, group, user_id):
    """
    View that handles banning/unbanning users from a group.
    """
    group = get_object_or_404(Group, slug=group)
    user = get_object_or_404(User, id=user_id)

    # Check if admin
    if user in group.admins.all():
        messages.error(request, _('Cannot ban an admin from the group.'))
        return redirect('groups:group', group=group.slug)

    if user in group.banned_users.all():
        # Unban the user
        group.banned_users.remove(user)
        messages.success(request, _(f'User {user.username} has been unbanned from this group.'))
    else:
        # Ban the user
        group.subscribers.remove(user)
        group.banned_users.add(user)
        messages.success(request, _(f'User {user.username} has been banned from this group.'))

    # Redirect back to banned users or referer
    referer = request.META.get('HTTP_REFERER')
    if 'banned_users' in referer:
        return redirect('groups:banned_users', group=group.slug)
    return redirect('groups:group', group=group.slug)


@login_required
@user_is_not_banned_from_group
def create_subject(request, group):
    """
    View that handles creating a new subject/post in a group.
    """
    group = get_object_or_404(Group, slug=group)

    # Check if user is a subscriber
    if request.user not in group.subscribers.all():
        messages.error(request, _('You must subscribe to the group to create posts.'))
        return redirect('groups:group', group=group.slug)

    if request.method == 'POST':
        form = GroupSubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.group = group
            subject.author = request.user
            subject.save()
            messages.success(request, _('Your post has been created successfully!'))
            return redirect(subject.get_absolute_url())
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = GroupSubjectForm()

    return render(request, 'groups/create_subject.html', {
        'form': form,
        'group': group,
    })


class SubjectDetailView(DetailView):
    """
    DetailView to display a subject/post and its comments.
    """
    model = GroupSubject
    template_name = 'groups/subject_detail.html'
    context_object_name = 'subject'
    slug_url_kwarg = 'subject'

    def get_object(self):
        group_slug = self.kwargs.get('group')
        subject_slug = self.kwargs.get('subject')
        return get_object_or_404(
            GroupSubject,
            group__slug=group_slug,
            slug=subject_slug
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject = self.get_object()

        # Increment view count
        subject.views_count += 1
        subject.save()

        # Get comments
        comments = subject.comments.all()

        # Pass group for context
        context['group'] = subject.group
        context['comments'] = comments
        context['comment_form'] = CommentForm() if self.request.user.is_authenticated else None

        # Check if user is a member & admin
        if self.request.user.is_authenticated:
            context['is_member'] = self.request.user in subject.group.subscribers.all()
            context['is_admin'] = self.request.user in subject.group.admins.all()
            context['is_author'] = subject.author == self.request.user
            context['has_liked'] = self.request.user in subject.likes.all()

        return context


@login_required
@user_is_not_banned_from_group
def add_comment(request, group, subject):
    """
    View to handle adding comments to a subject.
    """
    subject = get_object_or_404(GroupSubject, group__slug=group, slug=subject)

    # Check if user is a subscriber
    if request.user not in subject.group.subscribers.all():
        messages.error(request, _('You must subscribe to the group to comment.'))
        return redirect(subject.get_absolute_url())

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.subject = subject
            comment.author = request.user
            comment.save()
            messages.success(request, _('Your comment has been added.'))
        else:
            messages.error(request, _('Please correct the errors in your comment.'))

    return redirect(subject.get_absolute_url())


@login_required
@user_is_not_banned_from_group
@ajax_required
def like_subject(request, group, subject):
    """
    View to handle liking/unliking a subject.
    """
    subject = get_object_or_404(GroupSubject, group__slug=group, slug=subject)

    # Check if user is a subscriber
    if request.user not in subject.group.subscribers.all():
        return JsonResponse({
            'status': 'error',
            'message': _('You must subscribe to the group to like posts.')
        })

    if request.user in subject.likes.all():
        # Unlike
        subject.likes.remove(request.user)
        liked = False
    else:
        # Like
        subject.likes.add(request.user)
        liked = True

    return JsonResponse({
        'status': 'success',
        'likes_count': subject.likes.count(),
        'liked': liked
    })


@login_required
@user_is_group_admin
def group_settings(request, group):
    """
    View to handle group settings for admins.
    """
    group = get_object_or_404(Group, slug=group)

    if request.method == 'POST':
        form = GroupSettingsForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, _('Group settings updated successfully!'))
            return redirect('groups:group', group=group.slug)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = GroupSettingsForm(instance=group)

    return render(request, 'groups/group_settings.html', {
        'form': form,
        'group': group,
    })