from abc import ABC, abstractmethod

class Scraper(ABC):
    """
    Abstract base class for all scraper implementations.

    Any subclass must implement both `scrape()` and `get_article(url)` methods,
    and define a base URL for the source site.
    """
  

    default_pfp = "https://cdn-icons-png.flaticon.com/512/6676/6676023.png"

    @abstractmethod 
    def __init__(self, base_url: str) -> None:
        """
        Initialize the scraper with the given base URL.

        Args:
            base_url (str): The root URL of the target news site.
        """
        self.base_url = base_url

    @abstractmethod
    def scrape(self) -> dict:
        """
        Scrapes a list of article previews from the base URL.

        Returns:
            list[dict]: A list of articles with the following structure:
                {
                    'id': str,                # The full article URL
                    'title': str,             # The headline of the article
                    'metadata': {
                        'published_date': str,   # Publication date (ISO 8601 or readable format)
                        'author': {
                            'title': str,        # Author name
                            'pfp': str           # Author avatar URL (default if missing)
                        },
                        'imgix_url': str,        # URL of the article's main image
                        'teaser': str            # Short preview or excerpt from the article
                    }
                }

        Note:
            The 'id' field is used as a unique identifier and should match the article's link.
        """
        pass

    @abstractmethod
    def get_article(self,url: str) -> dict:
        """
        Scrapes the full content of a single article from the provided URL.

        Args:
            url (str): The full URL of the article to scrape.

        Returns:
            dict: A dictionary with the complete article details:
                {
                    "id": str,                  # The article's URL
                    "title": str,               # The full article title
                    "metadata": {
                        "imgix_url": str,       # High-res main image URL
                        "published_date": str,  # Publication date in readable format
                        "author": {
                            "title": str,       # Author name
                            "pfp": str          # Profile picture URL (default if missing)
                        }
                    },
                    "text": str                 # Sanitized HTML content of the full article
                }

        Note:
            The 'text' field may contain allowed HTML tags (e.g. <p>, <ul>, <img>, etc.).
        """
        pass