import csv
import datetime
import feedparser
import requests
from pathlib import Path
from openai import OpenAI
import logging
from bs4 import BeautifulSoup
from slack_sdk import WebClient

# Constants
MODEL = "gpt-4o"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
OPENAI_API_KEY = ""
SLACK_TOKEN = ''
CHANNEL_ID = ''
RSS_URLS_CSV = "rss_urls.csv"
LAST_DATE_FILE = Path("last_date.txt")
START_DATE = datetime.datetime(2024, 3, 18, 0, 0, 0)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


def scrape_web_page(url, type="", to_search=""):
    """Scrapes the web page at the given URL and returns its main content as text."""
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        main_content = soup.find(id=to_search) if type == "id" else soup.find(class_=to_search)

        return main_content.get_text(strip=True) if main_content else "Could not find main content."
    except requests.RequestException as e:
        logging.error(f"Error scraping web page: {e}")
        return f"Error scraping web page: {e}"


def summarize_content(content):
    """Summarizes the given content using the OpenAI API."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Summarize content."},
                {"role": "user", "content": f"Please summarize this content: \n\n{content}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return ""


def send_to_slack(rss_name, title, summary, published_date, url):
    """Send a message to a Slack channel."""
    blocks = [{
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"*{rss_name}*\n<{url}|*{title}*>\n\n*Summary:* {summary} \n\n Published on {published_date}"}
    }]

    client = WebClient(token=SLACK_TOKEN)
    try:
        client.chat_postMessage(channel=CHANNEL_ID, blocks=blocks)
    except Exception as e:
        logging.error(f"Error sending message to Slack: {e}")


def load_last_captured_date():
    """Load the last captured date from a file."""
    if LAST_DATE_FILE.exists():
        try:
            with LAST_DATE_FILE.open("r", encoding="utf-8") as file:
                file_content = file.read().strip()
                return datetime.datetime.strptime(file_content, "%Y-%m-%d %H:%M:%S") if file_content else datetime.datetime.min
        except ValueError:
            logging.error("Invalid date format in last_date.txt. Using minimum datetime.")
            return datetime.datetime.min
    else:
        return datetime.datetime.min


def save_last_captured_date(date):
    """Save the new last captured date to a file."""
    with LAST_DATE_FILE.open("w", encoding="utf-8") as file:
        file.write(date.strftime("%Y-%m-%d %H:%M:%S"))
        logging.info("Updated last captured date to %s", date)


def process_rss_entries(feed, rss_name, type, element, last_captured_date):
    """Process entries in an RSS feed."""
    for entry in feed.entries:
        published_date = datetime.datetime(*entry.published_parsed[:6])
        if published_date > START_DATE and published_date > last_captured_date:
            logging.info(f"Processing entry: {entry.link}")
            if rss_name == "Atlassian Developer - Changelog for Jira":
                summary = summarize_content(entry.description)
            else:
                page_main_content = scrape_web_page(entry.link, type, element)
                summary = summarize_content(page_main_content)
            send_to_slack(
                rss_name,
                entry['title'],
                summary,
                published_date.strftime("%Y-%m-%d"),
                entry.link
            )


def process_non_rss_url(rss_name, rss_url, last_captured_date):
    """Process non-RSS URLs."""
    logging.info(f"Processing URL: {rss_url}")
    response = requests.get(rss_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all('div', class_='collection-item-6')

    for div in divs:
        text_block = div.find('div', class_='text-block-30')
        if text_block:
            published_date = datetime.datetime.strptime(text_block.text, "%B %d, %Y")
            if published_date > START_DATE and published_date > last_captured_date:
                links = div.find_all('a', class_='link-block-8', href=True)
                for link in links:
                    first_div_in_a = link.find('div')
                    if first_div_in_a:
                        title = first_div_in_a.text
                    url = link['href']
                    content = scrape_web_page(url)
                    summary = summarize_content(content)
                    send_to_slack(rss_name, title, summary, published_date.strftime("%Y-%m-%d"), url)


def process_rss_feeds():
    """Process RSS feeds from a CSV file."""
    last_captured_date = load_last_captured_date()

    with open(RSS_URLS_CSV, "r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            is_rss = row['RSS'].lower() == "true"
            rss_name = row['Name']
            rss_url = row['RSS URL']
            type = row['Type']
            element = row['Element']

            if is_rss:
                feed = feedparser.parse(rss_url)
                process_rss_entries(feed, rss_name, type, element, last_captured_date)
            else:
                process_non_rss_url(rss_name, rss_url, last_captured_date)

    save_last_captured_date(datetime.datetime.now())


# Entry point for the script
if __name__ == "__main__":
    process_rss_feeds()
