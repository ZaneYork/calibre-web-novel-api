import re

import requests
from lxml import etree

from cps.metadata_provider.net.Base import GenericSearchDefine, GenericSearchBookSearcher
from cps.services.Metadata import Metadata


class TaduSearchDefine(GenericSearchDefine):

    def __init__(self):
        self.search_url = "https://www.tadu.com/search"
        base_url = "https://www.tadu.com"
        book_url_pattern = re.compile(".*/book/(\\d+)/?")
        provider_name = "塔读文学"
        provider_id = "tadu"
        super().__init__(base_url, book_url_pattern, provider_name, provider_id)

    def get_search_page(self, query):
        url = self.search_url
        params = {"query": query}
        return requests.post(url, params, headers=self.default_headers)

    def get_search_results(self, html, query, author):
        book_urls = []
        exact_urls = []
        alist = html.xpath("//a[contains(@class,'bookNm')]")
        for link in alist:
            href = link.attrib['href']
            if self.book_url_pattern.match(href):
                parsed = self.base_url + href
                book_urls.append(parsed)
            else:
                continue
            if len(link) > 0:
                title = ''.join(etree.HTML(etree.tostring(link)).xpath('//text()')).strip()
            else:
                title = link.text
            if title == query:
                item_base = link.getparent()
                if len(item_base):
                    item_author = item_base.xpath('div[starts-with(@class,"bot_list")]/div[@class="condition"]/a[@class="authorNm"]/text()')
                    if len(item_author) > 0:
                        if author == item_author[0]:
                            return [], [parsed]
                exact_urls.append(parsed)
        return book_urls, exact_urls

    def get_title(self, html):
        title_element = html.xpath("//a[@class='bkNm']/text()")
        return title_element[0].strip()

    def get_author(self, html):
        author_element = html.xpath("//div[@class='bookNm']/span[contains(@class,'author')]")
        return [self.get_text(author_element).replace(' 著', '')]

    def get_cover(self, html):
        img_element = html.xpath("//a[@class='bookImg']/img")
        if len(img_element):
            cover = img_element[0].attrib['src']
            if not cover:
                return ''
            else:
                return cover

    def get_description(self, html):
        summary_element = html.xpath("//p[contains(@class,'intro')]")
        if len(summary_element):
            return etree.tostring(summary_element[-1], encoding="utf8").decode("utf8").strip()

    def get_tags(self, html):
        tag_elements = html.xpath("//div[@class='sortList']/a[text()!='无标签']")
        if len(tag_elements):
            return [self.get_text(tag_element) for tag_element in tag_elements]


definition = TaduSearchDefine()


class Tadu(Metadata):
    __name__ = definition.provider_name
    __id__ = definition.provider_id

    def __init__(self):
        self.searcher = GenericSearchBookSearcher(definition)
        super().__init__()

    def search(self, query: str, generic_cover: str = "", locale: str = "en"):
        if self.active:
            return self.searcher.search_books(query)
