import re
from typing import List, Set, Optional, Dict
from urllib.parse import urlparse
from .smart_summarizer import SmartSummarizer

class SmartTagService:
    def __init__(self):
        self.domain_patterns = {
            'github.com': ['development', 'coding', 'programming', 'opensource'],
            'stackoverflow.com': ['programming', 'development', 'coding', 'help'],
            'youtube.com': ['video', 'entertainment', 'tutorial'],
            'medium.com': ['article', 'blog', 'reading'],
            'dev.to': ['programming', 'development', 'article'],
            'linkedin.com': ['professional', 'networking', 'career'],
            'twitter.com': ['social', 'news'],
            'reddit.com': ['discussion', 'community', 'social'],
            'docs.google.com': ['document', 'productivity', 'work'],
            'figma.com': ['design', 'ui', 'ux'],
            'dribbble.com': ['design', 'inspiration'],
            'behance.net': ['design', 'portfolio', 'creative'],
            'coursera.org': ['education', 'learning', 'course'],
            'udemy.com': ['education', 'learning', 'course'],
            'edx.org': ['education', 'learning', 'course'],
            'netflix.com': ['entertainment', 'streaming', 'video'],
            'spotify.com': ['music', 'audio', 'entertainment'],
            'amazon.com': ['shopping', 'ecommerce'],
            'news.ycombinator.com': ['tech', 'startup', 'programming'],
            'techcrunch.com': ['tech', 'startup', 'news'],
            'wired.com': ['tech', 'science', 'news'],
            'nytimes.com': ['news', 'journalism'],
            'bbc.com': ['news', 'journalism'],
            'cnn.com': ['news', 'journalism']
        }
        
        self.content_keywords = {
            'tutorial': ['tutorial', 'guide', 'how to', 'learn', 'beginner', 'step by step'],
            'documentation': ['docs', 'documentation', 'api', 'reference', 'manual'],
            'article': ['article', 'blog', 'post', 'read', 'story'],
            'video': ['video', 'watch', 'stream', 'movie', 'film'],
            'tool': ['tool', 'app', 'software', 'utility', 'platform'],
            'resource': ['resource', 'list', 'awesome', 'collection', 'curated'],
            'news': ['news', 'today', 'breaking', 'latest', 'update'],
            'research': ['research', 'paper', 'study', 'analysis', 'report'],
            'free': ['free', 'open source', 'gratis', 'no cost'],
            'course': ['course', 'class', 'training', 'certification', 'bootcamp']
        }

        self.tech_patterns = {
            'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'angular'],
            'python': ['python', 'django', 'flask', 'fastapi', 'pandas'],
            'programming': ['code', 'coding', 'programming', 'developer', 'development'],
            'webdev': ['html', 'css', 'frontend', 'backend', 'fullstack', 'web development'],
            'mobile': ['ios', 'android', 'mobile', 'app development', 'swift', 'kotlin'],
            'data': ['data', 'analytics', 'visualization', 'database', 'sql'],
            'ai': ['ai', 'machine learning', 'ml', 'deep learning', 'neural network'],
            'devops': ['docker', 'kubernetes', 'ci/cd', 'deployment', 'aws', 'azure'],
            'security': ['security', 'cybersecurity', 'encryption', 'vulnerability'],
            'design': ['ui', 'ux', 'design', 'figma', 'adobe', 'sketch']
        }

    def extract_domain_suggestions(self, url: str) -> Set[str]:
        try:
            domain = urlparse(url).netloc.lower()
            for pattern, tags in self.domain_patterns.items():
                if pattern in domain:
                    return set(tags)
        except:
            pass
        return set()

    def extract_content_suggestions(self, text: str) -> Set[str]:
        if not text:
            return set()
            
        text_lower = text.lower()
        suggestions = set()
        
        for tag, keywords in self.content_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                suggestions.add(tag)
        
        for tag, keywords in self.tech_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                suggestions.add(tag)
                
        return suggestions

    def extract_url_path_suggestions(self, url: str) -> Set[str]:
        try:
            path = urlparse(url).path.lower()
            suggestions = set()
            
            if '/blog' in path or '/article' in path:
                suggestions.add('article')
            if '/tutorial' in path or '/guide' in path:
                suggestions.add('tutorial')
            if '/doc' in path or '/api' in path:
                suggestions.add('documentation')
            if '/video' in path or '/watch' in path:
                suggestions.add('video')
            if '/tool' in path or '/app' in path:
                suggestions.add('tool')
                
            return suggestions
        except:
            return set()

    def suggest_tags(self, url: str, title: str = None, description: str = None, existing_tags: List[str] = None, use_content_analysis: bool = True) -> List[str]:
        existing_tags = existing_tags or []
        existing_tag_names = {tag.lower() for tag in existing_tags}
        
        # Always fetch fresh content for better suggestions
        analyzed_content = self._get_analyzed_content(url, title, description)
        
        # Extract suggestions from different sources with scoring
        suggestions_with_scores = {}
        
        # Domain suggestions (lower weight)
        domain_suggestions = self.extract_domain_suggestions(url)
        for tag in domain_suggestions:
            suggestions_with_scores[tag] = suggestions_with_scores.get(tag, 0) + 1
        
        # URL path suggestions (medium weight)
        path_suggestions = self.extract_url_path_suggestions(url)
        for tag in path_suggestions:
            suggestions_with_scores[tag] = suggestions_with_scores.get(tag, 0) + 2
            
        # Content-based suggestions (highest weight)
        content_suggestions = self._extract_intelligent_content_tags(analyzed_content)
        for tag in content_suggestions:
            suggestions_with_scores[tag] = suggestions_with_scores.get(tag, 0) + 3
            
        # Technology and tool specific suggestions
        tech_suggestions = self._extract_technology_tags(analyzed_content)
        for tag in tech_suggestions:
            suggestions_with_scores[tag] = suggestions_with_scores.get(tag, 0) + 4
            
        # Topic and subject specific suggestions
        topic_suggestions = self._extract_topic_tags(analyzed_content)
        for tag in topic_suggestions:
            suggestions_with_scores[tag] = suggestions_with_scores.get(tag, 0) + 3
        
        # Sort by relevance score and filter
        sorted_suggestions = sorted(
            suggestions_with_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Filter out existing tags and return top suggestions
        filtered_suggestions = [
            tag for tag, score in sorted_suggestions 
            if tag.lower() not in existing_tag_names and score >= 3  # Increased threshold for better quality
        ]
        
        # If we have too few high-quality suggestions, lower the threshold slightly
        if len(filtered_suggestions) < 3:
            filtered_suggestions = [
                tag for tag, score in sorted_suggestions 
                if tag.lower() not in existing_tag_names and score >= 2
            ]
        
        return filtered_suggestions[:8]  # Top 8 most relevant suggestions

    def _get_analyzed_content(self, url: str, title: str = None, description: str = None) -> Dict[str, str]:
        """Get comprehensive content analysis"""
        content = {
            'url': url,
            'title': title or '',
            'description': description or '',
            'summary': '',
            'full_content': ''
        }
        
        # Always try to fetch fresh content for better analysis
        try:
            summarizer = SmartSummarizer()
            result = summarizer.get_smart_summary(url)
            if 'error' not in result:
                # Use fetched content or fall back to provided content
                fetched_title = result.get('title', '') or ''
                fetched_description = result.get('description', '') or ''
                fetched_summary = result.get('ml_summary', '') or ''
                
                # Combine user-provided and fetched content for best analysis
                content['title'] = title or fetched_title
                content['description'] = description or fetched_description
                content['summary'] = fetched_summary
                
                # If user provided content, enhance it with fetched content
                if title and fetched_summary:
                    content['enhanced_context'] = fetched_summary
                if description and fetched_title:
                    content['enhanced_context'] = content.get('enhanced_context', '') + ' ' + fetched_title
            else:
                print(f"Content analysis error: {result.get('error')}")
        except Exception as e:
            print(f"Error in content analysis: {e}")
        
        # Combine all text for analysis with better weighting
        content_pieces = []
        
        # Title gets highest weight (mentioned twice)
        if content['title']:
            content_pieces.extend([content['title']] * 2)
        
        # Description gets medium weight
        if content['description']:
            content_pieces.append(content['description'])
            
        # Summary provides additional context
        if content['summary']:
            content_pieces.append(content['summary'])
            
        # Enhanced context from fetched content
        if content.get('enhanced_context'):
            content_pieces.append(content['enhanced_context'])
            
        # URL provides domain context
        content_pieces.append(url)
        
        content['full_content'] = ' '.join(filter(None, content_pieces))
        
        return content

    def _extract_advanced_content_suggestions(self, content: str) -> Set[str]:
        """Extract more sophisticated tag suggestions based on content analysis"""
        if not content:
            return set()
            
        content_lower = content.lower()
        suggestions = set()
        
        # Industry/Domain specific patterns
        industry_patterns = {
            'finance': ['finance', 'money', 'investment', 'banking', 'crypto', 'trading', 'stocks'],
            'healthcare': ['health', 'medical', 'doctor', 'patient', 'medicine', 'therapy'],
            'education': ['education', 'school', 'university', 'student', 'teacher', 'learning'],
            'marketing': ['marketing', 'advertising', 'brand', 'campaign', 'social media'],
            'business': ['business', 'startup', 'entrepreneur', 'company', 'enterprise'],
            'science': ['science', 'research', 'experiment', 'discovery', 'laboratory'],
            'travel': ['travel', 'vacation', 'trip', 'tourism', 'hotel', 'flight'],
            'food': ['food', 'recipe', 'cooking', 'restaurant', 'cuisine', 'meal'],
            'sports': ['sports', 'game', 'team', 'player', 'match', 'championship'],
            'entertainment': ['movie', 'music', 'game', 'celebrity', 'show', 'entertainment']
        }
        
        for tag, keywords in industry_patterns.items():
            if any(keyword in content_lower for keyword in keywords):
                suggestions.add(tag)
        
        # Content type patterns
        if any(word in content_lower for word in ['comparison', 'vs', 'versus', 'compare']):
            suggestions.add('comparison')
        if any(word in content_lower for word in ['review', 'rating', 'opinion']):
            suggestions.add('review')
        if any(word in content_lower for word in ['tips', 'advice', 'best practices']):
            suggestions.add('tips')
        if any(word in content_lower for word in ['interview', 'qa', 'q&a']):
            suggestions.add('interview')
        if any(word in content_lower for word in ['podcast', 'audio', 'listen']):
            suggestions.add('podcast')
        
        return suggestions

    def _extract_intelligent_content_tags(self, content: Dict[str, str]) -> Set[str]:
        """Extract intelligent tags based on actual content analysis"""
        text = content.get('full_content', '').lower()
        if not text:
            return set()
            
        suggestions = set()
        
        # Action/Purpose based tags with more specific patterns
        action_patterns = {
            'tutorial': ['how to', 'step by step', 'guide', 'learn', 'tutorial', 'walkthrough', 'beginner', 'getting started', 'introduction', 'basics'],
            'reference': ['documentation', 'docs', 'api reference', 'manual', 'specification', 'cheatsheet', 'quick reference', 'syntax'],
            'news': ['today', 'latest', 'breaking', 'update', 'announced', 'release', 'new version', 'changelog', 'what\'s new'],
            'review': ['review', 'comparison', 'vs', 'versus', 'opinion', 'rating', 'pros and cons', 'evaluation', 'assessment'],
            'tool': ['tool', 'utility', 'plugin', 'extension', 'app', 'software', 'library', 'framework', 'package'],
            'course': ['course', 'training', 'certification', 'bootcamp', 'class', 'workshop', 'masterclass', 'lesson'],
            'article': ['article', 'blog post', 'story', 'insights', 'thoughts', 'opinion', 'perspective'],
            'video': ['video', 'watch', 'youtube', 'stream', 'episode', 'webinar', 'screencast', 'recording'],
            'book': ['book', 'ebook', 'read', 'chapters', 'author', 'pdf', 'download', 'free book'],
            'research': ['research', 'study', 'analysis', 'report', 'findings', 'survey', 'whitepaper', 'case study'],
            'example': ['example', 'demo', 'sample', 'code example', 'implementation', 'showcase'],
            'list': ['list', 'collection', 'awesome', 'resources', 'curated', 'best of', 'top 10'],
            'interview': ['interview', 'q&a', 'questions', 'answers', 'discussion'],
            'podcast': ['podcast', 'audio', 'listen', 'episode', 'talk', 'discussion'],
        }
        
        for tag, keywords in action_patterns.items():
            if any(keyword in text for keyword in keywords):
                suggestions.add(tag)
        
        # Framework/Library specific extraction with more comprehensive keywords
        frameworks = {
            'react': ['react', 'reactjs', 'jsx', 'tsx', 'hooks', 'component', 'state management', 'usestate', 'useeffect', 'create-react-app', 'next.js', 'gatsby'],
            'vue': ['vue', 'vuejs', 'vue.js', 'composition api', 'single file', 'nuxt', 'vuex', 'pinia'],
            'angular': ['angular', 'angularjs', 'typescript', 'directive', 'service', 'rxjs', 'ionic'],
            'django': ['django', 'python web', 'orm', 'models', 'django rest', 'drf'],
            'laravel': ['laravel', 'php framework', 'eloquent', 'blade', 'artisan', 'composer'],
            'express': ['express', 'expressjs', 'nodejs', 'node.js', 'middleware', 'routes', 'npm'],
            'spring': ['spring', 'spring boot', 'java', 'dependency injection', 'beans', 'maven', 'gradle'],
            'flutter': ['flutter', 'dart', 'mobile', 'cross platform', 'widgets', 'pub'],
            'tensorflow': ['tensorflow', 'tf', 'machine learning', 'neural network', 'keras', 'deep learning'],
            'pytorch': ['pytorch', 'torch', 'deep learning', 'tensors', 'neural networks'],
            'fastapi': ['fastapi', 'python api', 'async', 'uvicorn', 'pydantic'],
            'flask': ['flask', 'python web', 'microframework', 'jinja2', 'werkzeug'],
            'svelte': ['svelte', 'sveltekit', 'reactive', 'compiler'],
            'nuxt': ['nuxt', 'nuxtjs', 'vue framework', 'ssr'],
            'nextjs': ['next.js', 'nextjs', 'react framework', 'vercel', 'ssr'],
            'tailwind': ['tailwind', 'tailwindcss', 'utility-first', 'css framework'],
            'bootstrap': ['bootstrap', 'css framework', 'responsive', 'grid'],
            'sass': ['sass', 'scss', 'css preprocessor'],
            'webpack': ['webpack', 'bundler', 'module bundler'],
            'vite': ['vite', 'build tool', 'fast build'],
        }
        
        for framework, keywords in frameworks.items():
            if any(keyword in text for keyword in keywords):
                suggestions.add(framework)
        
        return suggestions

    def _extract_technology_tags(self, content: Dict[str, str]) -> Set[str]:
        """Extract specific technology and tool mentions"""
        text = content.get('full_content', '').lower()
        if not text:
            return set()
            
        suggestions = set()
        
        # Programming languages with more specific patterns
        languages = {
            'python': ['python', 'python3', 'py', 'django', 'flask', 'fastapi', 'pandas', 'numpy', 'scipy', 'matplotlib', 'jupyter', 'pip', 'conda', 'virtualenv'],
            'javascript': ['javascript', 'js', 'ecmascript', 'node', 'nodejs', 'npm', 'yarn', 'es6', 'es2015', 'babel', 'eslint'],
            'typescript': ['typescript', 'ts', 'type safety', 'interfaces', 'generics', 'tsc', 'type annotations'],
            'java': ['java', 'openjdk', 'spring', 'spring boot', 'maven', 'gradle', 'junit', 'hibernate'],
            'csharp': ['c#', 'csharp', '.net', 'dotnet', 'asp.net', 'entity framework', 'visual studio', 'nuget'],
            'php': ['php', 'laravel', 'symfony', 'composer', 'wordpress', 'drupal', 'codeigniter'],
            'ruby': ['ruby', 'rails', 'ruby on rails', 'gem', 'bundler', 'rake', 'rspec'],
            'go': ['golang', 'go', 'go lang', 'goroutines', 'go mod', 'gofmt'],
            'rust': ['rust', 'cargo', 'memory safety', 'ownership', 'borrowing', 'rustc'],
            'swift': ['swift', 'ios', 'xcode', 'cocoapods', 'swiftui', 'objective-c'],
            'kotlin': ['kotlin', 'android', 'jvm', 'jetbrains', 'coroutines'],
            'cpp': ['c++', 'cpp', 'cmake', 'gcc', 'clang', 'boost'],
            'c': ['c language', 'gcc', 'make', 'cmake'],
            'scala': ['scala', 'sbt', 'akka', 'play framework'],
            'dart': ['dart', 'flutter', 'pub'],
            'elixir': ['elixir', 'phoenix', 'erlang', 'otp'],
            'haskell': ['haskell', 'ghc', 'cabal', 'stack'],
            'clojure': ['clojure', 'leiningen', 'jvm', 'lisp'],
        }
        
        for lang, keywords in languages.items():
            if any(keyword in text for keyword in keywords):
                suggestions.add(lang)
        
        # Databases
        databases = {
            'mysql': ['mysql', 'mariadb'],
            'postgresql': ['postgresql', 'postgres', 'psql'],
            'mongodb': ['mongodb', 'mongo', 'nosql', 'document'],
            'redis': ['redis', 'cache', 'in-memory'],
            'sqlite': ['sqlite', 'embedded database'],
        }
        
        for db, keywords in databases.items():
            if any(keyword in text for keyword in keywords):
                suggestions.add(db)
        
        # Cloud platforms
        cloud_platforms = {
            'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda'],
            'azure': ['azure', 'microsoft cloud'],
            'gcp': ['google cloud', 'gcp', 'firebase'],
            'docker': ['docker', 'container', 'containerization'],
            'kubernetes': ['kubernetes', 'k8s', 'orchestration'],
        }
        
        for platform, keywords in cloud_platforms.items():
            if any(keyword in text for keyword in keywords):
                suggestions.add(platform)
                
        return suggestions

    def _extract_topic_tags(self, content: Dict[str, str]) -> Set[str]:
        """Extract topic and subject-specific tags"""
        text = content.get('full_content', '').lower()
        if not text:
            return set()
            
        suggestions = set()
        
        # Development topics
        dev_topics = {
            'frontend': ['frontend', 'ui', 'user interface', 'client side'],
            'backend': ['backend', 'server', 'api', 'server side'],
            'fullstack': ['fullstack', 'full stack', 'end to end'],
            'mobile': ['mobile', 'ios', 'android', 'app development'],
            'web': ['web development', 'website', 'web app'],
            'api': ['api', 'rest', 'graphql', 'endpoint'],
            'database': ['database', 'sql', 'query', 'schema'],
            'testing': ['testing', 'unit test', 'integration', 'automation'],
            'deployment': ['deployment', 'deploy', 'production', 'hosting'],
            'performance': ['performance', 'optimization', 'speed', 'efficiency'],
            'security': ['security', 'authentication', 'authorization', 'encryption'],
        }
        
        for topic, keywords in dev_topics.items():
            if any(keyword in text for keyword in keywords):
                suggestions.add(topic)
        
        # Specific concepts
        concepts = {
            'machine-learning': ['machine learning', 'ml', 'artificial intelligence', 'ai'],
            'data-science': ['data science', 'analytics', 'visualization', 'statistics'],
            'blockchain': ['blockchain', 'cryptocurrency', 'bitcoin', 'ethereum'],
            'iot': ['internet of things', 'iot', 'sensors', 'embedded'],
            'devops': ['devops', 'ci/cd', 'continuous integration', 'infrastructure'],
            'open-source': ['open source', 'github', 'contributing', 'community'],
        }
        
        for concept, keywords in concepts.items():
            if any(keyword in text for keyword in keywords):
                suggestions.add(concept)
                
        return suggestions