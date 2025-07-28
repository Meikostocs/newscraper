import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from utils.extractor import extract_between
from scraper.scraper import Scraper
from datetime import datetime

import re

class RHCScraper(Scraper):


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

        posts = soup.select('article.elementor-post')
        if posts:
            # First one is duplicated
            posts = posts[1:]  
        
        for post in posts:
            try:
                link_tag = post.select_one('h2 a, h3 a')
                link = link_tag['href'].strip() if link_tag else None

                title = link_tag.get_text(strip=True) if link_tag else None

                author_tag = post.select_one('.elementor-post-author')
                author = author_tag.get_text(strip=True) if author_tag else "Sconosciuto"

                date_tag = post.select_one('.elementor-post-date')
                raw_date = date_tag.get_text(strip=True) if date_tag else None
                if raw_date:
                    try:
                        date_obj = datetime.strptime(raw_date, "%d/%m/%Y")
                    except ValueError:
                        date_obj = datetime.strptime(raw_date, "%d/%m/%y")
                    date = date_obj.strftime("%b, %d %Y")
                else:
                    date = None

                img_tag = post.select_one('img')
                img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None
                if img_url:
                    img_url = re.sub(r'-\d+x\d+(?=\.\w{3,4}$)', '', img_url)


                teaser_tag = post.select_one('.elementor-post__excerpt, .elementor-post__text p')
                teaser = teaser_tag.get_text(strip=True) if teaser_tag else ""

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
                print("Errore durante il parsing di un articolo:", e)

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

        title_tag = soup.select_one("h1")
        title = title_tag.get_text(strip=True) if title_tag else None
        
        author_tag = soup.select_one("a[href*='/post/author/']")
        author_name = author_tag.get_text(strip=True) if author_tag else "Sconosciuto"
        
        date_match = extract_between(str(soup), "</a> : ", "</b></span><p>").replace("</a> : ", "")
        date_match = re.search(r'(\d{1,2} \w+ \d{4})', date_match).group(1)

        months = {
            "Gennaio": "Jan", "Febbraio": "Feb", "Marzo": "Mar", "Aprile": "Apr", "Maggio": "May", "Giugno": "Jun",
            "Luglio": "Jul", "Agosto": "Aug", "Settembre": "Sep", "Ottobre": "Oct", "Novembre": "Nov", "Dicembre": "Dec"
        }
        created_at = None
        if date_match:
            day, month_it, year = date_match.split()
            created_at = f"{months.get(month_it, 'Jan')}, {int(day):02d} {year}"


        img_tag = soup.select_one("img.wp-post-image")
        thumbnails = img_tag["src"] if img_tag else None
        if thumbnails:
            thumbnails = re.sub(r'-\d+x\d+(?=\.\w{3,4}$)', '', thumbnails)

        for adv in soup.select(".advertising-rhc"):
            adv.decompose()

        new_text = str(soup)
        text = extract_between(new_text, '</b></span><p>', '<div class="tag-list"')        
        with open("out.txt",'w') as fout:
            fout.write(new_text)

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
            "text": text
        }

        return article
