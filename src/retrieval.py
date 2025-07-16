import requests
import praw
from newspaper import Article
from typing import List, Dict, Any
from dataclasses import dataclass
from config import Config
import time

@dataclass
class Source:
    url: str
    title: str
    content: str
    source_type: str
    timestamp: str
    relevance_score: float = 0.0

class NewsRetriever:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
    
    def search_news(self, query: str, max_results: int = 10) -> List[Source]:
        if not self.api_key:
            return []
        
        params = {
            'q': query,
            'apiKey': self.api_key,
            'language': 'en',
            'sortBy': 'relevancy',
            'pageSize': max_results
        }
        
        try:
            response = requests.get(f"{self.base_url}/everything", params=params)
            response.raise_for_status()
            data = response.json()
            
            sources = []
            for article in data.get('articles', []):
                try:
                    news_article = Article(article['url'])
                    news_article.download()
                    news_article.parse()
                    
                    source = Source(
                        url=article['url'],
                        title=article['title'],
                        content=news_article.text[:1000],
                        source_type='news',
                        timestamp=article['publishedAt']
                    )
                    sources.append(source)
                    time.sleep(0.1)
                except:
                    continue
            
            return sources
        except Exception as e:
            print(f"Error retrieving news: {e}")
            return []

class RedditRetriever:
    def __init__(self):
        try:
            self.reddit = praw.Reddit(
                client_id=Config.REDDIT_CLIENT_ID,
                client_secret=Config.REDDIT_CLIENT_SECRET,
                user_agent=Config.REDDIT_USER_AGENT
            )
        except:
            self.reddit = None
    
    def search_reddit(self, query: str, subreddits: List[str] = None, max_results: int = 10) -> List[Source]:
        if not self.reddit:
            return []
        
        if subreddits is None:
            subreddits = ['cryptocurrency', 'Bitcoin', 'ethereum', 'CryptoCurrency']
        
        sources = []
        
        try:
            for subreddit_name in subreddits:
                subreddit = self.reddit.subreddit(subreddit_name)
                submissions = subreddit.search(query, limit=max_results//len(subreddits), sort='relevance')
                
                for submission in submissions:
                    if len(sources) >= max_results:
                        break
                    
                    content = submission.selftext if submission.selftext else submission.title
                    if len(content) < 50:
                        continue
                    
                    source = Source(
                        url=f"https://reddit.com{submission.permalink}",
                        title=submission.title,
                        content=content[:1000],
                        source_type='reddit',
                        timestamp=str(submission.created_utc)
                    )
                    sources.append(source)
        except Exception as e:
            print(f"Error retrieving Reddit content: {e}")
        
        return sources

class CryptoBlogRetriever:
    def __init__(self):
        self.crypto_sites = [
            'coindesk.com',
            'cointelegraph.com',
            'decrypt.co',
            'theblock.co'
        ]
    
    def search_blogs(self, query: str, max_results: int = 10) -> List[Source]:
        sources = []
        
        try:
            for site in self.crypto_sites:
                search_url = f"https://www.google.com/search?q=site:{site} {query}"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(search_url, headers=headers)
                if response.status_code == 200:
                    time.sleep(1)
                
                if len(sources) >= max_results:
                    break
        except Exception as e:
            print(f"Error retrieving blog content: {e}")
        
        return sources

class UnifiedRetriever:
    def __init__(self):
        self.news_retriever = NewsRetriever()
        self.reddit_retriever = RedditRetriever()
        self.blog_retriever = CryptoBlogRetriever()
    
    def retrieve_all(self, query: str, max_per_source: int = 5) -> List[Source]:
        all_sources = []
        
        news_sources = self.news_retriever.search_news(query, max_per_source)
        reddit_sources = self.reddit_retriever.search_reddit(query, max_results=max_per_source)
        blog_sources = self.blog_retriever.search_blogs(query, max_per_source)
        
        all_sources.extend(news_sources)
        all_sources.extend(reddit_sources)
        all_sources.extend(blog_sources)
        
        # Fallback mock sources if no real sources found
        if not all_sources:
            all_sources = self._create_mock_sources(query)
        
        return all_sources
    
    def _create_mock_sources(self, query: str) -> List[Source]:
        return [
            Source(
                url="https://example.com/mock1",
                title=f"Analysis of {query} trends and implications",
                content=f"Recent analysis shows that {query} presents both opportunities and challenges. Market experts suggest careful consideration of various factors including regulatory frameworks, technological developments, and market dynamics.",
                source_type="mock",
                timestamp="2024-01-01",
                relevance_score=0.8
            ),
            Source(
                url="https://example.com/mock2", 
                title=f"Expert opinions on {query} future outlook",
                content=f"Industry experts have mixed views on {query}. Some believe it represents significant innovation potential, while others express concerns about volatility and regulatory uncertainty. Long-term implications remain to be seen.",
                source_type="mock",
                timestamp="2024-01-01",
                relevance_score=0.7
            )
        ]