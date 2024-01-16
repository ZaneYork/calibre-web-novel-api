from cps.metadata_provider.net.Jinjiang import Jinjiang

if __name__ == "__main__":
    jinjiang = Jinjiang()
    result = jinjiang.search("如意书;蒋牧童")
    for book in result:
        print(book)
