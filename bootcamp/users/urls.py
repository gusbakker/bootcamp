from django.urls import path, re_path
from allauth.account.views import PasswordChangeView

from . import views

app_name = "users"
urlpatterns = [
    re_path(r"^~users$", view=views.UserListView.as_view(), name="list"),
    re_path(r"^~redirect/$", view=views.UserRedirectView.as_view(), name="redirect"),
    re_path(r"^~update/$", view=views.UserUpdateView.as_view(), name="update"),
    re_path(r"^~password/$", view=PasswordChangeView.as_view(), name="account_change_password"),
    path("picture/", views.picture, name="picture"),
    path("upload_picture/", views.upload_picture, name="upload_picture"),
    path("save_uploaded_picture/", views.save_uploaded_picture, name="save_uploaded_picture"),
    path('<str:username>/following/', views.FollowingPageView.as_view(), name='view_following'),
    path('<str:username>/followers/', views.FollowersPageView.as_view(), name='view_all_followers'),
    path('follow_user/<int:user_id>/', views.follow_user, name='follow_user'),
    path('send_message_request/<int:user_id>/', views.send_message_request, name='send_message_request'),
    path('accept_message_request/<int:user_id>/', views.accept_message_request, name='accept_message_request'),
    path('block_spammer/<int:user_id>/', views.block_spammer, name='block_spammer'),
    path('<str:username>/friends/all/', views.all_friends, name='all_friends'),
    path('<str:username>/friends/requests/', views.all_message_requests, name='all_message_requests'),
    path('<str:username>/', views.UserDetailView.as_view(), name="detail"),
]
