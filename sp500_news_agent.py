#!/usr/bin/env python3
"""
SPY ETF News Agent - Retrieves the latest news about the SPY ETF and its components
"""
import argparse
import sys
from datetime import datetime
from dotenv import load_dotenv

from news_fetcher import NewsApiFetcher, YahooFinanceFetcher
from sp500_data import get_sp500_price, is_valid_sp500_company

# Load environment variables
load_dotenv()

def print_header():
    """Displays the application header"""
    print("\n" + "=" * 80)
    print(" " * 30 + "SPY ETF NEWS AGENT")
    print("=" * 80 + "\n")

def print_sp500_status():
    """Displays the current status of the SPY ETF"""
    try:
        data = get_sp500_price()
        print(f"SPY ETF: {data['current_price']:.2f} ", end="")
        
        if data['change'] >= 0:
            print(f"▲ +{data['change']:.2f} (+{data['change_percent']:.2f}%)")
        else:
            print(f"▼ {data['change']:.2f} ({data['change_percent']:.2f}%)")
        
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print("-" * 80 + "\n")
    except Exception as e:
        print(f"Unable to retrieve SPY ETF price: {e}")
        print("-" * 80 + "\n")

def print_article(article, index):
    """
    Displays a formatted article
    
    Args:
        article (dict): Formatted article
        index (int): Article number
    """
    published_date = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
    published_str = published_date.strftime('%Y-%m-%d %H:%M')
    
    print(f"{index}. {article['title']}")
    print(f"   Source: {article['source']} ({article['api_source']}) | {published_str}")
    print(f"   {article['description']}")
    print(f"   URL: {article['url']}")
    print()

def main():
    """Main function of the agent"""
    parser = argparse.ArgumentParser(description="SPY ETF News Agent")
    parser.add_argument('--source', choices=['newsapi', 'yahoo', 'all'], 
                        default='all', help="Data source to use")
    parser.add_argument('--company', type=str, help="S&P 500 company symbol (e.g: AAPL)")
    parser.add_argument('--limit', type=int, default=10, help="Maximum number of results")
    
    args = parser.parse_args()
    
    # Check if the specified company is part of the S&P 500
    if args.company and not is_valid_sp500_company(args.company):
        print(f"Error: {args.company} is not an S&P 500 company.")
        sys.exit(1)
    
    print_header()
    print_sp500_status()
    
    # Prepare the query
    query = args.company
    
    # Initialize news collectors according to the chosen source
    news_sources = []
    if args.source in ['newsapi', 'all']:
        try:
            news_sources.append(NewsApiFetcher())
        except ValueError as e:
            print(f"NewsAPI Error: {e}")
    
    if args.source in ['yahoo', 'all']:
        news_sources.append(YahooFinanceFetcher())
    
    if not news_sources:
        print("No news sources available.")
        sys.exit(1)
    
    # Retrieve news from each source
    all_articles = []
    for source in news_sources:
        try:
            articles = source.get_news(query=query, limit=args.limit)
            all_articles.extend(articles)
        except Exception as e:
            print(f"Error retrieving news: {e}")
    
    # Sort articles by publication date (from most recent to oldest)
    all_articles.sort(key=lambda x: x['published_at'], reverse=True)
    
    # Limit the total number of articles
    all_articles = all_articles[:args.limit]
    
    # Display the results
    if all_articles:
        print(f"Latest news about {args.company if args.company else 'SPY ETF'}:\n")
        for i, article in enumerate(all_articles, 1):
            print_article(article, i)
    else:
        print("No news found.")

if __name__ == "__main__":
    main()
