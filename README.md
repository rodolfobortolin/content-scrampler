# README.md

## Overview

This script fetches RSS feeds and web page content, summarizes the content using the OpenAI API, and posts the summarized information to a Slack channel. It supports both RSS and non-RSS URLs, and it tracks the last processed date to avoid redundant processing.

## Prerequisites

- Python 3.6+
- OpenAI API key
- Slack API token
- Requests library
- OpenAI library
- BeautifulSoup library
- feedparser library
- Slack SDK library

## Setup

1. **Clone the repository:**
    ```bash
    git clone git@github.com:rodolfobortolin/content-scrampler.git
    cd content-scrampler
    ```

2. **Install required Python packages:**
    ```bash
    pip install requests openai beautifulsoup4 feedparser slack_sdk
    ```

3. **Configuration:**
   - Update the `OPENAI_API_KEY` with your OpenAI API key.
   - Update the `SLACK_TOKEN` and `CHANNEL_ID` with your Slack API token and channel ID.
   - Add your RSS URLs to the `rss_urls.csv` file in the following format:

    | Name | RSS URL | Type | Element | RSS |
    |------|---------|------|---------|-----|
    | Atlassian Developer - Changelog for Jira | https://developer.atlassian.com/blog/rss/ | class | entry-title | true |
    | Example Non-RSS URL | https://example.com/blog | class | content | false |

4. **Logging Configuration:**
   - The script uses the `logging` module to log information. Modify the logging configuration if needed.

## Usage

1. **Run the Script:**
    ```bash
    python main.py
    ```

2. **Output:**
   - The script will post summarized content to the specified Slack channel.

## Script Details

### Functions

- **scrape_web_page(url, type="", to_search=""):**
  - Scrapes the web page at the given URL and returns its main content as text.

- **summarize_content(content):**
  - Summarizes the given content using the OpenAI API.

- **send_to_slack(rss_name, title, summary, published_date, url):**
  - Sends a message to a Slack channel.

- **load_last_captured_date():**
  - Loads the last captured date from a file.

- **save_last_captured_date(date):**
  - Saves the new last captured date to a file.

- **process_rss_entries(feed, rss_name, type, element, last_captured_date):**
  - Processes entries in an RSS feed.

- **process_non_rss_url(rss_name, rss_url, last_captured_date):**
  - Processes non-RSS URLs.

- **process_rss_feeds():**
  - Processes RSS feeds from a CSV file.

### Main Process

1. Loads the last captured date.
2. Reads the RSS URLs from the CSV file.
3. For each URL, processes the RSS or non-RSS content.
4. Summarizes the content using OpenAI API.
5. Posts the summary to the specified Slack channel.
6. Updates the last captured date.

## Logging

The script logs the following information:

- Success or failure of web scraping.
- Success or failure of content summarization.
- Sending messages to Slack.
- Updating the last captured date.

Modify the logging configuration as needed to adjust the log level and format.

This README provides a detailed guide on setting up and running the script, as well as explaining the functionality of each part of the code.
