import re

import requests
from lxml import etree
from lxml.etree import HTML

from cps.metadata_provider.net.Base import GenericSearchDefine, GenericSearchBookSearcher, GenericSearchMetaRecord
from cps.services.Metadata import Metadata, MetaSourceInfo


class FanqieSearchDefine(GenericSearchDefine):

    def __init__(self):
        self.search_url = "https://fanqienovel.com/api/author/search/search_book/v1?filter=127%2C127%2C127%2C127&page_count=10&page_index=0&query_type=0&query_word="
        base_url = "https://fanqienovel.com"
        book_url_pattern = re.compile(".*/page/(\\d+)/?")
        provider_name = "番茄小说网"
        provider_id = "fanqienovel"
        super().__init__(base_url, book_url_pattern, provider_name, provider_id)

    def get_search_page(self, query):
        url = self.search_url + query
        return requests.get(url, {}, headers=self.default_headers)

    def get_search_results(self, html, query, author):
        books = []
        exact_books = []
        alist = html["data"]["search_book_data_list"]
        for link in alist:
            book_id = link['book_id']
            parsed = "https://fanqienovel.com/page/" + book_id
            title = link['book_name']
            author = link['author']
            thumb_url = link['thumb_url']
            category = link['category'].split(',')
            description = link['book_abstract']
            book = GenericSearchMetaRecord(
                id=book_id,
                title=title,
                authors=[author],
                cover=thumb_url,
                publisher=self.provider_name,
                description=description,
                url=parsed,
                tags=category,
                source=MetaSourceInfo(
                    id=self.provider_id,
                    description=self.provider_name,
                    link=self.base_url
                )
            )
            books.append(book)
            if title == query:
                if author == link['author']:
                    return [], [book]
                exact_books.append(book)
        return books, exact_books


definition = FanqieSearchDefine()


class Fanqie(Metadata):
    __name__ = definition.provider_name
    __id__ = definition.provider_id

    def __init__(self):
        self.searcher = GenericSearchBookSearcher(definition)
        super().__init__()

    def search(self, query: str, generic_cover: str = "", locale: str = "en"):
        if self.active:
            return self.searcher.search_books_single(query)
