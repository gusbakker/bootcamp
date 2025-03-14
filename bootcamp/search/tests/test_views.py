from django.urls import reverse
from django.test import Client

from test_plus.test import TestCase

from bootcamp.articles.models import Article
from bootcamp.news.models import News


class SearchViewsTests(TestCase):
    """
    Includes tests for all the functionality
    associated with Views
    """

    def setUp(self):
        self.user = self.make_user("first_user")
        self.other_user = self.make_user("second_user")
        self.client = Client()
        self.other_client = Client()
        self.client.login(username="first_user", password="password")
        self.other_client.login(username="second_user", password="password")
        self.title = "A really nice to-be first title "
        self.content = """This is a really good content, just if somebody
        published it, that would be awesome, but no, nobody wants to publish
        it, because they know this is just a test, and you know than nobody
        wants to publish a test, just a test; everybody always wants the real
        deal."""
        self.article = Article.objects.create(
            user=self.user,
            title="A really nice first title",
            content=self.content,
            tags="list, lists",
            status="P",
        )
        self.article_2 = Article.objects.create(
            user=self.other_user,
            title="A first bad title",
            content="First bad content",
            tags="bad",
            status="P",
        )
        self.news_one = News.objects.create(
            user=self.user, content="This is the first lazy content."
        )

    def test_news_search_results(self):
        response = self.client.get(reverse("search:results"), {"query": "This is"})
        assert response.status_code == 200
        assert self.news_one in response.context["news_list"]
        assert self.article in response.context["articles_list"]