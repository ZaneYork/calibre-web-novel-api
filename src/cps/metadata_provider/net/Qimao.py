import re

import requests
from lxml import etree

from cps.metadata_provider.net.Base import GenericSearchDefine, GenericSearchBookSearcher
from cps.services.Metadata import Metadata


class QimaoSearchDefine(GenericSearchDefine):

    def __init__(self):
        self.search_url = "https://www.qimao.com/search/index/?keyword="
        base_url = "https://www.qimao.com"
        book_url_pattern = re.compile(".*/shuku/(\\d+)/?")
        provider_name = "七猫中文网"
        provider_id = "qimao"
        super().__init__(base_url, book_url_pattern, provider_name, provider_id)

    def get_search_page(self, query):
        url = self.search_url + query
        return requests.get(url, {}, headers=self.default_headers)

    def get_search_results(self, html, query, author):
        book_urls = []
        exact_urls = []
        alist = html.xpath("//li/div[@class='txt']/span[@class='s-tit']/a")
        for link in alist:
            href = link.attrib['href']
            if self.book_url_pattern.match(href):
                parsed = self.base_url + href
                book_urls.append(parsed)
            else:
                continue
            title = ''.join(etree.HTML(etree.tostring(link)).xpath('//text()')).strip()
            if title == query:
                item_base = link.getparent().getparent()
                if len(item_base):
                    item_author = item_base.xpath('p[@class="p-bottom"]/span[1]/a/text()')
                    if len(item_author) > 0:
                        if author == item_author[0]:
                            return [], [parsed]
                exact_urls.append(parsed)
        return book_urls, exact_urls

    def get_title(self, html):
        title_element = html.xpath('//div[starts-with(@class,"title")]/span[@class="txt"]')
        return self.get_text(title_element)

    def get_author(self, html):
        author_element = html.xpath('//div[@class="sub-title"]/span[@class="txt"]/em/a')
        return [self.get_text(author_element)]

    def get_cover(self, html):
        img_element = html.xpath('//div[@class="wrap-pic"]/img')
        if len(img_element):
            cover = img_element[0].attrib['src']
            if not cover:
                return ''
            else:
                return cover

    def get_description(self, html):
        summary_element = html.xpath('//p[@class="intro"]')
        if len(summary_element):
            return etree.tostring(summary_element[-1], encoding="utf8").decode("utf8").strip()

    def get_tags(self, html):
        tag_elements = html.xpath('//div[@class="tags-wrap"]/em/a')
        if len(tag_elements):
            return [self.get_text(tag_element) for tag_element in tag_elements]


definition = QimaoSearchDefine()


class Qimao(Metadata):
    __name__ = definition.provider_name
    __id__ = definition.provider_id

    def __init__(self):
        self.searcher = GenericSearchBookSearcher(definition)
        super().__init__()

    def search(self, query: str, generic_cover: str = "", locale: str = "en"):
        if self.active:
            return self.searcher.search_books(query)
