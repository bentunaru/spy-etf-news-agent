#!/usr/bin/env python3
"""
ETF News Agent - Retrieves the latest news about ETFs (SPY and QQQ) and their components
"""
import argparse
import sys
from datetime import datetime
from dotenv import load_dotenv

from news_fetcher import NewsApiFetcher, YahooFinanceFetcher
from etf_data import get_etf_price, is_valid_etf_component, ETF_INFO

# Load environment variables
load_dotenv()

def print_header():
    """Displays the application header"""
    print("\n" + "=" * 80)
    print(" " * 30 + "ETF NEWS AGENT")
    print("=" * 80 + "\n")

def print_etf_status(etf_symbol="SPY"):
    """
    Displays the current status of the selected ETF
    
    Args:
        etf_symbol (str): ETF symbol (SPY or QQQ)
    """
    try:
        data = get_etf_price(etf_symbol)
        print(f"{etf_symbol} ETF ({ETF_INFO[etf_symbol]}): {data['current_price']:.2f} ", end="")
        
        if data['change'] >= 0:
            print(f"▲ +{data['change']:.2f} (+{data['change_percent']:.2f}%)")
        else:
            print(f"▼ {data['change']:.2f} ({data['change_percent']:.2f}%)")
        
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print("-" * 80 + "\n")
    except Exception as e:
        print(f"Unable to retrieve {etf_symbol} ETF price: {e}")
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
    parser = argparse.ArgumentParser(description="ETF News Agent")
    parser.add_argument('--source', choices=['newsapi', 'yahoo', 'all'], 
                        default='all', help="Data source to use")
    parser.add_argument('--etf', choices=['SPY', 'QQQ'], default='SPY',
                        help="ETF to analyze (SPY for S&P 500, QQQ for Nasdaq-100)")
    parser.add_argument('--company', type=str, help="ETF component symbol (e.g: AAPL)")
    parser.add_argument('--limit', type=int, default=10, help="Maximum number of results")
    
    args = parser.parse_args()
    
    # Check if the specified company is part of the selected ETF
    if args.company and not is_valid_etf_component(args.company, args.etf):
        print(f"Error: {args.company} is not a component of the {args.etf} ETF.")
        sys.exit(1)
    
    print_header()
    print_etf_status(args.etf)
    
    # Prepare the query
    # If a company is specified, use it as the query
    # Otherwise, use the ETF symbol
    query = args.company if args.company else args.etf
    
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
        headline = f"Latest news about "
        if args.company:
            headline += f"{args.company} (component of {args.etf} ETF)"
        else:
            headline += f"{args.etf} ETF ({ETF_INFO[args.etf]})"
        
        print(f"{headline}:\n")
        for i, article in enumerate(all_articles, 1):
            print_article(article, i)
    else:
        print("No news found.")

if __name__ == "__main__":
    main()
