FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed (e.g., for BeautifulSoup)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Backend runs on 8000 but not exposed outside
CMD ["python", "backend.py"]
