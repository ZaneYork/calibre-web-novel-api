import re

import requests
from lxml import etree

from cps.metadata_provider.net.Base import GenericSearchDefine, GenericSearchBookSearcher
from cps.services.Metadata import Metadata


class ZxcsSearchDefine(GenericSearchDefine):

    def __init__(self):
        self.search_url = "https://zxcs.info/index.php"
        base_url = "https://zxcs.info"
        book_url_pattern = re.compile(".*/post/(\\d+)/?")
        provider_name = "知轩藏书"
        provider_id = "zxcs"
        self.book_name_pattern = re.compile(".*?《(.+?)》.*")
        self.author_name_pattern = re.compile(".*?作者[:：\s]+(.+)")
        super().__init__(base_url, book_url_pattern, provider_name, provider_id)

    def get_search_page(self, query):
        url = self.search_url
        params = {"keyword": query}
        return requests.get(url, params, headers=self.default_headers)

    def get_search_results(self, html, query, author):
        book_urls = []
        exact_urls = []
        alist = html.xpath("id('plist')/dt/a")
        for link in alist:
            href = link.attrib['href']
            if self.book_url_pattern.match(href):
                parsed = href
                book_urls.append(parsed)
            else:
                continue
            title = link.text
            title_groups = self.book_name_pattern.fullmatch(title)
            if title_groups:
                title = title_groups.group(1)
            if title == query:
                author_groups = self.author_name_pattern.fullmatch(link.text)
                if author_groups:
                    item_author = author_groups.group(1)
                    if author == item_author:
                        return [], [parsed]
                exact_urls.append(parsed)
        return book_urls, exact_urls

    def get_title(self, html):
        title_element = html.xpath("//div[contains(@class,'book-info')]/h1/text()")
        return title_element[0].strip().replace("《", "").replace("》", "")

    def get_author(self, html):
        author_element = html.xpath("//p[@class='intro']")
        return [self.get_text(author_element).replace(' 著', '')]

    def get_cover(self, html):
        img_element = html.xpath("id('bookImg')/img")
        if len(img_element):
            cover = img_element[0].attrib['src']
            if not cover:
                return ''
            else:
                return self.base_url + cover

    def get_description(self, html):
        vote_element = html.xpath("id('vote')")
        if len(vote_element) > 0:
            vote_element[0].getparent().remove(vote_element[0])
        summary_element = html.xpath("//div[@class='book-info-detail']")
        if len(summary_element):
            return (etree.tostring(summary_element[-1], encoding="utf8").decode("utf8").strip()
                                .replace('<cite class="icon-pin"/> <br/>',''))

    def get_tags(self, html):
        tag_elements = html.xpath("//p[@class='tag']/a")
        if len(tag_elements):
            return [self.get_text(tag_element).replace('精校','') for tag_element in tag_elements]


definition = ZxcsSearchDefine()


class Zxcs(Metadata):
    __name__ = definition.provider_name
    __id__ = definition.provider_id

    def __init__(self):
        self.searcher = GenericSearchBookSearcher(definition)
        super().__init__()

    def search(self, query: str, generic_cover: str = "", locale: str = "en"):
        if self.active:
            return self.searcher.search_books(query)
