import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import threading
from queue import Queue
from selenium import webdriver
from urllib import robotparser


class AdvancedCrawler:
    def __init__(self, base_url, max_depth=3, max_threads=5, rate_limit=1, obey_robots=True):
        self.base_url = base_url
        self.max_depth = max_depth
        self.max_threads = max_threads
        self.rate_limit = rate_limit  # seconds between requests
        self.obey_robots = obey_robots

        self.visited = set()
        self.to_visit = Queue()
        self.to_visit.put((base_url, 0))
        self.robots = robotparser.RobotFileParser()
        self.robots.set_url(urljoin(base_url, "/robots.txt"))
        self.robots.read()
        self.lock = threading.Lock()

    def is_allowed_by_robots(self, url):
        if self.obey_robots:
            return self.robots.can_fetch("*", url)
        return True

    def crawl(self):
        threads = []
        for _ in range(self.max_threads):
            thread = threading.Thread(target=self.worker)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def worker(self):
        while not self.to_visit.empty():
            url, depth = self.to_visit.get()
            if depth <= self.max_depth and url not in self.visited and self.is_allowed_by_robots(url):
                self.visited.add(url)
                self.process_url(url, depth)
                time.sleep(self.rate_limit)

    def process_url(self, url, depth):
        try:
            print(f"Processing: {url} (Depth: {depth})")
            response = requests.get(url, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract and queue new URLs
            self.extract_links(url, soup, depth)

            # Handle forms
            self.handle_forms(url, soup)

            # Handle dynamic content (if any)
            self.handle_dynamic_content(url)

        except requests.RequestException as e:
            print(f"Error processing {url}: {e}")

    def extract_links(self, base_url, soup, depth):
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(base_url, a_tag['href'])
            if self.is_valid_url(link):
                with self.lock:
                    self.to_visit.put((link, depth + 1))

    def handle_forms(self, url, soup):
        for form in soup.find_all('form'):
            action = form.get('action')
            method = form.get('method', 'get').lower()
            form_url = urljoin(url, action)
            form_data = {input_tag.get('name'): input_tag.get('value', '') for input_tag in form.find_all('input') if
                         input_tag.get('name')}

            if method == 'post':
                response = requests.post(form_url, data=form_data, verify=False)
            else:
                response = requests.get(form_url, params=form_data, verify=False)

            print(f"Submitted form to {form_url} with data {form_data}")

    def handle_dynamic_content(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(2)  # Allow time for dynamic content to load

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        self.extract_links(url, soup, 0)  # Extract additional links
        driver.quit()

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        return bool(parsed_url.netloc) and bool(parsed_url.scheme) and parsed_url.scheme in ['http', 'https']


if __name__ == "__main__":
    base_url = "http://asi.payumoney.com"
    crawler = AdvancedCrawler(base_url, max_depth=3, max_threads=5, rate_limit=1)
    crawler.crawl()
    print(f"Visited URLs: {crawler.visited}")
