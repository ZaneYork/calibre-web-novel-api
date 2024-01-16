from cps.metadata_provider.net.QQReader import QQReader

if __name__ == "__main__":
    qqreader = QQReader()
    result = qqreader.search("第一序列;会说话的肘子")
    for book in result:
        print(book)
