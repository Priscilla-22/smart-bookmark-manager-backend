import re
import requests
from typing import Optional, Dict, List
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class MLSummarizer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; BookmarkBot/1.0)'
        }
        self.timeout = 10
        self.max_summary_length = 200


    def extract_content(self, url: str) -> Dict[str, Optional[str]]:
        """Extract and clean content from webpage"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract description from meta tags
            description = None
            meta_desc = soup.find('meta', {'name': 'description'})
            if not meta_desc:
                meta_desc = soup.find('meta', property='og:description')
            if meta_desc:
                description = meta_desc.get('content', '').strip()[:300]
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Clean and prepare content for summarization
            clean_content = self._clean_content(content)
            
            return {
                'title': title,
                'description': description,
                'content': clean_content,
                'content_length': len(clean_content) if clean_content else 0
            }
            
        except Exception as e:
            return {
                'title': None,
                'description': None,
                'content': None,
                'error': str(e)
            }

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title"""
        title_sources = [
            soup.find('title'),
            soup.find('meta', property='og:title'),
            soup.find('meta', {'name': 'twitter:title'}),
            soup.find('h1')
        ]
        
        for source in title_sources:
            if source:
                title = source.get('content') if source.get('content') else source.get_text()
                if title:
                    return title.strip()[:200]
        return None

    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract main content for summarization"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'button', 'advertisement']):
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
            '.article-body',
            '#content',
            'div.content',
            'div#main-content'
        ]
        
        main_content = None
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                text = content_elem.get_text(separator=' ', strip=True)
                if len(text) > 200:  # Ensure substantial content
                    main_content = text
                    break
        
        # If no main content found, try paragraphs
        if not main_content:
            paragraphs = soup.find_all('p')
            if paragraphs:
                para_texts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]
                if para_texts:
                    main_content = ' '.join(para_texts[:5])  # Take first 5 paragraphs
        
        # Fallback to body text
        if not main_content:
            body = soup.find('body')
            if body:
                main_content = body.get_text(separator=' ', strip=True)
                
        return main_content

    def _clean_content(self, content: Optional[str]) -> Optional[str]:
        """Clean and prepare content for summarization"""
        if not content:
            return None
        
        # Remove extra whitespace and normalize
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Simple sentence splitting without NLTK
        sentences = re.split(r'[.!?]+', content)
        meaningful_sentences = [s.strip() for s in sentences if len(s.split()) > 5]
        
        # Rejoin meaningful sentences
        clean_content = '. '.join(meaningful_sentences)
        if clean_content and not clean_content.endswith('.'):
            clean_content += '.'
        
        return clean_content if len(clean_content) > 50 else None

    def generate_ml_summary(self, content: str) -> Optional[str]:
        """Generate intelligent summary using text processing"""
        if not content:
            return None
        
        return self._smart_extractive_summary(content)

    def _smart_extractive_summary(self, content: str) -> Optional[str]:
        """Create intelligent extractive summary that tells users what they'll find"""
        if not content:
            return None
        
        # Clean and prepare content
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.split()) > 3]
        
        if not sentences:
            return None
        
        # Score sentences based on what would be useful to know before visiting
        sentence_scores = []
        for i, sentence in enumerate(sentences[:15]):  # Consider more sentences
            score = 0
            sentence_lower = sentence.lower()
            
            # Position score (earlier sentences usually contain main topic)
            position_score = (15 - i) / 15
            score += position_score * 0.2
            
            # Length score (prefer informative but not too long sentences)
            word_count = len(sentence.split())
            if 8 <= word_count <= 30:
                score += 0.3
            elif word_count < 8:
                score += 0.1
            
            # Content type indicators (what kind of content is this?)
            content_indicators = [
                'tutorial', 'guide', 'how to', 'learn', 'course', 'lesson', 'steps',
                'article', 'blog', 'post', 'news', 'story', 'report',
                'product', 'service', 'company', 'about', 'tool', 'app',
                'documentation', 'docs', 'manual', 'help', 'faq',
                'review', 'comparison', 'analysis', 'research'
            ]
            for indicator in content_indicators:
                if indicator in sentence_lower:
                    score += 0.3
            
            # Purpose/action indicators (what can users do here?)
            action_words = [
                'download', 'buy', 'purchase', 'get', 'access', 'use', 'try',
                'learn', 'discover', 'find', 'explore', 'create', 'build',
                'offers', 'provides', 'features', 'includes', 'contains'
            ]
            for action in action_words:
                if action in sentence_lower:
                    score += 0.25
            
            # Topic/subject indicators
            topic_words = [
                'technology', 'software', 'programming', 'development', 'business',
                'education', 'science', 'health', 'finance', 'marketing',
                'design', 'entertainment', 'news', 'sports', 'travel'
            ]
            for topic in topic_words:
                if topic in sentence_lower:
                    score += 0.15
            
            # Avoid promotional/generic sentences
            avoid_words = ['cookie', 'privacy', 'terms', 'subscribe', 'newsletter', 'email']
            for avoid in avoid_words:
                if avoid in sentence_lower:
                    score -= 0.2
            
            sentence_scores.append((score, sentence))
        
        # Sort by score and select best sentences
        sentence_scores.sort(reverse=True, key=lambda x: x[0])
        
        # Create summary that answers "What will I find on this page?"
        summary_parts = []
        total_length = 0
        max_sentences = 2
        
        for score, sentence in sentence_scores[:max_sentences * 2]:  # Look at top candidates
            if score > 0 and total_length + len(sentence) <= self.max_summary_length:
                summary_parts.append(sentence)
                total_length += len(sentence)
                if len(summary_parts) >= max_sentences:
                    break
        
        if summary_parts:
            summary = '. '.join(summary_parts)
            if not summary.endswith(('.', '!', '?')):
                summary += '.'
            return summary
        
        # Enhanced fallback - try to find the most descriptive sentence
        for sentence in sentences[:5]:
            sentence_lower = sentence.lower()
            if any(word in sentence_lower for word in ['about', 'provides', 'offers', 'features', 'helps', 'allows']):
                return sentence + '.' if not sentence.endswith('.') else sentence
        
        # Final fallback to first substantial sentence
        for sentence in sentences[:3]:
            if len(sentence.split()) >= 5:
                return sentence + '.' if not sentence.endswith('.') else sentence
                
        return None

    def get_ml_summary(self, url: str) -> Dict[str, Optional[str]]:
        """Main method to get AI-powered summary that tells users what they'll find"""
        try:
            # Extract content
            extraction_result = self.extract_content(url)
            
            if 'error' in extraction_result:
                return extraction_result
            
            content = extraction_result.get('content')
            title = extraction_result.get('title')
            description = extraction_result.get('description')
            
            # Generate smart summary that tells users what to expect
            smart_summary = self.generate_ml_summary(content) if content else None
            
            # Use description as fallback if no smart summary generated
            final_summary = smart_summary or description
            
            return {
                'title': title,
                'description': description,
                'content_length': extraction_result.get('content_length', 0),
                'ml_summary': final_summary,
                'summary_method': 'smart' if smart_summary else ('meta' if description else 'none')
            }
            
        except Exception as e:
            return {'error': f'Failed to generate smart summary: {str(e)}'}