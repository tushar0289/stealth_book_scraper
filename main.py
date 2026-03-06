from curl_cffi import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import json, time, random, re, urllib.parse
from antiban_code import get_safe_proxies # Custom module for some useful functions


ua = UserAgent()
books_detail = []
base_url = "https://books.toscrape.com/"
end_point = "catalogue/category/books/romance_8/index.html"


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
            try:
                session.get(base_url, impersonate="chrome110", timeout=(6, 15))
                print("Session re-primed on new proxy.")
            except Exception as e:
                print(f"Re-priming failed on this proxy {(e)}. Trying again.")

        else:
            print("No proxies left to try.")

    return None


def load_proxies(filename):
    with open(filename, 'r') as rf:
        return [line.strip() for line in rf if line.strip()]


test_proxies = load_proxies("proxies.txt") 
working_proxies = get_safe_proxies(test_proxies)


session = requests.Session()

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
url = base_url + end_point
session.get(base_url, impersonate="chrome110", timeout=(6, 15))
page_count = 1


while True:
    r = fetch_with_retry(url, session)

    if not r:
        print("Failed to reach the target after all retries. Use Other proxies")
        break

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

    next_tag = soup.select_one("li.next a")

    with open("books.json", 'w') as wf:
        json.dump(books_detail, wf, indent=4)

    print(f"Page {page_count} parsed")

    if next_tag:
        next_page_url = next_tag.get("href")
        url = urllib.parse.urljoin(url, next_page_url)
        time.sleep(random.uniform(2, 4))
        page_count += 1

    else:
        print("No more pages found!")
        break

