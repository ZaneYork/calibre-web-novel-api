from cps.metadata_provider.NetNovel import NetNovel

if __name__ == "__main__":
    netnovel = NetNovel()
    result = netnovel.search("战皇;傲天无痕")
    for book in result:
        print(book)
