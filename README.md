# 📰 NewsScraper

**NewsScraper** is a personal project that aggregates articles from various FOSS-related news sites using Python (Flask) on the backend and Next.js on the frontend. Everything runs in Docker, and the frontend pulls data from the backend via internal API.

---

## 📦 Project Structure

```
/
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
├── backend.py
├── scraper/
├── utils/
└── newscraper-react/    # Frontend (Next.js) as a Git submodule
```

---

## 🚀 Features

- Article aggregation from multiple sources (e.g., fossforce.com, miamammausalinux.org, bleepingcomputer.com)
- Automatic parsing and extraction (title, author, date, thumbnail, teaser, full content)
- Sorted by latest post date
- Fully dockerized (only frontend is exposed)
- HTML sanitization to prevent XSS

---

## 🐳 Quickstart with Docker

**Make sure you have Docker and Docker Compose installed.**

```bash
git clone --recurse-submodules https://github.com/Meikostocs/newscraper.git
cd newscraper
docker compose up --build
```

🟢 The app will be available at:  
**http://localhost:3000**

📌 The backend is not exposed to the public. It communicates internally via Docker network.

---

## ⚙️ Manual Setup (Development Only)

### 🔙 Backend (Flask)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend.py
```

### 🌐 Frontend (Next.js)
```bash
cd newscraper-react/
npm install
npm run dev
```

Then visit: [http://localhost:3000](http://localhost:3000)

To configure the API endpoint in dev:
```bash
export NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🔒 Security Notes

- All HTML content rendered in the frontend is **sanitized** to prevent XSS attacks.
- Sanitization is handled using `isomorphic-dompurify` with a strict allowlist of safe HTML tags (e.g. `p`, `ul`, `ol`, `li`, `img`, `blockquote`, etc.).
- This makes it safe to render rich text using `dangerouslySetInnerHTML`.

---

## 🌍 Remote Access Options

This application is intended to run locally or within a private environment, but you may also:

- Make the frontend accessible externally by exposing port **3000** through your router or a reverse proxy.
- Use a **dynamic DNS (DDNS)** service to access your local server from anywhere.
- For improved privacy and security, consider accessing the app via a **VPN** (e.g. WireGuard, OpenVPN) to keep traffic encrypted and internal.

Make sure you understand the implications of exposing services to the public internet.
---

