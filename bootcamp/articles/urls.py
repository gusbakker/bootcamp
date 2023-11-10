from django.urls import path

from bootcamp.articles.views import (
    ArticlesListView,
    DraftsListView,
    CreateArticleView,
    EditArticleView,
    DetailArticleView,
)

app_name = "articles"
urlpatterns = [
    path('', ArticlesListView.as_view(), name="list"),
    path('write-new-article/', CreateArticleView.as_view(), name="write_new"),
    path('drafts/', DraftsListView.as_view(), name="drafts"),
    path('edit/<int:pk>/', EditArticleView.as_view(), name="edit_article"),
    path('<slug:slug>/', DetailArticleView.as_view(), name="article"),
    path('tag/<slug:tag>/', ArticlesListView.as_view(), name="tagged"),
]

