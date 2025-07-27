import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from utils.extractor import extract_between
from scraper.scraper import Scraper

class FOSSScraper(Scraper):


    def __init__(self, base_url):
        self.base_url = base_url


    def scrape(self):
        response = requests.get(self.base_url)
        if response.status_code != 200:
            print(f"Errore nel caricamento della pagina: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []

        for post in soup.select('div.loop-container > div.entry'):
            article_tag = post.find('article')

            title_tag = article_tag.select_one('h2.post-title a')
            title = title_tag.text.strip()
            link = title_tag['href'].strip()

            byline = article_tag.select_one('.post-byline')
            author = byline.text.strip().split(' on ')[0].replace("By ", "")
            date = byline.text.strip().split(' on ')[-1].split(' | ')[0].strip()

            img_tag = article_tag.select_one('.featured-image img')
            img_url = img_tag['src'] if img_tag else None

            teaser_tag = article_tag.select_one('.post-content p')
            teaser = teaser_tag.text.strip() if teaser_tag else ''

            article = {
                'id': link,
                'title': title,
                'metadata': {
                    'published_date': date,
                    'author': {'title': author, 'pfp': self.default_pfp},
                    'date': date,
                    'imgix_url': img_url,
                    'teaser': teaser,
                }
            }

            articles.append(article)
        return articles.copy()


    def get_article(self, url):
        pass