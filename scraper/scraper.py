from abc import ABC, abstractmethod

class Scraper(ABC):  

    default_pfp = "https://cdn-icons-png.flaticon.com/512/6676/6676023.png"

    @abstractmethod 
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    @abstractmethod
    def scrape(self) -> dict:
        pass

    @abstractmethod
    def get_article(self,url: str) -> dict:
        pass