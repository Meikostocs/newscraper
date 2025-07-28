import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from urllib.parse import urlparse

from utils.extractor import extract_between
from utils.parser import parse_date, get_scraper_classes, sanitize_parameters

SCRAPER_MAP = get_scraper_classes()

app = Flask(__name__)
CORS(app)  # Permette richieste da React (localhost:3000)


@app.route('/api/posts', methods=['POST'])
def get_post():
    data = request.json
    url = data.get('url')
    scraper_class = SCRAPER_MAP.get(urlparse(url).netloc.replace("www.", ""))
    return jsonify(sanitize_parameters(scraper_class.get_article(url)))


@app.route('/api/posts', methods=['GET'])
def get_all_posts():
    posts = []
    for _, scraper_class in SCRAPER_MAP.items():
        posts += scraper_class.scrape().copy()
    sorted_posts = sorted(posts, key=parse_date, reverse=True)
    sanitized = [sanitize_parameters(p) for p in sorted_posts]
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
    app.run(host='0.0.0.0', port=8000, debug=True)

