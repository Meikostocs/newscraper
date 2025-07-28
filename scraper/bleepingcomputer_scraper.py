import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from utils.extractor import extract_between
from scraper.scraper import Scraper
import re
import jsonify

class BleepingComputerScraper(Scraper):


    def __init__(self, base_url):
        self.base_url = base_url

    def scrape(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

        response = requests.get(self.base_url, headers=headers)
        if response.status_code != 200:
            print(f"Errore nel caricamento della pagina: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        main_block = soup.find('div', class_='bc_latest_news')
        if not main_block:
            return []


        for li in main_block.select('ul#bc-home-news-main-wrap > li'):
                try:
                    link_tag = li.find('h4').find('a')
                    link = link_tag['href']
                    title = link_tag.get_text(strip=True)

                    teaser_tag = li.find('p')
                    teaser = teaser_tag.get_text(strip=True) if teaser_tag else ''

                    img_tag = li.find('div', class_='bc_latest_news_img').find('img')
                    img_url = img_tag.get('data-src') or img_tag.get('src') or ''
                    img_url = re.sub(r'/thumb/\d+x\d+_', '/', img_url)

                    author_tag = li.select_one('.bc_news_author .author') or li.select_one('.bc_news_author')
                    author = author_tag.get_text(strip=True).replace("Sponsorship", "").strip() if author_tag else 'Unknown'
                    if "BleepingComputer Deals" in author or "Nudge Security" in author  or "Sponsorship" in author:
                        continue

                    date_tag = li.select_one('.bc_news_date')
                    date = date_tag.get_text(strip=True) if date_tag else ''

                    articles.append({
                        'id': link,
                        'title': title,
                        'metadata': {
                            'published_date': date,
                            'author': {
                                'title': author,
                                'pfp': self.default_pfp
                            },
                            'imgix_url': img_url,
                            'teaser': teaser
                        }
                    })
                except Exception as e:
                    print(f"[!] Errore parsing articolo: {e}")
                    continue

        return articles.copy()


    def get_article(self,url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

        if not url:
            return jsonify({"error": "Missing url"}), 400

        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return jsonify({"error": "Cannot fetch URL"}), 500

        soup = BeautifulSoup(resp.text, 'html.parser')

        article_id = url

        title = soup.title.string.strip() if soup.title else ""
        
        author_tag = soup.select_one('.cz-news-title-left-area .author span[itemprop="name"]')
        author_name = author_tag.get_text(strip=True) if author_tag else "Unknown"

        date_tag = soup.select_one('.cz-news-date')
        created_at = date_tag.get_text(strip=True) if date_tag else None

        article_body = soup.find('div', class_='articleBody')
        first_img = article_body.find('img')
        thumbnails = first_img['src'] if first_img else None
        
        first_img = article_body.find('img')
        if first_img and first_img.find_parent('p'):
            first_img.find_parent('p').decompose()

        text = extract_between(str(soup), '<div class="articleBody">', "<style>")

        if text=="":
            text = extract_between(str(soup), '<div class="articleBody">', "</article>")
    
        article = {
            "id": article_id,
            "title": title,
            "metadata": {
                "imgix_url" : thumbnails,
                "published_date": created_at,
                "author":{
                    "pfp": self.default_pfp,
                    'title': author_name
                }
            },
            "text": text,
        }

        return article
