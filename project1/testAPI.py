import requests

def testAPI(isbn):
    res = requests.get("http://127.0.0.1:5000/api/{}".format(isbn))
    if res.status_code == 404:
        print("status_code: {}".format(res.status_code))
    print(res)

if __name__ == "__main__":
    isbn = str(input("Enter isbn: "))
    testAPI(isbn)