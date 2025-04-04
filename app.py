#!/usr/bin/env python3
"""
Streamlit web application for the SPY ETF News Agent
"""
import streamlit as st
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from news_fetcher import NewsApiFetcher, YahooFinanceFetcher
from sp500_data import get_sp500_price, is_valid_sp500_company, get_sp500_historical_data

# Streamlit page configuration
st.set_page_config(
    page_title="SPY ETF News Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to get news
def get_news(query=None, limit=10):
    """Retrieves news from all available sources"""
    news_sources = []
    
    try:
        news_sources.append(NewsApiFetcher())
    except ValueError as e:
        st.warning(f"NewsAPI Error: {e}")
    
    news_sources.append(YahooFinanceFetcher())
    
    all_articles = []
    for source in news_sources:
        try:
            articles = source.get_news(query=query, limit=limit)
            all_articles.extend(articles)
        except Exception as e:
            st.error(f"Error retrieving news: {e}")
    
    # Sort articles by publication date (from most recent to oldest)
    all_articles.sort(key=lambda x: x['published_at'], reverse=True)
    
    # Limit the total number of articles
    return all_articles[:limit]

# Function to display historical chart
def display_historical_chart(period="6mo"):
    """Displays a chart of SPY ETF historical data"""
    data = get_sp500_historical_data(period=period)
    if data.empty:
        st.warning("No historical data available for SPY ETF")
        return
    
    # Calculate the linear regression line
    import numpy as np
    from scipy import stats
    
    # Create a numerical index for regression
    x = np.arange(len(data))
    # Filter NaN values for regression
    mask = ~np.isnan(data['Close'])
    if sum(mask) > 1:  # At least 2 points are needed for regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x[mask], data['Close'][mask])
        # Create the trend line
        line = slope * x + intercept
        data['Trend'] = line
        
        # Determine the trend direction
        trend_direction = "bullish" if slope > 0 else "bearish"
        trend_strength = abs(slope)
        
        # Display trend information
        st.info(f"{trend_direction.capitalize()} trend (slope: {slope:.6f})")
        
        # Calculate additional statistics
        st.sidebar.markdown("### Trend Statistics")
        st.sidebar.markdown(f"**R²:** {r_value**2:.4f}")
        st.sidebar.markdown(f"**P-value:** {p_value:.6f}")
        st.sidebar.markdown(f"**Standard error:** {std_err:.6f}")
    
    # Create an interactive chart with Plotly
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, 
                        row_heights=[0.7, 0.3])
    
    # Add candlestick chart for prices
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Price"
    ), row=1, col=1)
    
    # Add the regression line if it exists
    if 'Trend' in data.columns:
        # Determine color based on trend direction
        trend_color = 'green' if slope > 0 else 'red'
        
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data['Trend'], 
            line=dict(color=trend_color, width=2, dash='dash'),
            name="Trend line"
        ), row=1, col=1)
    
    # Add volume chart
    fig.add_trace(go.Bar(
        x=data.index,
        y=data['Volume'],
        name="Volume",
        marker_color='rgba(0, 0, 255, 0.3)'
    ), row=2, col=1)
    
    # Customize the chart
    fig.update_layout(
        title=f"SPY ETF Historical Data ({period})",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=600,
        xaxis_rangeslider_visible=False,
        yaxis2_title="Volume",
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

# Application title
st.title("📈 SPY ETF News Agent")
st.markdown("---")

# Sidebar for options
st.sidebar.title("Options")
period = st.sidebar.selectbox(
    "Historical data period",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=2  # 6mo default
)

company_filter = st.sidebar.text_input(
    "Filter by S&P 500 company (e.g.: AAPL)",
    key="company_filter",
)

news_limit = st.sidebar.slider(
    "Number of news to display",
    min_value=5,
    max_value=20,
    value=10
)

# Check if the specified company is valid
if company_filter and not is_valid_sp500_company(company_filter):
    st.sidebar.error(f"{company_filter} is not a valid S&P 500 company.")
    company_filter = None

# Main display in two columns
col1, col2 = st.columns([1, 1])

# Column 1: Price and chart
with col1:
    # Get and display current price
    price_data = get_sp500_price()
    
    if price_data['current_price'] > 0:
        price_delta = f"{price_data['change']:.2f} ({price_data['change_percent']:.2f}%)"
        st.metric(
            label="SPY ETF (Current Price)",
            value=f"${price_data['current_price']:.2f}",
            delta=price_delta
        )
    else:
        st.error("Unable to retrieve current SPY ETF price")
    
    # Display update time
    st.caption(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display historical chart
    display_historical_chart(period)

# Column 2: News
with col2:
    st.header(f"Latest news about {company_filter if company_filter else 'SPY ETF'}")
    
    # Retrieve and display news
    articles = get_news(query=company_filter, limit=news_limit)
    
    if not articles:
        st.info(f"No news found for {company_filter if company_filter else 'SPY ETF'}")
    
    for article in articles:
        # Convert publication date
        try:
            published_date = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
            published_str = published_date.strftime('%Y-%m-%d %H:%M')
        except:
            published_str = "Unknown date"
        
        # Create article card
        with st.expander(f"{article['title']}"):
            st.caption(f"Source: {article['source']} ({article['api_source']}) | {published_str}")
            st.write(article['description'])
            st.markdown(f"[Read full article]({article['url']})")

# Footer
st.markdown("---")
st.caption("2025 SPY ETF News Agent - Developed with Streamlit")
