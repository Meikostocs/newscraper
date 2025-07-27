import yaml
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


def parse_date(post):
    try:
        dt = parse(post["metadata"]["date"])
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