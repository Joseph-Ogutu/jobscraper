# 🕷️ Job Scraper – Django + Selenium Web Scraping Dashboard

A **Django-based job scraping application** that extracts job listings from **Indeed**, **LinkedIn**, and **Glassdoor**, stores them in a PostgreSQL/SQLite database, and displays them in a responsive dashboard with REST API support.



---

## 🎯 Features

- ✅ **Web Scraping** with **Selenium** (for JS-heavy sites) + **BeautifulSoup** (for static HTML)
- ✅ **Fallback to Indeed RSS** when Selenium is blocked (ensures reliability)
- ✅ **Duplicate prevention** using unique `source_url`
- ✅ **RESTful API** with Django REST Framework (DRF)
- ✅ **Real-time dashboard** with stats, search, and pagination
- ✅ **Background scraping** (non-blocking via threading)
- ✅ **Scrape logging** (`ScrapeLog` model tracks success/failure/duplicates)
- ✅ **Advanced filtering**: by source, company, location, job type
- ✅ **Full-text search** across title, company, and description

---

## 🛠️ Tech Stack

| Layer          | Technologies |
|----------------|--------------|
| **Backend**    | Django 5.2, Django REST Framework |
| **Database**   | SQLite (dev), PostgreSQL (production-ready) |
| **Scraping**   | Selenium, BeautifulSoup4, feedparser (RSS fallback) |
| **Frontend**   | HTML5, CSS3 (custom dashboard) |
| **API**        | REST, JSON, Filtering, Pagination |
| **Dev Tools**  | Python 3.10+, pip, virtualenv |

---

## 📁 Project Structure
jobscraper/
├── jobscraper/              # Django project settings
└── jobs/                    # Main app
    ├── models.py            # Job & ScrapeLog models
    ├── views.py             # API & dashboard views
    ├── serializers.py       # DRF serializers
    ├── scraper.py           # Selenium + RSS scraping logic
    ├── urls.py              # URL routing
    └── templates/
        └── dashboard.html   # Live job dashboard



---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/jobscraper.git
cd jobscraper
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver

3. Use the App 

    Dashboard: http://localhost:8000/dashboard/ 
    API: http://localhost:8000/api/jobs/ 
    Admin: http://localhost:8000/admin/  (create superuser with createsuperuser)

