import requests

def main():
    key = 'QRkPc39JGyW3XkL49JaHQ'
    secret = 'tI3UcydWViHHv7invrWVapXjxTCZK96ZGTaZkRFiWg'
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"isbns": '0586064176', "key": key})
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    data = res.json()
    print(data)

if __name__ == "__main__":
    main()
