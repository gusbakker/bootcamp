from django.urls import path

from bootcamp.search import views

app_name = "search"
urlpatterns = [
    path("", views.SearchListView.as_view(), name="results"),
    path("suggestions/", views.get_suggestions, name="suggestions"),
]
