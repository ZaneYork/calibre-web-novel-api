import dataclasses
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

import requests
from lxml import etree

from cps.services.Metadata import MetaRecord, MetaSourceInfo

CONST_BOOK_CACHE_SIZE = 500  # 最大缓存数量
CONST_CONCURRENCY_SIZE = 5  # 并发查询数


class GenericSearchDefine:
    def __init__(self,
                 base_url,
                 book_url_pattern,
                 provider_name,
                 provider_id
                 ):
        self.base_url = base_url
        self.book_url_pattern = book_url_pattern
        self.provider_name = provider_name
        self.provider_id = provider_id
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3573.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': base_url
        }

    def get_search_page(self, query):
        pass

    def get_search_results(self, html, query, author):
        pass

    def get_title(self, html):
        pass

    def get_author(self, html):
        pass

    def get_cover(self, html):
        pass

    def get_description(self, html):
        pass

    def get_tags(self, html):
        pass

    def get_text(self, element, default_str=''):
        text = default_str
        if len(element) and element[0].text:
            text = element[0].text.strip()
        elif isinstance(element, etree._Element) and element.text:
            text = element.text.strip()
        return text if text else default_str


@dataclasses.dataclass
class GenericSearchMetaRecord(MetaRecord):

    def __getattribute__(self, item):  # cover通过本地服务代理访问
        return super().__getattribute__(item)


class GenericSearchBookSearcher:

    def __init__(self, definition: GenericSearchDefine):
        self.definition = definition
        self.book_loader = GenericSearchBookLoader(definition)
        self.thread_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix=definition.provider_id + '_async')

    def load_book_urls_new(self, query):
        sections = query.split(';')
        if len(sections) > 1:
            query = sections[0]
            author = sections[1]
        else:
            author = None
        res = self.definition.get_search_page(query)
        book_urls = []
        exact_urls = []
        if res.status_code in [200, 201]:
            if(res.headers['Content-Type'].find('/json') >= 0):
                html = res.json()
            else:
                html = etree.HTML(res.content)
            book_urls, exact_urls = self.definition.get_search_results(html, query, author)
        if len(exact_urls) > 0:
            return exact_urls
        return book_urls[:3]

    def search_books(self, query):
        book_urls = self.load_book_urls_new(query)
        books = []
        futures = [self.thread_pool.submit(self.book_loader.load_book, book_url) for book_url in book_urls]
        for future in as_completed(futures):
            book = future.result()
            if book is not None:
                books.append(future.result())
        return books

    def search_books_single(self, query):
        sections = query.split(';')
        if len(sections) > 1:
            query = sections[0]
            author = sections[1]
        else:
            author = None
        res = self.definition.get_search_page(query)
        books = []
        exact_books = []
        if res.status_code in [200, 201]:
            if (res.headers['Content-Type'].find('/json') >= 0):
                html = res.json()
            else:
                html = etree.HTML(res.content)
            books, exact_books = self.definition.get_search_results(html, query, author)
        if len(exact_books) > 0:
            return exact_books
        return books[:3]

class GenericSearchBookLoader:

    def __init__(self, definition: GenericSearchDefine):
        self.book_parser = GenericSearchBookHtmlParser(definition)
        self.definition = definition

    @lru_cache(maxsize=CONST_BOOK_CACHE_SIZE)
    def load_book(self, url):
        book = None
        self.random_sleep()
        start_time = time.time()
        res = requests.get(url, headers=self.definition.default_headers)
        if res.status_code in [200, 201]:
            print("下载书籍:{}成功,耗时{:.0f}ms".format(url, (time.time() - start_time) * 1000))
            book_detail_content = res.content
            book = self.book_parser.parse_book(url, book_detail_content.decode("utf8"))
        return book

    def random_sleep(self):
        random_sec = random.random() / 10
        print("Random sleep time {}s".format(random_sec))
        time.sleep(random_sec)


class GenericSearchBookHtmlParser:
    def __init__(self, definition: GenericSearchDefine):
        self.definition = definition
        self.id_pattern = definition.book_url_pattern

    def parse_book(self, url, book_content):
        book = GenericSearchMetaRecord(
            id="",
            title="",
            authors=[],
            publisher="",
            description="",
            url="",
            source=MetaSourceInfo(
                id=self.definition.provider_id,
                description=self.definition.provider_name,
                link=self.definition.base_url
            )
        )
        html = etree.HTML(book_content)
        book.title = self.definition.get_title(html)
        book.url = url
        id_match = self.id_pattern.match(url)
        if id_match:
            book.id = id_match.group(1)
        book.cover = self.definition.get_cover(html)
        book.publisher = self.definition.provider_name
        # rating_element = html.xpath("//strong[@property='v:average']")
        # book.rating = self.get_rating(rating_element)
        book.authors = self.definition.get_author(html)
        book.description = self.definition.get_description(html)
        book.tags = self.definition.get_tags(html)
        return book
