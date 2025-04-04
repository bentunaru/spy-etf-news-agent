"""
Module to retrieve the latest news about the SPY ETF (which tracks the S&P 500)
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from newsapi import NewsApiClient
import yfinance as yf

# Load environment variables
load_dotenv()

class NewsFetcher:
    """Base class for news collectors"""
    
    def get_news(self, query=None, limit=10):
        """
        Abstract method for retrieving news
        
        Args:
            query (str, optional): Specific search term
            limit (int, optional): Maximum number of results to return
            
        Returns:
            list: List of formatted articles
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def format_article(self, article):
        """
        Formats an article into a standard format
        
        Args:
            article (dict): Raw article from the source
            
        Returns:
            dict: Formatted article
        """
        raise NotImplementedError("Subclasses must implement this method")


class NewsApiFetcher(NewsFetcher):
    """News collector using News API"""
    
    def __init__(self):
        """Initializes the News API client"""
        api_key = os.getenv('NEWS_API_KEY')
        if not api_key:
            raise ValueError("News API key missing. Please set the NEWS_API_KEY environment variable.")
        self.api = NewsApiClient(api_key=api_key)
    
    def get_news(self, query=None, limit=10):
        """
        Retrieves news from News API
        
        Args:
            query (str, optional): Specific search term
            limit (int, optional): Maximum number of results
            
        Returns:
            list: List of formatted articles
        """
        # Define the base query for the SPY ETF
        base_query = "SPY ETF OR SPDR S&P 500 ETF"
        
        # Add the specific search term if provided
        if query:
            search_query = f"{base_query} AND {query}"
        else:
            search_query = base_query
        
        # Calculate the date one week ago to limit results
        one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Make the API request
        response = self.api.get_everything(
            q=search_query,
            language='en',
            sort_by='publishedAt',
            from_param=one_week_ago,
            page_size=limit
        )
        
        # Format the articles
        articles = []
        for article in response['articles'][:limit]:
            articles.append(self.format_article(article))
        
        return articles
    
    def format_article(self, article):
        """
        Formats a News API article into the standard format
        
        Args:
            article (dict): Raw article from News API
            
        Returns:
            dict: Formatted article
        """
        return {
            'title': article['title'],
            'description': article['description'],
            'url': article['url'],
            'source': article['source']['name'],
            'published_at': article['publishedAt'],
            'api_source': 'News API'
        }


class YahooFinanceFetcher(NewsFetcher):
    """News collector using Yahoo Finance"""
    
    def get_news(self, query=None, limit=10):
        """
        Retrieves news from Yahoo Finance
        
        Args:
            query (str, optional): Company symbol (e.g.: AAPL)
            limit (int, optional): Maximum number of results
            
        Returns:
            list: List of formatted articles
        """
        try:
            # Use the SPY ticker (S&P 500 ETF) or the specific company ticker
            ticker_symbol = query if query else "SPY"
            
            # Retrieve data
            ticker = yf.Ticker(ticker_symbol)
            news = ticker.news
            
            # Check if news is None or empty
            if news is None or len(news) == 0:
                print(f"No news found for {ticker_symbol} via Yahoo Finance")
                return []
            
            # Format the articles
            articles = []
            for article in news[:limit]:
                articles.append(self.format_article(article))
            
            return articles
            
        except Exception as e:
            print(f"Error retrieving Yahoo Finance news: {e}")
            return []
    
    def format_article(self, article):
        """
        Formats a Yahoo Finance article into the standard format
        
        Args:
            article (dict): Raw article from Yahoo Finance
            
        Returns:
            dict: Formatted article
        """
        try:
            # Convert timestamp to datetime format
            published_at = datetime.fromtimestamp(article.get('providerPublishTime', 0)).isoformat()
            
            return {
                'title': article.get('title', 'Title not available'),
                'description': article.get('summary', 'Description not available'),
                'url': article.get('link', '#'),
                'source': article.get('publisher', 'Yahoo Finance'),
                'published_at': published_at,
                'api_source': 'Yahoo Finance'
            }
        except Exception as e:
            # In case of error, return an article with default values
            print(f"Error formatting a Yahoo Finance article: {e}")
            return {
                'title': 'Retrieval Error',
                'description': 'Unable to retrieve details for this article',
                'url': '#',
                'source': 'Yahoo Finance',
                'published_at': datetime.now().isoformat(),
                'api_source': 'Yahoo Finance'
            }
