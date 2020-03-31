from django.db import models

from scholar.models import Author


class Article(models.Model):

    authors = models.ManyToManyField(Author, related_name='articles')

    arxiv_id = models.CharField(max_length=100)

    title = models.TextField()

    summary = models.TextField(null=True, blank=True)

    published_timestamp = models.DateTimeField()

    class Meta:
        ordering = ['-published_timestamp']
