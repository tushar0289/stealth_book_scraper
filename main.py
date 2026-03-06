from curl_cffi import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import json, time, random, re
from antiban_code import get_safe_proxies # Custom module for some useful functions


ua = UserAgent()
books_detail = []


def fetch_with_retry(url, session, retries=3):
    delay = 5
    for i in range(retries):
        try:
            response = session.get(url, impersonate="chrome110", timeout=(6, 20))
            
            if response.status_code == 200:
                return response
            
            print(f"Attempt {i+1}, Status Code: {response.status_code}...")

            if response.status_code == 403:
                print("403 Forbidden Error! IP Most likely flagged.")

        except Exception as e:
            print(f"Error: {e}")

        wait_time = delay * 2 ** i + random.uniform(2, 5)
        print(f"Waiting {wait_time: .2f}s before retry...")
        time.sleep(wait_time)

        if working_proxies:
            p_addr = random.choice(working_proxies)
            proxy = {
                "http": f"http://{p_addr}",
                "https": f"http://{p_addr}"
            }

            session.proxies = proxy

        else:
            print("No proxies left to try.")

    return None


def load_proxies(filename):
    with open(filename, 'r') as rf:
        return [line.strip() for line in rf if line.strip()]


test_proxies = load_proxies("proxies.txt") 
working_proxies = get_safe_proxies(test_proxies)


base_url = "https://books.toscrape.com/"
session = requests.Session()
end_point = "catalogue/category/books/romance_8/index.html"

session.headers.update(
    {
        "User-Agent": ua.chrome,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1", # Do Not Track
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
)

p_addr = random.choice(working_proxies)
proxy = {
    "http": f"http://{p_addr}",
    "https": f"http://{p_addr}"
}

session.proxies = proxy

session.get(base_url, impersonate="chrome110")
url = base_url + end_point
r = fetch_with_retry(url, session)

if r:
    soup = BeautifulSoup(r.content, "lxml")
    books = soup.select("article.product_pod")

    for book in books:
        title = book.select_one("h3 a").get("title")
        raw_price = book.select_one("p.price_color").text
        price = re.search(r"(\d+\.?\d+)", raw_price)
        if price:
            price = float(price.group(1))
        else:
            price = 0.0
        availability = book.select_one("p.instock").text.strip()

        single_book = {
            "title": title,
            "price": price,
            "availability": availability
        }

        books_detail.append(single_book)

    """for book in books_detail:
        print(book)"""
    print(json.dumps(books_detail, indent=4))

else:
    print("Failed to reach the target after all retries. Use Other proxies")