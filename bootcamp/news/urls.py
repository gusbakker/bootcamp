from django.urls import path

from bootcamp.news import views

app_name = "news"
urlpatterns = [
    path('', views.NewsListView.as_view(), name="list"),
    # path('delete/<slug:pk>/', views.NewsDeleteView.as_view(), name="delete_news"),
    path('remove/', views.remove_news, name="remove_news"),
    path('post-news/', views.post_news, name="post_news"),
    path('like/', views.like, name="like_post"),
    path('get-thread/', views.get_thread, name="get_thread"),
    path('post-comment/', views.post_comment, name="post_comments"),
    path('update-interactions/', views.update_interactions, name="update_interactions"),
    path('<str:pk>/', views.news, name='news'),
]
