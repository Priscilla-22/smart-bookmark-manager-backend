import re
import requests
from typing import Optional, Dict
from bs4 import BeautifulSoup

class SmartSummarizer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; BookmarkBot/1.0)'
        }
        self.timeout = 10
        self.max_summary_length = 200

    def get_smart_summary(self, url: str) -> Dict[str, Optional[str]]:
        """Get smart summary that tells users what they'll find on the page"""
        try:
            # Fetch the webpage
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic info
            title = self._get_title(soup)
            description = self._get_description(soup)
            content = self._get_main_content(soup)
            
            # Generate smart summary
            summary = self._create_summary(title, description, content)
            
            return {
                'title': title,
                'description': description,
                'content_length': len(content) if content else 0,
                'ml_summary': summary,
                'summary_method': 'smart' if summary else 'basic'
            }
            
        except Exception as e:
            return {'error': f'Failed to analyze URL: {str(e)}'}
    
    def _get_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title"""
        # Try different title sources
        title_elem = soup.find('title')
        if title_elem:
            return title_elem.get_text().strip()[:200]
        
        # Try meta og:title
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title:
            return og_title.get('content', '').strip()[:200]
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()[:200]
            
        return None
    
    def _get_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page description"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()[:300]
        
        # Try og:description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc:
            return og_desc.get('content', '').strip()[:300]
            
        return None
    
    def _get_main_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract main page content"""
        # Remove unwanted elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer']):
            script.decompose()
        
        # Try to find main content
        selectors = ['article', 'main', '.content', '#content']
        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                text = content.get_text(separator=' ', strip=True)
                if len(text) > 100:
                    return text[:2000]  # Limit length
        
        # Fallback to paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            text = ' '.join([p.get_text(strip=True) for p in paragraphs[:5]])
            if text:
                return text[:2000]
        
        return None
    
    def _create_summary(self, title: str, description: str, content: str) -> Optional[str]:
        """Create intelligent summary from extracted content"""
        # Use description if available as it's usually well-crafted
        if description and len(description) > 20:
            return description
        
        # If no description, analyze content to create summary
        if content:
            return self._analyze_content_for_summary(content, title)
        
        # Fallback to title if nothing else
        if title:
            return f"Page titled: {title}"
            
        return None
    
    def _analyze_content_for_summary(self, content: str, title: str) -> Optional[str]:
        """Analyze content to create informative summary"""
        if not content:
            return None
        
        # Clean and split into sentences
        content = re.sub(r'\s+', ' ', content).strip()
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if not sentences:
            return None
        
        # Score sentences for usefulness
        scored_sentences = []
        for i, sentence in enumerate(sentences[:10]):  # Only check first 10
            score = self._score_sentence(sentence, i, title)
            if score > 0:
                scored_sentences.append((score, sentence))
        
        # Sort by score and select best sentences
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        
        # Build summary
        summary_parts = []
        total_length = 0
        
        for score, sentence in scored_sentences[:3]:  # Take top 3
            if total_length + len(sentence) <= self.max_summary_length:
                summary_parts.append(sentence)
                total_length += len(sentence)
            else:
                break
        
        if summary_parts:
            return '. '.join(summary_parts) + '.'
        
        # Fallback to first good sentence
        for sentence in sentences[:3]:
            if len(sentence.split()) >= 5:
                return sentence + '.'
                
        return None
    
    def _score_sentence(self, sentence: str, position: int, title: str) -> float:
        """Score sentence for summary usefulness"""
        score = 0.0
        sentence_lower = sentence.lower()
        
        # Position bonus (earlier sentences often more important)
        score += (10 - position) * 0.1
        
        # Length bonus (prefer moderate length)
        word_count = len(sentence.split())
        if 8 <= word_count <= 25:
            score += 1.0
        elif word_count < 8:
            score += 0.3
        
        # Content type indicators
        useful_words = [
            'provides', 'offers', 'features', 'includes', 'allows', 'helps',
            'tutorial', 'guide', 'learn', 'how to', 'step',
            'article', 'blog', 'news', 'information',
            'tool', 'service', 'platform', 'app', 'software',
            'company', 'organization', 'business'
        ]
        
        for word in useful_words:
            if word in sentence_lower:
                score += 0.5
        
        # Title relevance
        if title:
            title_words = title.lower().split()
            for word in title_words:
                if len(word) > 3 and word in sentence_lower:
                    score += 0.3
        
        # Avoid promotional/generic content
        avoid_words = ['cookie', 'privacy', 'terms', 'subscribe', 'newsletter']
        for word in avoid_words:
            if word in sentence_lower:
                score -= 0.5
        
        return max(0.0, score)