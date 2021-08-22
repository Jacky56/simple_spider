from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options 
from typing import * 
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path
from fake_useragent import UserAgent

PATH = "./website_printscreen/"
ua = UserAgent()


def not_domains(url: str) -> bool:
    exclude_domains = set([
        "google",
        "youtube",
        "facebook",
        "amazon",
        "yahoo",
        "linkedin",
        "microsoft",
        "indeed",
        "vertbaudet",
        "twitter",
        "stackoverflow"
    ])
    return not urlparse(url).netloc.split('.')[0] in exclude_domains
    
def get_config() -> Options:
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1280,720")
    return chrome_options

def get_urls(url: str, html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    domain = urlparse(url).netloc
    urls = set()
    for a in soup.find_all('a', href=True):
        if urlparse(a['href']).netloc:
            urls.add(a['href'])
        else:
            urls.add(f"http://{domain}/{a['href']}")
    return list(urls)

def get_html(driver: webdriver.Chrome, url: str) -> tuple:
    headers = {
        'User-Agent': ua.random
    }
    status_code = requests.get(url, headers=headers).status_code
    driver.get(url)
    return status_code, driver.page_source

def dump_printscreen(path: str, driver: webdriver.Chrome, create_folder: bool=True) -> str:  
    unix_timestamp = int(datetime.now().timestamp() * 10000)
    domain = urlparse(driver.current_url).netloc
    file_path = f"{path}/{domain}_{unix_timestamp}.png"
    if create_folder:
        Path(path).mkdir(parents=True, exist_ok=True)
    driver.get_screenshot_as_file(file_path)
    return str(file_path)

if __name__ == "__main__":
    chromedriver_autoinstaller.install()
    driver = webdriver.Chrome(chrome_options=get_config())

    # used to count how many times domain was taken
    url_checked_count = {}
    # used to exclude urls thats ready been checked
    url_checked = set()

    url_stack = ["https://www.4chan.org"]
    
    while url_stack and len(url_checked_count) < 1000:
        current_url = url_stack.pop()
        key = urlparse(current_url).netloc
        if not key in url_checked_count:
            url_checked_count[key] = 0
        url_checked_count[key] += 1
        if url_checked_count[key] < 20 and not_domains(current_url) and (not current_url in url_checked):
            try:
                status, html = get_html(driver, current_url)
                urls = get_urls(driver.current_url, html)
                url_stack.extend(urls)
                if status != 200:
                    path_label = f"{PATH}/{status}/"
                    dump_printscreen(path_label, driver)
            except Exception as e:
                print(e)
                driver = webdriver.Chrome(chrome_options=get_config())

        url_checked.add(current_url)

    print("spider complete.")