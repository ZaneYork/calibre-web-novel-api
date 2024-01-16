import re

import requests
from lxml import etree
from lxml.etree import HTML

from cps.metadata_provider.net.Base import GenericSearchDefine, GenericSearchBookSearcher
from cps.services.Metadata import Metadata


class QidianSearchDefine(GenericSearchDefine):

    def __init__(self):
        self.search_url = "https://www.qidian.com/so/"
        base_url = "https://www.qidian.com/"
        book_url_pattern = re.compile(".*/book/(\\d+)/?")
        provider_name = "起点中文网"
        provider_id = "qidian"
        super().__init__(base_url, book_url_pattern, provider_name, provider_id)

    def get_search_page(self, query):
        url = self.search_url + query + ".html"
        return requests.get(url, {}, headers=self.default_headers)

    def get_search_results(self, html, query, author):
        book_urls = []
        exact_urls = []
        alist = html.xpath("//h3/a[contains(@title,'在线阅读')]")
        for link in alist:
            href = link.attrib['href']
            if self.book_url_pattern.match(href):
                parsed = "https:" + href
                book_urls.append(parsed)
            else:
                continue
            title = link.attrib['title'].replace('在线阅读', '')
            if title == query:
                item_base = link.getparent().getparent()
                if len(item_base):
                    item_author = item_base.xpath('p[@class="author"]/a[@class="name"]/text()')
                    if len(item_author) > 0:
                        if author == item_author[0]:
                            return [], [parsed]
                exact_urls.append(parsed)
        return book_urls, exact_urls

    def get_title(self, html):
        title_element = html.xpath('id("bookName")')
        return self.get_text(title_element)

    def get_author(self, html):
        author_element = html.xpath("//a[@class='writer-name']")
        return [self.get_text(author_element)]

    def get_cover(self, html):
        img_element = html.xpath('id("bookImg")/img')
        if len(img_element):
            cover = img_element[0].attrib['src']
            if not cover:
                return ''
            else:
                return "https:" + cover

    def get_description(self, html):
        summary_element = html.xpath('id("book-intro-detail")')
        if len(summary_element):
            return etree.tostring(summary_element[-1], encoding="utf8").decode("utf8").strip()

    def get_tags(self, html):
        tag_elements = html.xpath("//p[@class='book-attribute']/a")
        if len(tag_elements):
            return [self.get_text(tag_element) for tag_element in tag_elements]


definition = QidianSearchDefine()


class Qidian(Metadata):
    __name__ = definition.provider_name
    __id__ = definition.provider_id

    def __init__(self):
        self.searcher = GenericSearchBookSearcher(definition)
        super().__init__()

    def search(self, query: str, generic_cover: str = "", locale: str = "en"):
        if self.active:
            return self.searcher.search_books(query)
