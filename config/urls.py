from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from graphene_django.views import GraphQLView

urlpatterns = [
    path(r"^$", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        r"^about/$",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path(r"^accounts/", include("allauth.urls")),
    # Third party apps here
    path(r"^comments/", include("django_comments.urls")),
    path(r"^graphql", GraphQLView.as_view(graphiql=True)),
    path(r"^markdownx/", include("markdownx.urls")),
    # Local apps here
    path(
        r"^notifications/",
        include("bootcamp.notifications.urls", namespace="notifications"),
    ),
    path(r"^articles/", include("bootcamp.articles.urls", namespace="articles")),
    path(r"^news/", include("bootcamp.news.urls", namespace="news")),
    path(r"^messages/", include("bootcamp.messager.urls", namespace="messager")),
    path(r"^qa/", include("bootcamp.qa.urls", namespace="qa")),
    path(r"^search/", include("bootcamp.search.urls", namespace="search")),
    path("", include("bootcamp.users.urls", namespace="users")),
    path(r"^groups/", include("bootcamp.groups.urls", namespace="groups")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development
    urlpatterns += [
        path(
            r"^400/$",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            r"^403/$",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            r"^404/$",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path(r"^500/$", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns


# flatpages urls
# urlpatterns.append(path(r'^', include('django.contrib.flatpages.urls')))
