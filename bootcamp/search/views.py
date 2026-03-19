from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView

from taggit.models import Tag

from bootcamp.articles.models import Article
from bootcamp.news.models import News
from bootcamp.helpers import ajax_required


class SearchListView(LoginRequiredMixin, ListView):
    """CBV to contain all the search results"""

    model = News
    template_name = "search/search_results.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get("query")
        context["active"] = "news"
        context["hide_search"] = True
        context["tags_list"] = Tag.objects.filter(name=query)
        context["news_list"] = News.objects.filter(
            content__icontains=query, reply=False
        ).distinct()
        context["articles_list"] = Article.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__name__icontains=query),
            status="P",
        ).distinct()
        context["users_list"] = (
            get_user_model()
            .objects.filter(Q(username__icontains=query) | Q(name__icontains=query))
            .distinct()
        )
        context["news_count"] = context["news_list"].count()
        context["articles_count"] = context["articles_list"].count()
        context["users_count"] = context["users_list"].count()
        context["tags_count"] = context["tags_list"].count()
        context["total_results"] = (
            context["news_count"]
            + context["articles_count"]
            + context["users_count"]
            + context["tags_count"]
        )
        return context


# For autocomplete suggestions
@login_required
@ajax_required
def get_suggestions(request):
    # Convert users, articles objects into list to be
    # represented as a single list.
    query = request.GET.get("term", "")
    users = list(
        get_user_model().objects.filter(
            Q(username__icontains=query) | Q(name__icontains=query)
        )
    )
    articles = list(
        Article.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__name__icontains=query),
            status="P",
        )
    )
    # Add all the retrieved users, articles to data_retrieved
    # list.
    data_retrieved = users
    data_retrieved.extend(articles)
    results = []
    
    from django.urls import reverse
    
    for data in data_retrieved:
        data_json = {}
        if isinstance(data, get_user_model()):
            data_json["type"] = "user"
            data_json["id"] = data.id
            data_json["name"] = data.get_profile_name()
            data_json["subtitle"] = f"@{data.username}"
            data_json["image"] = data.get_picture()
            data_json["url"] = data.get_absolute_url()

        if isinstance(data, Article):
            data_json["type"] = "article"
            data_json["id"] = data.id
            data_json["name"] = data.title
            data_json["subtitle"] = f"By {data.user.get_profile_name()}"
            if data.image:
                data_json["image"] = data.image.url
            else:
                from django.templatetags.static import static
                data_json["image"] = static('img/favicon.png')
            data_json["url"] = reverse("articles:article", kwargs={"slug": data.slug})

        results.append(data_json)

    return JsonResponse(results, safe=False)
