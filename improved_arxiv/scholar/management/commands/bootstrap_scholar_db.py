import urllib.request as libreq
import xml.etree.ElementTree as ET

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from scholar.models import Author, Article


class Command(BaseCommand):
    help = 'Populate scholar db with articles from axRiv using its bulk data API.'

    def handle(self, *args, **options):

        # for prototype, we are hardcoding the cutoff here for boostraping. However, ideally, this management command
        # will be executed frequently as a cronjob to fetch more recent data from axRiv, which means that the cutoff
        # time should be based on the last time this data collection is run.
        now = timezone.now()
        six_months_ago = now - relativedelta(months=6)
        
        start = 0 
        offset = 200  # this pagination offset can also be a dynamic setting where we tweak it for performance tuning
        total_results = 201
        within_cutoff = True

        url_path = ('http://export.arxiv.org/api/query?search_query=all:psychiatry'
                    '+OR+all:therapy+OR+all:%22machine+learning%22'
                    '+OR+all:%22data+science%22&start={}&max_results={}'
                    '&sortBy=submittedDate&sortOrder=descending')

        while start < total_results and within_cutoff:
            print('Start index: {}'.format(start)
            current_url_path = url_path.format(start, offset)

            with libreq.urlopen(current_url_path) as url:
                data = url.read()
                root = ET.fromstring(data)

                if start == 0:
                    total_results = int(root[4].text)
                    print('Total results to parse: {}'.format(total_results)

                for child in root:
                    if 'entry' in child.tag:
                        # assume published is the 3rd element
                        published_timestamp = parse(child[2].text)
                        # if the article entry is older than six months ago, we can go ahead and quit
                        # because the output of the API call should be sorted descending by submittedDate
                        if published_timestamp >= six_months_ago:
                            self._handle_entry(child)
                        else:
                            within_cutoff = False
                            break

            start += offset

    def _handle_entry(self, entry):
        """
        This method takes in an entry atom from the xml, parses it, and creates its authors and the article entry if
        the related objects are not in the database.
        """
        entry_id = published_timestamp = title = summary = None
        authors = []
        for child in entry:
            tag = child.tag
            text = child.text

            if 'id' in tag:
                # should parse this
                entry_id = text
            elif 'published' in tag:
                published_timestamp = parse(text)
            elif 'title' in tag:
                title = text
            elif 'summary' in tag:
                summary = text
            elif 'author' in tag:
                name = child[0].text
                author, _ = Author.objects.get_or_create(name=name)
                authors.append(author)

        article, _ = Article.objects.get_or_create(
            arxiv_id=entry_id, title=title, summary=summary, published_timestamp=published_timestamp)
        article.authors.set(authors)
