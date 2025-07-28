import yaml
import bleach

from datetime import datetime

from dateutil.parser import parse

from scraper.mmul_scaper import MMULScraper
from scraper.foss_scraper import FOSSScraper
from scraper.bleepingcomputer_scraper import BleepingComputerScraper

SCRAPER_CLASSES = {
    "FOSSScraper": FOSSScraper,
    "MMULScraper": MMULScraper,
    "BleepingComputer": BleepingComputerScraper
}

ALLOWED_TAGS = ['p', 'ul', 'ol', 'li', 'strong', 'em', 'blockquote', 'a', 'h2', 'h3', 'br', 'img']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
}


def parse_date(post):
    try:
        dt = parse(post["metadata"]["published_date"])
        return dt.replace(tzinfo=None)
    except Exception as e:
        print(f"[!] Errore parsing data per '{post['title']}': {e}")
        return datetime.min

def loadScrapers():
    with open("config/scrapers.yaml", "r") as f:
        scraper_config = yaml.safe_load(f)
    
    return scraper_config

def get_scraper_classes():
    scraper_config = loadScrapers()
    SCRAPER_MAP = {}
    for domain, config in scraper_config.items():
        class_name = config["name"]
        base_url = config["base_url"]
        scraper_class = SCRAPER_CLASSES.get(class_name)
        if scraper_class:
            SCRAPER_MAP[domain] = scraper_class(base_url)
    return SCRAPER_MAP


def sanitize_parameters(article: dict) -> dict:
    def sanitize_value(key, value):
        if isinstance(value, str):
            if key == 'text':
                return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
            else:
                # Per tutti gli altri campi: rimuove TUTTI i tag
                return bleach.clean(value, tags=[], strip=True)
        elif isinstance(value, dict):
            return {k: sanitize_value(k, v) for k, v in value.items()}
        elif isinstance(value, list):
            return [sanitize_value(key, v) for v in value]
        else:
            return value

    return {k: sanitize_value(k, v) for k, v in article.items()}