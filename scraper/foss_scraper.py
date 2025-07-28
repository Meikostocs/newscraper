import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from utils.extractor import extract_between
from scraper.scraper import Scraper
from urllib.parse import urlparse, urlunparse
import re

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
            if "The Top Five" in title or "Open Tech News Quiz" in title: 
                continue
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
                    'imgix_url': img_url,
                    'teaser': teaser,
                }
            }

            articles.append(article)
        return articles.copy()


    def get_article(self,url):
        if not url:
            return jsonify({"error": "Missing url"}), 400

        resp = requests.get(url)
        if resp.status_code != 200:
            return jsonify({"error": "Cannot fetch URL"}), 500

        soup = BeautifulSoup(resp.text, 'html.parser')

        article_id = url

        # Get title
        title_tag = soup.find('h1', class_='post-title')
        title = title_tag.get_text(strip=True) if title_tag else 'No title'
        
        # Get figure
        img_url = extract_between(resp.text, '<img data-recalc-dims="1" decoding="async" src="', '"')

        parsed = urlparse(img_url.replace('<img data-recalc-dims="1" decoding="async" src="', ''))
        clean_url = parsed._replace(query="")  
        clean_img_url = urlunparse(clean_url)

        thumbnails = clean_img_url if clean_img_url else ''

        author_name = ""
        created_at = ""
        # Get creation date and author name
        byline_div = soup.find('div', class_='post-byline')

        if byline_div:
            text = byline_div.get_text(separator=' ', strip=True).split("|")[0].strip()
            match = re.search(r"By (.*?) on ([A-Za-z]+\s\d{1,2},\s\d{4})", text)
            if match:
                author_name = match.group(1)
                created_at = match.group(2)

        # Get article body
        allowed_tags = ['p', 'li', 'blockquote', 'h2', 'h3', 'table', 'th', 'tr', 'td']

        extracted_html = extract_between(resp.text, '<p>', '<div class="saboxplugin-wrap"')
        soup = BeautifulSoup(extracted_html, 'html.parser')
        
        for ad in soup.select('.fossf-in-article-1, .fossf-in-article-3, .sharedaddy'):
            ad.decompose()

        content = []
        for tag in soup.find_all(allowed_tags):
            if tag.find_parent(allowed_tags):
                continue
            content.append(str(tag))


        text = "\n".join(content)
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
