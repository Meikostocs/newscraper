## 🤝 Contributing

Thank you for considering a contribution to this project!

This guide explains how to add a **new news source** to the scraper system.

---

### 🧱 Step 1: Create a Scraper Class

Add a new Python file in the `scraper/` directory. Your class must inherit from the abstract base class `Scraper` and implement the required methods.

**Example:**

```python
from .base_scraper import Scraper

class MyNewScraper(Scraper):
    def __init__(self, base_url: str):
        super().__init__(base_url)

    def scrape(self):
        # Return a list of preview articles
        return [{
            'id': link,
            'title': title,
            'metadata': {
                'published_date': date,
                'author': {'title': author, 'pfp': self.default_pfp},
                'imgix_url': img_url,
                'teaser': teaser,
            }
        }]

    def get_article(self, url: str):
        # Return the full article details
        return {
            'id': article_id,
            'title': title,
            'metadata': {
                'imgix_url': thumbnails,
                'published_date': created_at,
                'author': {
                    'pfp': self.default_pfp,
                    'title': author_name
                }
            },
            'text': text,
        }
```

---

### 🗂 Step 2: Register the Scraper in `parser.py`

In `utils/parser.py`, register the new class in the `SCRAPER_CLASSES` dictionary:

```python
SCRAPER_CLASSES = {
    # ...
    "MyNewScraper": MyNewScraper # <- Add this
}
```

---

### ⚙️ Step 3: Add Domain Mapping in `config/scrapers.yaml`

Add your new scraper to the YAML config file:


```yaml
mynewsite.com:
  name: MyNewScraper
  base_url: https://mynewsite.com
```

This tells the system which scraper class to use based on the domain of the incoming URL.

---

### ✅ Final Notes

- Your scraper should avoid relying on brittle HTML structure.
- Filter out ads or unrelated sections.
- All article content will be sanitized server-side for security.

Thanks again for contributing 🙌
