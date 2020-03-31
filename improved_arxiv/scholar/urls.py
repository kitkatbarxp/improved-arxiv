from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('newest_articles', views.newest_articles, name='newest_articles'),
    path('prolific_authors', views.prolific_authors, name='prolific_authors'),
    path('article/<int:article_id>', views.article, name='article'),
    path('author/<int:author_id>', views.author, name='author'),
]
