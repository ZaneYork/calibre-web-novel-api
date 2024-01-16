from cps.metadata_provider.net.Tadu import Tadu

if __name__ == "__main__":
    tadu = Tadu()
    result = tadu.search("全职修真高手;洗剑")
    for book in result:
        print(book)
