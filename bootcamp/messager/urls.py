from django.urls import path

from bootcamp.messager import views

app_name = "messager"
urlpatterns = [
    path('', views.MessagesListView.as_view(), name="messages_list"),
    path('send-message/', views.send_message, name="send_message"),
    path('receive-message/', views.receive_message, name="receive_message"),
    path('mark-read-messages/', views.mark_read_messages, name="mark_read_messages"),
    path('get-unread-messages/', views.get_unread_messages, name="get_unread_messages"),
    path('delete/<uuid:message_id>/', views.delete_message, name="delete_message"),
    path('react/<uuid:message_id>/', views.react_message, name="react_message"),
    path('delete-conversation/<str:username>/', views.delete_conversation, name="delete_conversation"),
    path('mute/<str:username>/', views.mute_conversation, name="mute_conversation"),
    path('<str:username>/', views.ConversationListView.as_view(), name="conversation_detail"),
]

