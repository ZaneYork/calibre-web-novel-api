from cps.metadata_provider.net.Zxcs import Zxcs

if __name__ == "__main__":
    zxcs = Zxcs()
    result = zxcs.search("夜的命名术;会说话的肘子")
    for book in result:
        print(book)
