from cps.metadata_provider.net.Qimao import Qimao

if __name__ == "__main__":
    qimao = Qimao()
    result = qimao.search("综武：人在酒楼，捡尸王语嫣;要长记性啊")
    for book in result:
        print(book)
