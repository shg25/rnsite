import requests
from bs4 import BeautifulSoup


def scraping_title(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")
    return soup.find("title").text
