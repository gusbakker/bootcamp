from django.urls import path

from bootcamp.messager import views

app_name = "messager"
urlpatterns = [
    path('', views.MessagesListView.as_view(), name="messages_list"),
    path('send-message/', views.send_message, name="send_message"),
    path('receive-message/', views.receive_message, name="receive_message"),
    path('mark-read-messages/', views.mark_read_messages, name="mark_read_messages"),
    path('get-unread-messages/', views.get_unread_messages, name="get_unread_messages"),
    path('<str:username>/', views.ConversationListView.as_view(), name="conversation_detail"),
]

