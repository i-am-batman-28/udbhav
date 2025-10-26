"""
Web Scraper Module with Advanced Features

This module provides a comprehensive web scraping solution with support for
multiple protocols, error handling, rate limiting, and data extraction.

Author: AI Assistant
Date: 2025-10-26
License: MIT
"""

import requests
import time
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
from dataclasses import dataclass
from datetime import datetime


# Configure logging for the module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScrapedData:
    """
    Data class to store scraped information.
    
    This class provides a structured way to store and access scraped data
    from web pages, including metadata about the scraping operation.
    
    Attributes:
        url (str): The URL that was scraped.
        title (str): The title of the web page.
        content (str): The main content extracted from the page.
        links (List[str]): A list of all links found on the page.
        timestamp (datetime): When the data was scraped.
        status_code (int): The HTTP status code of the response.
    """
    url: str
    title: str
    content: str
    links: List[str]
    timestamp: datetime
    status_code: int


class WebScraper:
    """
    A comprehensive web scraper class with advanced features.
    
    This class provides methods for scraping web pages, extracting data,
    handling errors, and managing rate limiting to avoid overwhelming servers.
    
    Attributes:
        session (requests.Session): The HTTP session for making requests.
        headers (Dict[str, str]): HTTP headers to use for requests.
        timeout (int): Request timeout in seconds.
        rate_limit (float): Minimum time between requests in seconds.
        last_request_time (float): Timestamp of the last request.
    """
    
    def __init__(
        self,
        timeout: int = 30,
        rate_limit: float = 1.0,
        user_agent: Optional[str] = None
    ):
        """
        Initialize the WebScraper with configuration parameters.
        
        Args:
            timeout (int): Request timeout in seconds. Defaults to 30.
            rate_limit (float): Minimum seconds between requests. Defaults to 1.0.
            user_agent (Optional[str]): Custom user agent string. If None, uses default.
            
        Raises:
            ValueError: If timeout or rate_limit are negative values.
        """
        # Validate input parameters
        if timeout < 0:
            raise ValueError("Timeout must be a non-negative integer")
        if rate_limit < 0:
            raise ValueError("Rate limit must be a non-negative number")
        
        # Initialize the HTTP session
        self.session = requests.Session()
        
        # Set up default headers
        self.headers = {
            'User-Agent': user_agent or 'Mozilla/5.0 (compatible; WebScraper/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Set configuration parameters
        self.timeout = timeout
        self.rate_limit = rate_limit
        self.last_request_time = 0.0
        
        # Log initialization
        logger.info(f"WebScraper initialized with timeout={timeout}s, rate_limit={rate_limit}s")
    
    def _enforce_rate_limit(self) -> None:
        """
        Enforce rate limiting between requests.
        
        This internal method ensures that requests are spaced out according
        to the configured rate limit to avoid overwhelming target servers.
        """
        # Calculate time since last request
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # If not enough time has passed, sleep for the remaining duration
        if time_since_last_request < self.rate_limit:
            sleep_duration = self.rate_limit - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_duration:.2f} seconds")
            time.sleep(sleep_duration)
        
        # Update the last request time
        self.last_request_time = time.time()
    
    def fetch_page(self, url: str) -> Optional[requests.Response]:
        """
        Fetch a web page and return the response.
        
        This method handles the HTTP request with proper error handling,
        rate limiting, and logging.
        
        Args:
            url (str): The URL of the page to fetch.
            
        Returns:
            Optional[requests.Response]: The response object if successful, None otherwise.
            
        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        # Validate the URL format
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            logger.error(f"Invalid URL format: {url}")
            return None
        
        # Enforce rate limiting
        self._enforce_rate_limit()
        
        try:
            # Log the request
            logger.info(f"Fetching URL: {url}")
            
            # Make the HTTP request
            response = self.session.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Log success
            logger.info(f"Successfully fetched {url} (Status: {response.status_code})")
            
            # Return the response
            return response
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for URL: {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for URL: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for URL {url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception for URL {url}: {e}")
            return None
    
    def extract_text(self, html: str) -> str:
        """
        Extract readable text from HTML content.
        
        This method parses HTML and extracts the main text content,
        removing scripts, styles, and other non-content elements.
        
        Args:
            html (str): The HTML content to parse.
            
        Returns:
            str: The extracted text content.
        """
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(['script', 'style', 'meta', 'link']):
            script_or_style.decompose()
        
        # Get the text content
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines()]
        text = ' '.join(line for line in lines if line)
        
        # Return the cleaned text
        return text
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """
        Extract all links from HTML content.
        
        This method finds all anchor tags in the HTML and extracts their
        href attributes, converting relative URLs to absolute URLs.
        
        Args:
            html (str): The HTML content to parse.
            base_url (str): The base URL for resolving relative links.
            
        Returns:
            List[str]: A list of absolute URLs found in the HTML.
        """
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Initialize the links list
        links = []
        
        # Find all anchor tags
        for anchor in soup.find_all('a', href=True):
            # Get the href attribute
            href = anchor['href']
            
            # Convert relative URLs to absolute URLs
            absolute_url = urljoin(base_url, href)
            
            # Validate that it's a proper HTTP/HTTPS URL
            parsed = urlparse(absolute_url)
            if parsed.scheme in ['http', 'https']:
                links.append(absolute_url)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        # Log the number of links found
        logger.info(f"Found {len(unique_links)} unique links")
        
        # Return the list of unique links
        return unique_links
    
    def scrape(self, url: str) -> Optional[ScrapedData]:
        """
        Scrape a web page and extract structured data.
        
        This is the main method that combines fetching, parsing, and
        data extraction into a single operation.
        
        Args:
            url (str): The URL of the page to scrape.
            
        Returns:
            Optional[ScrapedData]: A ScrapedData object if successful, None otherwise.
        """
        # Fetch the page
        response = self.fetch_page(url)
        
        # Check if the fetch was successful
        if response is None:
            logger.error(f"Failed to scrape {url}")
            return None
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the title
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        
        # Extract the main content
        content = self.extract_text(response.text)
        
        # Extract all links
        links = self.extract_links(response.text, url)
        
        # Create and return the ScrapedData object
        scraped_data = ScrapedData(
            url=url,
            title=title,
            content=content[:1000],  # Limit content length
            links=links,
            timestamp=datetime.now(),
            status_code=response.status_code
        )
        
        # Log successful scraping
        logger.info(f"Successfully scraped {url}")
        
        # Return the scraped data
        return scraped_data
    
    def close(self) -> None:
        """
        Close the HTTP session and clean up resources.
        
        This method should be called when done with the scraper to
        properly release resources.
        """
        # Close the session
        self.session.close()
        
        # Log closure
        logger.info("WebScraper session closed")
