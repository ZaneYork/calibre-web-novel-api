import traceback

from cps.metadata_provider.net.QQReader import QQReader
from cps.metadata_provider.net.Qidian import Qidian
from cps.metadata_provider.net.Qimao import Qimao
from cps.metadata_provider.net.Fanqie import Fanqie
from cps.metadata_provider.net.Tadu import Tadu
from cps.metadata_provider.net.Zxcs import Zxcs
from cps.services.Metadata import Metadata

PROVIDER_NAME = "网文聚合"
PROVIDER_ID = "netnovel"


class NetNovel(Metadata):
    __name__ = PROVIDER_NAME
    __id__ = PROVIDER_ID

    def __init__(self):
        self.searchers = [
            Qidian(),
            QQReader(),
            Qimao(),
            Fanqie(),
            Tadu(),
            Zxcs()
        ]
        super().__init__()

    def search(self, query: str, generic_cover: str = "", locale: str = "en"):
        if self.active:
            sections = query.split(';')
            author = '未知'
            if len(sections) > 1:
                title = sections[0]
                author = sections[1]
            else:
                title = query
            result_title_match = []
            result_rest = []
            for searcher in self.searchers:
                try:
                    results = searcher.search(query)
                    for result in results:
                        if result.title == title:
                            if author in result.authors:
                                return [result]
                            else:
                                result_title_match.append(result)
                        else:
                            result_rest.append(result)
                except:
                    traceback.print_exc()
            if len(result_title_match) > 0:
                return result_title_match
            result_title_match.extend(result_rest)
            return result_title_match
