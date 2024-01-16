from cps.metadata_provider.net.Fanqie import Fanqie

if __name__ == "__main__":
    fanqie = Fanqie()
    result = fanqie.search("夺舍;木牛流猫")
    for book in result:
        print(book)
