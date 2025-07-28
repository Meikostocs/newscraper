import requests
from flask import Flask, jsonify, request, send_file, render_template
from flask_cors import CORS
from urllib.parse import urlparse
from weasyprint import HTML
from datetime import datetime, timedelta
from io import BytesIO
from dateutil import parser

from utils.extractor import extract_between
from utils.parser import parse_date, get_scraper_classes, sanitize_parameters

# Dictionary mapping each domain to its corresponding scraper class
SCRAPER_MAP = get_scraper_classes()

app = Flask(__name__)
CORS(app) 


@app.route('/api/posts', methods=['POST'])
def get_post():
    """
    Retrieve a single article from a specific URL.

    - Expects a JSON payload with a 'url' field.
    - Determines the appropriate scraper based on the domain.
    - Calls the scraper's `get_article()` method to extract the article content.
    - Sanitizes the result to remove potentially unsafe content.
    - Returns the article as a JSON response.
    """
    data = request.json
    url = data.get('url')
    scraper_class = SCRAPER_MAP.get(urlparse(url).netloc.replace("www.", ""))
    return jsonify(sanitize_parameters(scraper_class.get_article(url)))


@app.route('/api/posts', methods=['GET'])
def get_all_posts():
    """
    Retrieve a list of articles from all registered scraper sources.

    - Iterates over all configured scraper classes.
    - Calls each scraper's `scrape()` method to fetch articles.
    - Sorts articles by publication date (most recent first).
    - Sanitizes each article.
    - Returns a JSON array of all posts.
    """
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


@app.route("/api/newspaper", methods=["GET"])
def generate_newspaper():
    """
    Generate a PDF newspaper containing articles published yesterday.

    - Iterates over all configured scrapers in SCRAPER_MAP.
    - For each scraper, calls `scrape()` to get article summaries.
    - Filters articles whose `published_date` matches yesterday's date.
    - Uses `get_article(id)` to retrieve full content for matching articles.
    - Renders the articles into HTML using the `journal.html` template.
    - Converts the rendered HTML into a PDF using WeasyPrint.
    - Returns the PDF file as an HTTP response with appropriate headers.

    Returns:
        A Flask `send_file` response containing the generated PDF.
    """
    articles = []
    yesterday = datetime.now().date() - timedelta(days=1)
    for _, scraper in SCRAPER_MAP.items():
        for a in scraper.scrape():
            date_str = a["metadata"]["published_date"]
            pub_date = datetime.strptime(date_str, "%b %d, %Y").date()
            if  yesterday == pub_date:
                    full = scraper.get_article(a["id"])
                    articles.append(full)

    html = render_template("journal.html", articles=articles)
    pdf_io = BytesIO()
    HTML(string=html).write_pdf(pdf_io)
    pdf_io.seek(0)
    return send_file(pdf_io, download_name=f"newspaper.pdf", mimetype="application/pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)

