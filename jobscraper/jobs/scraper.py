# jobs/scraper.py
import time
import random
import logging
import urllib.parse
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import feedparser
from .models import Job, ScrapeLog

logger = logging.getLogger(__name__)

def get_stealth_driver():
    """Returns a Chrome WebDriver with anti-detection settings."""
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    driver.execute_script("delete navigator.__proto__.webdriver")
    driver.set_page_load_timeout(15)
    return driver

def scrape_indeed_selenium(query, location, max_pages):
    """Scrape Indeed using Selenium with improved resilience."""
    driver = get_stealth_driver()
    jobs_created = 0
    duplicates = 0
    base_url = "https://www.indeed.com"

    try:
        encoded_query = urllib.parse.quote(query)
        encoded_location = urllib.parse.quote(location) if location else ""

        for page in range(max_pages):
            start = page * 10
            url = f"{base_url}/jobs?q={encoded_query}&l={encoded_location}&start={start}"
            logger.info(f"Scraping Indeed page {page + 1}: {url}")
            driver.get(url)

            # Wait for job cards to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.job_seen_beacon"))
                )
            except:
                logger.warning(f"No job cards loaded on page {page + 1}")
                break

            time.sleep(random.uniform(1.5, 3.0))  # Human-like delay
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_cards = soup.select('div.job_seen_beacon')

            if not job_cards:
                logger.info("No more job cards found. Ending scrape.")
                break

            for card in job_cards:
                try:
                    # Title
                    title_tag = card.select_one('h2.jobTitle span[title]')
                    title = title_tag['title'] if title_tag else None
                    if not title:
                        title_elem = card.select_one('h2.jobTitle')
                        title = title_elem.get_text(strip=True) if title_elem else "N/A"

                    # Company
                    company_elem = card.select_one('span.companyName')
                    company = company_elem.get_text(strip=True) if company_elem else "N/A"

                    # Location
                    loc_elem = card.select_one('div.companyLocation')
                    job_location = loc_elem.get_text(strip=True) if loc_elem else location or "N/A"

                    # URL
                    link = card.select_one('h2.jobTitle a')
                    if not link or not link.get('href'):
                        continue
                    source_url = base_url + link['href'] if link['href'].startswith('/') else link['href']

                    # Deduplication
                    if Job.objects.filter(source_url=source_url).exists():
                        duplicates += 1
                        continue

                    # Save
                    Job.objects.create(
                        title=title,
                        company=company,
                        location=job_location,
                        source='indeed',
                        source_url=source_url,
                        scraped_at=timezone.now(),
                        is_active=True
                    )
                    jobs_created += 1

                except Exception as e:
                    logger.error(f"Error parsing job card: {e}")
                    continue

    except Exception as e:
        logger.exception(f"Selenium scraping failed: {e}")
        raise
    finally:
        driver.quit()

    return jobs_created, duplicates

def scrape_indeed_rss(query, location, max_pages=1):
    """Fallback: scrape Indeed via public RSS feed (no JS, no blocking)."""
    encoded_query = urllib.parse.quote(query)
    encoded_location = urllib.parse.quote(location) if location else ""
    rss_url = f"https://www.indeed.com/rss?q={encoded_query}&l={encoded_location}"
    logger.info(f"Using Indeed RSS: {rss_url}")

    feed = feedparser.parse(rss_url)
    jobs_created = 0
    duplicates = 0

    for entry in feed.entries[:20]:  # Limit to 20 jobs
        try:
            if Job.objects.filter(source_url=entry.link).exists():
                duplicates += 1
                continue

            Job.objects.create(
                title=entry.title,
                company=getattr(entry, 'author', 'Unknown'),
                location=location or "N/A",
                description=getattr(entry, 'summary', ''),
                source='indeed',
                source_url=entry.link,
                scraped_at=timezone.now(),
                is_active=True
            )
            jobs_created += 1
        except Exception as e:
            logger.error(f"RSS job save error: {e}")

    return jobs_created, duplicates

def scrape_indeed(query, location, max_pages):
    """Try Selenium first; fall back to RSS if it fails or returns 0 jobs."""
    try:
        jobs, dups = scrape_indeed_selenium(query, location, max_pages)
        if jobs == 0:
            logger.info("Selenium returned 0 jobs. Falling back to RSS.")
            return scrape_indeed_rss(query, location, max_pages)
        return jobs, dups
    except Exception as e:
        logger.warning(f"Selenium failed, using RSS fallback: {e}")
        return scrape_indeed_rss(query, location, max_pages)

# Placeholders (safe, non-breaking)
def scrape_linkedin(query, location, max_pages):
    logger.info("LinkedIn scraping skipped (requires login & bypasses not implemented)")
    return 0, 0

def scrape_glassdoor(query, location, max_pages):
    logger.info("Glassdoor scraping skipped (requires login & anti-bot protection)")
    return 0, 0

def scrape_jobs_from_source(source, query, location, max_pages=1):
    """Main entry point for scraping jobs from a source."""
    start_time = timezone.now()
    jobs_scraped = 0
    duplicates_found = 0
    error_msg = ""
    status = "success"

    try:
        if source == "indeed":
            jobs_scraped, duplicates_found = scrape_indeed(query, location, max_pages)
        elif source == "linkedin":
            jobs_scraped, duplicates_found = scrape_linkedin(query, location, max_pages)
        elif source == "glassdoor":
            jobs_scraped, duplicates_found = scrape_glassdoor(query, location, max_pages)
        else:
            raise ValueError(f"Unsupported source: {source}")

    except Exception as e:
        status = "failed"
        error_msg = str(e)
        logger.error(f"Scraping failed for {source}: {e}")

    # Log the result
    ScrapeLog.objects.create(
        source=source,
        status=status,
        jobs_scraped=jobs_scraped,
        duplicates_found=duplicates_found,
        error_message=error_msg[:500],  # Truncate if too long
        completed_at=timezone.now()
    )

    logger.info(f"Scrape completed: {source} | Jobs: {jobs_scraped} | Duplicates: {duplicates_found}")