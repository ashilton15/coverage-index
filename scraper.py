"""URL scraping module for Coverage Index."""

from __future__ import annotations

import trafilatura
from trafilatura.settings import use_config
import requests
from urllib.parse import urlparse
import re


# Minimum content requirements
MIN_CONTENT_LENGTH = 500  # characters
MIN_WORD_COUNT = 100  # words

# Paywall/block indicators - if content contains these, likely not the real article
PAYWALL_INDICATORS = [
    "subscribe to continue",
    "subscription required",
    "sign in to read",
    "log in to continue",
    "create an account",
    "premium content",
    "members only",
    "unlock this article",
    "already a subscriber",
    "start your free trial",
    "access denied",
    "please subscribe",
    "to read the full article",
    "continue reading with a subscription",
    "this content is for subscribers",
    "register to continue",
    "sign up to read",
]


def configure_trafilatura():
    """Configure trafilatura for better extraction."""
    config = use_config()
    config.set("DEFAULT", "EXTRACTION_TIMEOUT", "30")
    return config


# Browser-like headers for sites that block default requests
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


def fetch_with_headers(url: str, timeout: int = 15) -> str | None:
    """Fetch URL with browser-like headers as fallback."""
    try:
        response = requests.get(url, headers=BROWSER_HEADERS, timeout=timeout)
        if response.status_code == 200:
            return response.text
        return None
    except Exception:
        return None


def extract_domain(url: str) -> str:
    """Extract domain from URL for outlet matching."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix if present
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def check_content_quality(content: str) -> tuple[bool, str]:
    """
    Check if extracted content is likely the real article.

    Returns:
        (is_valid, error_message)
    """
    if not content:
        return False, "No content extracted"

    content_stripped = content.strip()

    # Check minimum length
    if len(content_stripped) < MIN_CONTENT_LENGTH:
        return False, f"Content too short ({len(content_stripped)} chars) - likely paywalled or blocked"

    # Check word count
    words = content_stripped.split()
    if len(words) < MIN_WORD_COUNT:
        return False, f"Content too short ({len(words)} words) - likely paywalled or blocked"

    # Check for paywall indicators
    content_lower = content_stripped.lower()
    for indicator in PAYWALL_INDICATORS:
        if indicator in content_lower:
            # Only flag if the content is relatively short (long articles might mention subscriptions naturally)
            if len(words) < 300:
                return False, f"Paywall detected - content contains '{indicator}'"

    # Check if content is mostly repetitive (some paywalls repeat the same text)
    unique_words = set(words)
    if len(words) > 50 and len(unique_words) / len(words) < 0.3:
        return False, "Content appears to be repetitive/blocked"

    return True, ""


def scrape_url(url: str) -> dict:
    """
    Scrape article content from URL.

    Returns:
        dict with keys: success, content, title, author, error, word_count
    """
    result = {
        "success": False,
        "content": None,
        "title": None,
        "author": None,
        "error": None,
        "domain": extract_domain(url),
        "word_count": 0,
        "raw_html": None,  # For byline detection
    }

    try:
        # Download the page - try trafilatura first, then fallback to requests with headers
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            # Fallback: use requests with browser-like headers
            downloaded = fetch_with_headers(url)

        if not downloaded:
            result["error"] = "Could not fetch URL - site may be blocking requests"
            return result

        # Extract content
        content = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            no_fallback=False,
        )

        # Quality check the content
        is_valid, error_msg = check_content_quality(content)

        if not is_valid:
            result["error"] = error_msg
            # Store partial content for debugging but mark as failed
            result["partial_content"] = content[:500] if content else None
            return result

        # Extract title/metadata
        metadata = trafilatura.extract_metadata(downloaded)
        if metadata:
            result["title"] = metadata.title
            result["author"] = metadata.author if hasattr(metadata, 'author') else None

        # Store raw HTML for byline detection (first 5000 chars is enough)
        result["raw_html"] = downloaded[:5000] if downloaded else None

        result["success"] = True
        result["content"] = content
        result["word_count"] = len(content.split())
        return result

    except requests.exceptions.Timeout:
        result["error"] = "Request timed out"
        return result
    except requests.exceptions.RequestException as e:
        result["error"] = f"Network error: {str(e)}"
        return result
    except Exception as e:
        result["error"] = f"Scraping error: {str(e)}"
        return result


def scrape_batch(urls: list) -> list:
    """
    Scrape multiple URLs.

    Returns:
        List of dicts with scraping results
    """
    results = []
    for url in urls:
        result = scrape_url(url)
        result["url"] = url
        results.append(result)
    return results
