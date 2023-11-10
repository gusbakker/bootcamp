from django.urls import path

from bootcamp.search import views

app_name = "search"
urlpatterns = [
    path(r"^$", views.SearchListView.as_view(), name="results"),
    path(r"^suggestions/$", views.get_suggestions, name="suggestions"),
]
