from cps.metadata_provider.net.Qidian import Qidian

if __name__ == "__main__":
    qidian = Qidian()
    result = qidian.search("第一序列")
    for book in result:
        print(book)
