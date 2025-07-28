import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from utils.extractor import extract_between
from scraper.scraper import Scraper

class MMULScraper(Scraper):


    def __init__(self, base_url):
        self.base_url = base_url

    def scrape(self):
        response = requests.get(self.base_url)
        if response.status_code != 200:
            print(f"Errore nel caricamento della pagina: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        class_names = [
            'wp-block-columns',
            'are-vertically-aligned-center',
            'is-layout-flex',
            'wp-container-core-columns-is-layout-28f84493',
            'wp-block-columns-is-layout-flex'
        ]

        articles_divs = soup.find_all(
            lambda tag: tag.has_attr('class') and all(c in tag['class'] for c in class_names)
        )
        articles = []
        for div in articles_divs:
            try:
                img_tag = div.select_one('figure.wp-block-post-featured-image img')
                img_url = img_tag['src'] if img_tag else None

                title_a = div.select_one('h2.wp-block-post-title a')
                title = title_a.text.strip() if title_a else None
                link = title_a['href'] if title_a else None

                cat_a = div.select_one('div.taxonomy-category a')
                category = cat_a.text.strip() if cat_a else None

                author_div = div.select_one('div.wp-block-post-author-name')
                author = author_div.text.strip() if author_div else None

                time_tag = div.select_one('div.wp-block-post-date time')
                date = time_tag['datetime'] if time_tag else None

                teaser_p = div.select_one('div.wp-block-post-excerpt p')
                teaser = teaser_p.text.strip() if teaser_p else None

                article = {
                    'id':link,
                    'title': title,
                    'metadata':{
                        'published_date':date,
                        'author': {'title':author, "pfp": self.default_pfp},
                        'imgix_url': img_url,
                        'teaser': teaser,
                    }

                }
                articles.append(article)
            except Exception as e:
                print(f"Errore nell'estrazione di un articolo: {e}")
                return []

        return articles.copy()

    def get_article(self,url):
        str_start = '<p>'    
        str_end = "<!-- MOLONGUI AUTHORSHIP PLUGIN 5.1.0 -->"


        if not url:
            return jsonify({"error": "Missing url"}), 400

        resp = requests.get(url)
        if resp.status_code != 200:
            return jsonify({"error": "Cannot fetch URL"}), 500

        text = extract_between(resp.text, str_start, str_end)
        soup = BeautifulSoup(resp.text, 'html.parser')

        article_id = url

        title_tag = soup.find('h2', class_='wp-block-post-title')
        title = title_tag.get_text(strip=True) if title_tag else 'No title'

        thumbnail_img = soup.select_one('figure.wp-block-image.aligncenter img')
        thumbnails = thumbnail_img['src'] if thumbnail_img else ''

        time_tag = soup.find('time')
        created_at = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else ''

        author_name = soup.find('a', class_="m-a-box-name-url")
        author_name = author_name.get_text(strip=True)

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
