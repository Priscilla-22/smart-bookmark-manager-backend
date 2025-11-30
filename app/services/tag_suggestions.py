import re
import requests
from typing import List, Set
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TagSuggestionService:
    def __init__(self):
        self.domain_keywords = {
            'github.com': ['development', 'coding', 'programming', 'software'],
            'stackoverflow.com': ['programming', 'development', 'coding', 'help'],
            'youtube.com': ['video', 'entertainment', 'tutorial', 'learning'],
            'medium.com': ['article', 'blog', 'writing', 'learning'],
            'linkedin.com': ['professional', 'networking', 'career', 'business'],
            'twitter.com': ['social', 'news', 'updates'],
            'reddit.com': ['discussion', 'community', 'social'],
            'docs.google.com': ['document', 'productivity', 'work'],
            'figma.com': ['design', 'ui', 'ux', 'creativity'],
            'dribbble.com': ['design', 'inspiration', 'creativity'],
            'coursera.org': ['education', 'learning', 'course'],
            'udemy.com': ['education', 'learning', 'course'],
            'netflix.com': ['entertainment', 'streaming', 'video'],
            'spotify.com': ['music', 'audio', 'entertainment']
        }
        
        self.tech_keywords = {
            'python': ['programming', 'development', 'backend'],
            'javascript': ['programming', 'development', 'frontend'],
            'react': ['frontend', 'development', 'programming'],
            'vue': ['frontend', 'development', 'programming'],
            'angular': ['frontend', 'development', 'programming'],
            'node': ['backend', 'development', 'programming'],
            'docker': ['devops', 'deployment', 'containers'],
            'kubernetes': ['devops', 'deployment', 'containers'],
            'aws': ['cloud', 'devops', 'infrastructure'],
            'azure': ['cloud', 'devops', 'infrastructure'],
            'api': ['development', 'programming', 'backend'],
            'database': ['development', 'backend', 'data'],
            'machine learning': ['ai', 'data science', 'programming'],
            'ai': ['artificial intelligence', 'technology', 'programming']
        }

    def extract_content(self, url: str, title: str = None, description: str = None) -> str:
        content_parts = []
        
        if title:
            content_parts.append(title)
        if description:
            content_parts.append(description)
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            path = parsed_url.path.lower()
            
            content_parts.extend([domain, path])
            
            if domain in self.domain_keywords:
                content_parts.extend(self.domain_keywords[domain])
            
            try:
                response = requests.get(url, timeout=5, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; BookmarkBot/1.0)'
                })
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    page_title = soup.find('title')
                    if page_title and not title:
                        content_parts.append(page_title.get_text().strip())
                    
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    if meta_desc and not description:
                        content_parts.append(meta_desc.get('content', ''))
                    
                    keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
                    if keywords_meta:
                        content_parts.append(keywords_meta.get('content', ''))
                        
            except Exception:
                pass
                
        except Exception:
            pass
        
        return ' '.join(content_parts).lower()

    def generate_keyword_tags(self, content: str) -> Set[str]:
        tags = set()
        content_lower = content.lower()
        
        for tech, related_tags in self.tech_keywords.items():
            if tech in content_lower:
                tags.update(related_tags)
                tags.add(tech)
        
        if any(word in content_lower for word in ['tutorial', 'guide', 'how to', 'learn']):
            tags.add('tutorial')
        
        if any(word in content_lower for word in ['news', 'article', 'blog']):
            tags.add('reading')
        
        if any(word in content_lower for word in ['video', 'watch', 'stream']):
            tags.add('video')
        
        if any(word in content_lower for word in ['tool', 'software', 'app']):
            tags.add('tools')
        
        if any(word in content_lower for word in ['work', 'productivity', 'business']):
            tags.add('work')
        
        return tags

    def suggest_tags(self, url: str, title: str = None, description: str = None, 
                    existing_tags: List[str] = None, max_suggestions: int = 5) -> List[str]:
        existing_tags = existing_tags or []
        existing_tag_names = {tag.lower() for tag in existing_tags}
        
        content = self.extract_content(url, title, description)
        suggested_tags = self.generate_keyword_tags(content)
        
        filtered_suggestions = [
            tag for tag in suggested_tags 
            if tag.lower() not in existing_tag_names
        ]
        
        return list(filtered_suggestions)[:max_suggestions]