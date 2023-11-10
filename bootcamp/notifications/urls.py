from django.urls import path

from bootcamp.notifications import views

app_name = "notifications"
urlpatterns = [
    path('', views.NotificationUnreadListView.as_view(), name="unread"),
    path('mark-as-read/<slug:slug>/', views.mark_as_read, name="mark_as_read"),
    path('mark-as-read-ajax/', views.mark_as_read_ajax, name="mark_as_read_ajax"),
    path('mark-all-as-read/', views.mark_all_as_read, name="mark_all_read"),
    path('latest-notifications/', views.get_latest_notifications, name="latest_notifications"),
    path('unread-notifications/', views.get_unread_notifications, name="unread_notifications"),
]
