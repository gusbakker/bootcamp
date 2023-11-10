from django.urls import path

from . import views

app_name = "groups"
urlpatterns = [
    path('all', view=views.GroupsPageView.as_view(), name='list'),
    path('<slug:group>/', views.GroupPageView.as_view(), name='group'),
    # path('ban_user/<slug:group>/<int:user_id>/', views.ban_user, name='ban_user'),
    path('<slug:group>/edit_group_cover/', views.edit_group_cover, name='edit_group_cover'),
    path('<slug:group>/subscription/', views.subscribe, name='subscribe'),
    # path('<slug:subject>/like/', views.like_subject, name='like'),
    path('banned_users/<slug:group>/', views.banned_users, name='banned_users'),
]
