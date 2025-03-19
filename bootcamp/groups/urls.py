# urls.py - Add these paths to complete your groups functionality

from django.urls import path

from . import views

app_name = "groups"
urlpatterns = [
    path('all/', view=views.GroupsPageView.as_view(), name='list'),
    path('new/', views.new_group, name='new_group'),  # New group creation URL
    path('subscriptions/', views.UserSubscriptionListView.as_view(), name='user_subscription_list'),
    path('ban_user/<slug:group>/<int:user_id>/', views.ban_user, name='ban_user'),
    path('banned_users/<slug:group>/', views.banned_users, name='banned_users'),
    path('user/<str:username>/', views.UserCreatedGroupsPageView.as_view(), name='user_created_groups'),
    path('<slug:group>/', views.GroupPageView.as_view(), name='group'),
    path('<slug:group>/edit_group_cover/', views.edit_group_cover, name='edit_group_cover'),
    path('<slug:group>/subscription/', views.subscribe, name='subscribe'),
]