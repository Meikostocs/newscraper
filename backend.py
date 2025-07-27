from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
from dateutil.parser import parse
from utils.extractor import extract_between
from scraper.mmul_scaper import MMULScraper
from scraper.foss_scraper import FOSSScraper
from datetime import datetime

import requests


app = Flask(__name__)
CORS(app)  # Permette richieste da React (localhost:3000)

foss_scraper = FOSSScraper("https://fossforce.com/")
mmul_scraper = MMULScraper("https://www.miamammausalinux.org/")


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
    return jsonify(mmul_scraper.get_article(url))

@app.route('/api/posts', methods=['GET'])
def get_all_posts():
    posts = []
    posts += mmul_scraper.scrape()
    posts += foss_scraper.scrape()
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

