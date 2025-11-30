import re
import requests
from typing import Optional, Dict
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class ContentSummarizer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; BookmarkBot/1.0)'
        }
        self.timeout = 10

    def extract_content(self, url: str) -> Dict[str, Optional[str]]:
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract description/summary
            description = self._extract_description(soup)
            
            # Extract main content for summarization
            content = self._extract_main_content(soup)
            
            # Generate summary
            summary = self._generate_summary(content, description)
            
            return {
                'title': title,
                'description': description,
                'summary': summary,
                'content_length': len(content) if content else 0
            }
            
        except Exception as e:
            return {
                'title': None,
                'description': None,
                'summary': None,
                'error': str(e)
            }

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        # Try multiple title sources
        title_sources = [
            soup.find('title'),
            soup.find('meta', property='og:title'),
            soup.find('meta', name='twitter:title'),
            soup.find('h1')
        ]
        
        for source in title_sources:
            if source:
                title = source.get('content') if source.get('content') else source.get_text()
                if title:
                    return title.strip()[:200]  # Limit length
        return None

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        # Try multiple description sources
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()[:300]
            
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            return og_desc.get('content', '').strip()[:300]
            
        twitter_desc = soup.find('meta', name='twitter:description')
        if twitter_desc:
            return twitter_desc.get('content', '').strip()[:300]
            
        return None

    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[str]:
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try to find main content areas
        content_selectors = [
            'article',
            'main',
            '[role="main"]',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '#content',
            '.container'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                text = content_elem.get_text(separator=' ', strip=True)
                if len(text) > 200:  # Ensure substantial content
                    return text[:2000]  # Limit content length
        
        # Fallback to body text
        body = soup.find('body')
        if body:
            text = body.get_text(separator=' ', strip=True)
            return text[:2000]
            
        return None

    def _generate_summary(self, content: Optional[str], description: Optional[str]) -> Optional[str]:
        # If we have a good meta description, use it
        if description and len(description) > 50:
            return description
        
        if not content:
            return None
        
        # Clean the content
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Extract first few sentences as summary
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        if not sentences:
            return None
        
        # Build summary from first 2-3 sentences
        summary = ""
        for sentence in sentences[:3]:
            if len(summary + sentence) < 250:
                summary += sentence + ". "
            else:
                break
        
        return summary.strip() if summary else None

    def get_page_info(self, url: str) -> Dict[str, Optional[str]]:
        """Main method to get page title, description, and summary"""
        try:
            # Validate URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return {'error': 'Invalid URL'}
            
            return self.extract_content(url)
            
        except Exception as e:
            return {'error': f'Failed to process URL: {str(e)}'}