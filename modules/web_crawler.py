#!/usr/bin/env python3
"""
Web Crawler Module
HTTP spider for link discovery and site mapping
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, List, Dict
import time

class WebCrawler:
    """
    Basic web crawler for reconnaissance
    """
    
    def __init__(self, base_url: str, max_depth: int = 3, max_pages: int = 50):
        """
        Initialize web crawler
        
        Args:
            base_url: Starting URL
            max_depth: Maximum crawl depth
            max_pages: Maximum pages to crawl
        """
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited = set()
        self.to_visit = [(base_url, 0)]
        self.results = {
            'pages': [],
            'forms': [],
            'external_links': set(),
            'subdomains': set(),
            'emails': set(),
            'robots_txt': None,
            'sitemap': None
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ReconBot/1.0)'
        })
    
    def crawl(self) -> Dict:
        """
        Start crawling
        
        Returns:
            Crawl results
        """
        # Check robots.txt
        self.check_robots_txt()
        
        # Check for sitemap
        self.check_sitemap()
        
        # Crawl pages
        while self.to_visit and len(self.visited) < self.max_pages:
            url, depth = self.to_visit.pop(0)
            
            if url in self.visited or depth > self.max_depth:
                continue
            
            self.crawl_page(url, depth)
            time.sleep(0.5)  # Be polite
        
        # Convert sets to lists for JSON serialization
        self.results['external_links'] = list(self.results['external_links'])
        self.results['subdomains'] = list(self.results['subdomains'])
        self.results['emails'] = list(self.results['emails'])
        
        return self.results
    
    def crawl_page(self, url: str, depth: int):
        """
        Crawl a single page
        
        Args:
            url: URL to crawl
            depth: Current depth
        """
        try:
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code != 200:
                return
            
            self.visited.add(url)
            
            # Store page info
            page_info = {
                'url': url,
                'status': response.status_code,
                'title': None,
                'depth': depth
            }
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get title
            title_tag = soup.find('title')
            if title_tag:
                page_info['title'] = title_tag.get_text().strip()
            
            self.results['pages'].append(page_info)
            
            # Extract links
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                # Parse URL
                parsed = urlparse(full_url)
                
                # Same domain links
                if parsed.netloc == self.domain:
                    if full_url not in self.visited and (full_url, depth + 1) not in self.to_visit:
                        self.to_visit.append((full_url, depth + 1))
                
                # External links
                elif parsed.netloc and parsed.netloc != self.domain:
                    self.results['external_links'].add(full_url)
                    
                    # Check for subdomains of parent domain
                    if self.domain.split('.')[-2:] == parsed.netloc.split('.')[-2:]:
                        self.results['subdomains'].add(parsed.netloc)
            
            # Extract forms
            forms = soup.find_all('form')
            for form in forms:
                form_info = {
                    'url': url,
                    'action': urljoin(url, form.get('action', '')),
                    'method': form.get('method', 'get').upper(),
                    'inputs': []
                }
                
                # Get form inputs
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    form_info['inputs'].append({
                        'name': input_tag.get('name'),
                        'type': input_tag.get('type', 'text'),
                        'value': input_tag.get('value', '')
                    })
                
                self.results['forms'].append(form_info)
            
            # Extract emails
            import re
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
            self.results['emails'].update(emails)
            
        except Exception as e:
            pass
    
    def check_robots_txt(self):
        """
        Check robots.txt file
        """
        robots_url = urljoin(self.base_url, '/robots.txt')
        try:
            response = self.session.get(robots_url, timeout=5)
            if response.status_code == 200:
                self.results['robots_txt'] = response.text
        except:
            pass
    
    def check_sitemap(self):
        """
        Check for sitemap.xml
        """
        sitemap_urls = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap1.xml'
        ]
        
        for sitemap_path in sitemap_urls:
            sitemap_url = urljoin(self.base_url, sitemap_path)
            try:
                response = self.session.get(sitemap_url, timeout=5)
                if response.status_code == 200:
                    self.results['sitemap'] = {
                        'url': sitemap_url,
                        'content': response.text[:1000]  # First 1000 chars
                    }
                    break
            except:
                continue


def crawl_website(url: str, max_depth: int = 3, max_pages: int = 50) -> Dict:
    """
    Crawl a website
    
    Args:
        url: Target URL
        max_depth: Maximum crawl depth
        max_pages: Maximum pages to crawl
        
    Returns:
        Crawl results
    """
    crawler = WebCrawler(url, max_depth, max_pages)
    return crawler.crawl()
