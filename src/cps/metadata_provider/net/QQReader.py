import re

import requests
from lxml import etree

from cps.metadata_provider.net.Base import GenericSearchDefine, GenericSearchBookSearcher
from cps.services.Metadata import Metadata


class QQReaderSearchDefine(GenericSearchDefine):

    def __init__(self):
        self.search_url = "https://book.qq.com/so/"
        base_url = "https://book.qq.com/"
        book_url_pattern = re.compile(".*/book-detail/(\\d+)/?")
        provider_name = "QQ阅读"
        provider_id = "qqreader"
        super().__init__(base_url, book_url_pattern, provider_name, provider_id)

    def get_search_page(self, query):
        url = self.search_url + query
        return requests.get(url, {}, headers=self.default_headers)

    def get_search_results(self, html, query, author):
        book_urls = []
        exact_urls = []
        alist = html.xpath("//div[contains(@class,'book-large')]/a")
        for link in alist:
            href = link.attrib['href']
            if self.book_url_pattern.match(href):
                parsed = "https:" + href
                book_urls.append(parsed)
            else:
                continue
            title = link.attrib['title']
            if title == query:
                item_base = link
                if len(item_base):
                    item_author = item_base.xpath('div[@class="content"]/p[@class="other"]/object/a[contains(@href,"book-writer")]/text()')
                    if len(item_author) > 0:
                        if author == item_author[0]:
                            return [], [parsed]
                exact_urls.append(parsed)
        return book_urls, exact_urls

    def get_title(self, html):
        title_element = html.xpath("//h1[@class='book-title']/text()")
        return title_element[0].strip()

    def get_author(self, html):
        author_element = html.xpath("//div[@class='book-meta']/a[contains(@class,'author')]")
        return [self.get_text(author_element).replace(' 著', '')]

    def get_cover(self, html):
        img_element = html.xpath("//div[@class='page-header-content']//img[@class='ypc-book-cover']")
        if len(img_element):
            cover = img_element[0].attrib['src']
            if not cover:
                return ''
            else:
                return cover

    def get_description(self, html):
        summary_element = html.xpath("//div[contains(@class,'book-intro')]")
        if len(summary_element):
            return etree.tostring(summary_element[-1], encoding="utf8").decode("utf8").strip()

    def get_tags(self, html):
        tag_elements = html.xpath("//div[@class='book-tags']/a[contains(@class,'tag')]")
        if len(tag_elements):
            return [self.get_text(tag_element) for tag_element in tag_elements]


definition = QQReaderSearchDefine()


class QQReader(Metadata):
    __name__ = definition.provider_name
    __id__ = definition.provider_id

    def __init__(self):
        self.searcher = GenericSearchBookSearcher(definition)
        super().__init__()

    def search(self, query: str, generic_cover: str = "", locale: str = "en"):
        if self.active:
            return self.searcher.search_books(query)
