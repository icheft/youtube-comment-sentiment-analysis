import re
import sys


def url(raw_url):
    print(raw_url)
    regExp = r'^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*'
    match = re.match(regExp, raw_url)
    if match and len(match[7]) == 11:
        return match[7]
    else:
        return False


if __name__ == "__main__":
    # while(True):
    #     raw_url = input()
    #     print(url(raw_url))

    print(url(sys.argv[1]))
