# stealth_book_scraper

A lightweight, stealth-oriented python scraper designed to extract data from [Books to Scrape](https://books.toscrape.com/) and output it in a structures json format.

### Key Features
- **Session Persistance:** Begins every crawl from the homepage to establish valid cookies and headers, mimicking organic user behavior.

- **Proxy Rotation:** Rotates through safe proxy list to bypass IP Rate Limiting.

- **JSON Output:** Formats raw HTML data into clean, structured JSON structure.

- **Pagination Handling:** Handles pagination, retries with different proxy if fails.


### Project Workflow

The script reads the **proxies.txt** file, filters out dead or transparent proxies. (Proxies I used in the text files are some free proxies which gets cleaned by *get_safe_proxies* function. Include any text file named **proxies.txt** inside the project's root directory containing IP address in the **IP:PORT** format (one per line).)

Using random proxy from the safe proxy list, the script connects with the website, mimicking a real browser and gets the raw html data.

Finally the HTML data gets cleaned and output structured JSON.


### Disclaimer and Future Roadmap

This scraper only showcases basic scraping with all antiban precautions. Please note that, I haven't included the custom module **antiban_code** in this project. It needs some work. I might add it in future after refining it a bit.

For now, you can add a list of working proxies inside the **working_proxies** variable and remove the test_proxies and the module from the script.
