import re

import requests
from lxml import etree

from cps.metadata_provider.net.Base import GenericSearchDefine, GenericSearchBookSearcher
from cps.services.Metadata import Metadata


class JinjiangSearchDefine(GenericSearchDefine):

    def __init__(self):
        self.search_url = "https://www.jjwxc.net/search.php?kw="
        base_url = "https://www.jjwxc.net"
        book_url_pattern = re.compile(".*/onebook.php\\?novelid=(\\d+)/?")
        provider_name = "晋江文学城"
        provider_id = "jinjiang"
        super().__init__(base_url, book_url_pattern, provider_name, provider_id)
        self.default_headers['Accept-Charset'] = "utf-8"

    def get_search_page(self, query):
        url = self.search_url + query + "&t=1&ord=relate"
        return requests.get(url, {}, headers=self.default_headers)

    def get_search_results(self, html, query, author):
        book_urls = []
        exact_urls = []
        alist = html.xpath("id('search_result')/div/h3[@class='title']/a")
        for link in alist:
            href = link.attrib['href']
            if self.book_url_pattern.match(href):
                parsed = href
                book_urls.append(parsed)
            else:
                continue
            title = link.xpath('text()')[0]
            if title == query:
                item_base = link.getparent().getparent()
                if len(item_base):
                    item_author = item_base.xpath('//div[@class="info"]/a[contains(@href,"oneauthor")]/span/text()')
                    if len(item_author) > 0:
                        if author == item_author[0]:
                            return [], [parsed]
                exact_urls.append(parsed)
        return book_urls, exact_urls

    def get_title(self, html):
        title_element = html.xpath('//h1[@itemprop="name"]/span[@itemprop="articleSection"]')
        return self.get_text(title_element)

    def get_author(self, html):
        author_element = html.xpath('//h2/a/span[@itemprop="author"]')
        return [self.get_text(author_element)]

    def get_cover(self, html):
        img_element = html.xpath('//img[@class="noveldefaultimage"]')
        if len(img_element):
            cover = img_element[0].attrib['src']
            if not cover:
                return ''
            else:
                return "https:" + cover

    def get_description(self, html):
        summary_element = html.xpath('id("novelintro")')
        other_element = html.xpath('id("novelintro")/a')
        if len(other_element):
            summary_element.remove(other_element)
        if len(summary_element):
            return etree.tostring(summary_element[-1], encoding="utf8").decode("utf8").strip()

    def get_tags(self, html):
        tag_elements = html.xpath('//div[@class="smallreadbody"]/span/a[contains(@href,"bookbase")]')
        if len(tag_elements):
            return [self.get_text(tag_element) for tag_element in tag_elements]


definition = JinjiangSearchDefine()


class Jinjiang(Metadata):
    __name__ = definition.provider_name
    __id__ = definition.provider_id

    def __init__(self):
        self.searcher = GenericSearchBookSearcher(definition)
        super().__init__()

    def search(self, query: str, generic_cover: str = "", locale: str = "en"):
        if self.active:
            return self.searcher.search_books(query)
