"""
If I had extra time, I would turn these function-based views into ViewSets and group the endpoints like the following:
    ArticleViewSet:
        - newest_articles (GET)
        - article (GET)
    AuthorViewSet:
        - prolific_authors (GET)
        - author(GET)

I would also introduce defensive coding to make sure only GET requests are acceptable.
"""
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator
from django.db.models import Case, Count, IntegerField, Max, When
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from scholar.models import Author, Article


def index(request):
    return render(request, 'scholar/index.html')


def newest_articles(request):
    now = timezone.now()
    six_months_ago = relativedelta(months=-6)
    cutoff = now + six_months_ago

    articles = Article.objects.filter(published_timestamp__gte=cutoff)
    paginator = Paginator(articles, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'scholar/newest_articles.html', {'page_obj': page_obj})


def prolific_authors(request):
    now = timezone.now()
    six_months_ago = relativedelta(months=-6)
    cutoff = now + six_months_ago

    authors = Author.objects.annotate(
        article_count=Count(Case(When(articles__published_timestamp__gte=cutoff, then=1), output_field=IntegerField())),
        last_pub=Max('articles__published_timestamp'))
    authors = authors.values('id', 'name', 'article_count', 'last_pub').order_by('-article_count', '-last_pub')

    paginator = Paginator(authors, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'scholar/prolific_authors.html', {'page_obj': page_obj})


def article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'scholar/article.html', {'article': article})


def author(request, author_id):
    author = get_object_or_404(Author, pk=author_id)

    now = timezone.now()
    six_months_ago = relativedelta(months=-6)
    cutoff = now + six_months_ago
    articles = author.articles.filter(published_timestamp__gte=cutoff).values('id', 'title')

    context = {'name': author.name, 'articles': articles}

    return render(request, 'scholar/author.html', context)
