from django.urls import path

from . import views

app_name = "groups"
urlpatterns = [
    # Group listing pages
    path('', views.GroupsPageView.as_view(), name='list'),
    path('new/', views.new_group, name='new_group'),
    path('subscriptions/', views.UserSubscriptionListView.as_view(), name='user_subscription_list'),
    path('user/<str:username>/', views.UserCreatedGroupsPageView.as_view(), name='user_created_groups'),

    # Group administration
    path('<slug:group>/edit-cover/', views.edit_group_cover, name='edit_group_cover'),
    path('<slug:group>/banned-users/', views.banned_users, name='banned_users'),
    path('<slug:group>/ban-user/<int:user_id>/', views.ban_user, name='ban_user'),
    path('<slug:group>/settings/', views.group_settings, name='group_settings'),

    # Group interaction
    path('<slug:group>/subscription/', views.subscribe, name='subscribe'),

    # Removed subject-related URLs:
    # path('<slug:group>/create-subject/', views.create_subject, name='create_subject'),
    # path('<slug:group>/subject/<slug:subject>/', views.SubjectDetailView.as_view(), name='subject_detail'),
    # path('<slug:group>/subject/<slug:subject>/like/', views.like_subject, name='like_subject'),
    # path('<slug:group>/subject/<slug:subject>/comment/', views.add_comment, name='add_comment'),

    # Group detail - keep at the end to avoid URL pattern conflicts
    path('<slug:group>/', views.GroupPageView.as_view(), name='group'),
]