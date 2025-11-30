"""
Bookmark recommendation service using content similarity
"""

import re
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter
import math

from app.models import Bookmark, Tag
from .smart_summarizer import SmartSummarizer


class BookmarkRecommender:
    def __init__(self):
        self.smart_summarizer = SmartSummarizer()
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'you', 'your', 'this', 'that', 'but',
            'or', 'if', 'can', 'could', 'should', 'would', 'may', 'might'
        }

    def get_similar_bookmarks(
        self, 
        db: Session, 
        url: str, 
        title: str = None, 
        description: str = None,
        user_id: int = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Find similar bookmarks based on content analysis
        """
        try:
            # Analyze the input content
            input_content = self._prepare_content_for_analysis(url, title, description)
            
            # Get all bookmarks (optionally filtered by user)
            query = db.query(Bookmark)
            if user_id:
                query = query.filter(Bookmark.user_id == user_id)
            
            existing_bookmarks = query.all()
            
            if not existing_bookmarks:
                return []
            
            # Calculate similarity scores
            similarities = []
            for bookmark in existing_bookmarks:
                # Skip if it's the same URL
                if bookmark.url.lower() == url.lower():
                    continue
                    
                bookmark_content = self._prepare_bookmark_content(bookmark)
                similarity_score = self._calculate_similarity(input_content, bookmark_content)
                
                if similarity_score > 0.1:  # Only include if there's meaningful similarity
                    similarities.append({
                        'bookmark': bookmark,
                        'score': similarity_score,
                        'reasons': self._get_similarity_reasons(input_content, bookmark_content)
                    })
            
            # Sort by similarity score
            similarities.sort(key=lambda x: x['score'], reverse=True)
            
            # Format results
            results = []
            for sim in similarities[:limit]:
                bookmark = sim['bookmark']
                results.append({
                    'id': bookmark.id,
                    'title': bookmark.title,
                    'url': bookmark.url,
                    'description': bookmark.description,
                    'summary': bookmark.summary,
                    'similarity_score': round(sim['score'], 3),
                    'similarity_reasons': sim['reasons'],
                    'tags': [{'name': tag.name, 'color': tag.color} for tag in bookmark.tags] if bookmark.tags else [],
                    'created_at': bookmark.created_at.isoformat() if bookmark.created_at else None
                })
            
            return results
            
        except Exception as e:
            print(f"Error in bookmark recommendation: {e}")
            return []

    def _prepare_content_for_analysis(self, url: str, title: str = None, description: str = None) -> Dict[str, str]:
        """
        Prepare input content for similarity analysis
        """
        content = {
            'url': url or '',
            'title': title or '',
            'description': description or '',
            'summary': ''
        }
        
        # If no title/description provided, try to extract from URL
        if not title and not description:
            try:
                result = self.smart_summarizer.get_smart_summary(url)
                if 'error' not in result:
                    content['title'] = result.get('title', '') or ''
                    content['description'] = result.get('description', '') or ''
                    content['summary'] = result.get('ml_summary', '') or ''
            except Exception:
                pass
        
        return content

    def _prepare_bookmark_content(self, bookmark: Bookmark) -> Dict[str, str]:
        """
        Prepare existing bookmark content for comparison
        """
        return {
            'url': bookmark.url or '',
            'title': bookmark.title or '',
            'description': bookmark.description or '',
            'summary': bookmark.summary or '',
            'tags': ' '.join([tag.name for tag in bookmark.tags]) if bookmark.tags else ''
        }

    def _calculate_similarity(self, content1: Dict[str, str], content2: Dict[str, str]) -> float:
        """
        Calculate similarity score between two content pieces
        """
        # Combine all text for each content
        text1 = ' '.join([
            content1.get('title', ''),
            content1.get('description', ''),
            content1.get('summary', ''),
            self._extract_domain_keywords(content1.get('url', ''))
        ]).lower()
        
        text2 = ' '.join([
            content2.get('title', ''),
            content2.get('description', ''),
            content2.get('summary', ''),
            content2.get('tags', ''),
            self._extract_domain_keywords(content2.get('url', ''))
        ]).lower()
        
        # Extract keywords
        keywords1 = self._extract_keywords(text1)
        keywords2 = self._extract_keywords(text2)
        
        if not keywords1 or not keywords2:
            return 0.0
        
        # Calculate Jaccard similarity for keywords
        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))
        
        if union == 0:
            return 0.0
        
        jaccard_score = intersection / union
        
        # Calculate domain similarity bonus
        domain1 = self._extract_domain(content1.get('url', ''))
        domain2 = self._extract_domain(content2.get('url', ''))
        domain_bonus = 0.2 if domain1 and domain2 and domain1 == domain2 else 0.0
        
        # Calculate title similarity bonus
        title_bonus = self._calculate_title_similarity(
            content1.get('title', ''), 
            content2.get('title', '')
        ) * 0.3
        
        return min(1.0, jaccard_score + domain_bonus + title_bonus)

    def _extract_keywords(self, text: str) -> set:
        """
        Extract meaningful keywords from text
        """
        if not text:
            return set()
        
        # Clean and tokenize
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove stop words and filter
        keywords = {
            word for word in words 
            if word not in self.stop_words and len(word) >= 3
        }
        
        return keywords

    def _extract_domain_keywords(self, url: str) -> str:
        """
        Extract domain-specific keywords from URL
        """
        domain_mapping = {
            'github.com': 'programming development code',
            'stackoverflow.com': 'programming development help',
            'youtube.com': 'video tutorial entertainment',
            'medium.com': 'article blog reading',
            'linkedin.com': 'professional networking',
            'twitter.com': 'social news',
            'reddit.com': 'discussion community',
            'dev.to': 'programming development',
            'docs.google.com': 'document productivity',
            'figma.com': 'design ui ux'
        }
        
        try:
            domain = self._extract_domain(url)
            return domain_mapping.get(domain, '')
        except:
            return ''

    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL
        """
        try:
            from urllib.parse import urlparse
            return urlparse(url.lower()).netloc.replace('www.', '')
        except:
            return ''

    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """
        Calculate similarity between titles
        """
        if not title1 or not title2:
            return 0.0
        
        words1 = set(self._extract_keywords(title1))
        words2 = set(self._extract_keywords(title2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

    def _get_similarity_reasons(self, content1: Dict[str, str], content2: Dict[str, str]) -> List[str]:
        """
        Get human-readable reasons for similarity
        """
        reasons = []
        
        # Check domain similarity
        domain1 = self._extract_domain(content1.get('url', ''))
        domain2 = self._extract_domain(content2.get('url', ''))
        if domain1 and domain2 and domain1 == domain2:
            reasons.append(f"Same domain ({domain1})")
        
        # Check keyword overlap
        keywords1 = self._extract_keywords(' '.join(content1.values()))
        keywords2 = self._extract_keywords(' '.join(content2.values()))
        common_keywords = keywords1.intersection(keywords2)
        
        if common_keywords:
            top_common = list(common_keywords)[:3]
            reasons.append(f"Common keywords: {', '.join(top_common)}")
        
        # Check title similarity
        if content1.get('title') and content2.get('title'):
            title_sim = self._calculate_title_similarity(content1['title'], content2['title'])
            if title_sim > 0.3:
                reasons.append("Similar titles")
        
        return reasons[:3]  # Limit to top 3 reasons