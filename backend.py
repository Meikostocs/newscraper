from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
from dateutil.parser import parse
import requests
import re

app = Flask(__name__)
CORS(app)  # Permette richieste da React (localhost:3000)
MMUL_URL = "https://www.miamammausalinux.org/"
FOSS_URL = "https://fossforce.com/"

default_pfp = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/340px-Default_pfp.svg.png"

def extract_between(text: str, str_start: str, str_end: str) -> str:
    pattern = re.escape(str_start) + r'(.*?)' + re.escape(str_end)
    match = re.search(pattern, text, re.DOTALL)
    return str_start + match.group(1) if match else ''

def scrape_mmul():
    response = requests.get(MMUL_URL)
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
                    'author': {'title':author, "pfp": default_pfp},
                    'date': date,
                    'imgix_url': img_url,
                    'teaser': teaser,
                }

            }
            articles.append(article)
        except Exception as e:
            print(f"Errore nell'estrazione di un articolo: {e}")
            return []

    return articles.copy()

def get_article_mmul(url):
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
                "pfp": default_pfp,
                'title': author_name
            }
        },
        "text": text,
    }

    return jsonify(article)

def scrape_foss():
    response = requests.get(FOSS_URL)
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
                'author': {'title': author, 'pfp': default_pfp},
                'date': date,
                'imgix_url': img_url,
                'teaser': teaser,
            }
        }

        articles.append(article)
    return articles.copy()


def parse_date(post):
    try:
        dt = parse(post["metadata"]["date"])
        return dt.replace(tzinfo=None)
    except Exception as e:
        print(f"[!] Errore parsing data per '{post['title']}': {e}")
        return datetime.min


@app.route('/api/posts', methods=['POST'])
def get_post():
    data = request.json
    url = data.get('url')
    return get_article_mmul(url)

@app.route('/api/posts', methods=['GET'])
def get_all_posts():
    posts = []
    posts += scrape_mmul()
    posts += scrape_foss()

    sorted_posts = sorted(posts, key=parse_date, reverse=True)

    return jsonify(sorted_posts)



@app.route('/api/global', methods=['GET'])
def get_mock_global():
    return jsonify({
        "metadata": {
            "site_title": "Il Mio News Scraper",
            "site_tag": "Tutte le notizie in un posto solo"
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=8000)

