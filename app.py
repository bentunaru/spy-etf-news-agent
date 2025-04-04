#!/usr/bin/env python3
"""
Streamlit web application for the ETF News Agent (SPY & QQQ)
"""
import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from news_fetcher import NewsApiFetcher, YahooFinanceFetcher
from etf_data import (
    get_etf_price, is_valid_etf_component, get_etf_historical_data, 
    get_etf_components, ETF_INFO
)
from price_prediction import (
    prepare_time_series_data, train_linear_regression, 
    train_random_forest, train_svr, predict_future_prices,
    evaluate_model
)

# Streamlit page configuration
st.set_page_config(
    page_title="ETF News Agent",
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
def display_historical_chart(etf_symbol="SPY", period="6mo"):
    """Displays a chart of ETF historical data"""
    data = get_etf_historical_data(etf_symbol, period)
    if data.empty:
        st.warning(f"No historical data available for {etf_symbol} ETF")
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
        title=f"{etf_symbol} ETF Historical Data ({period})",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=600,
        xaxis_rangeslider_visible=False,
        yaxis2_title="Volume",
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

# Function to display price predictions
def display_price_predictions(data, etf_symbol="SPY", forecast_days=5):
    """Display price predictions for the selected ETF"""
    st.header(f"{etf_symbol} ETF Price Predictions")
    
    # Show information about the prediction
    st.info(f"Predicting {etf_symbol} ETF prices for the next {forecast_days} trading days based on historical data.")
    
    # Prepare data for prediction
    prepared_data = prepare_time_series_data(
        data, 
        lookback=30,  # Use 30 days of history
        forecast_horizon=forecast_days, 
        test_size=0.2
    )
    
    # Create columns for model selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Select Prediction Model")
        model_type = st.selectbox(
            "Model",
            ["Linear Regression", "Random Forest", "Support Vector Regression"],
            index=0
        )
    
    with col2:
        st.subheader("Model Parameters")
        lookback_days = st.slider(
            "Days of history to use",
            min_value=10,
            max_value=60,
            value=30,
            step=5
        )
    
    # Train selected model
    if model_type == "Linear Regression":
        model = train_linear_regression(prepared_data['X_train'], prepared_data['y_train'])
        model_name = "Linear Regression"
    elif model_type == "Random Forest":
        model = train_random_forest(prepared_data['X_train'], prepared_data['y_train'])
        model_name = "Random Forest"
    else:
        model = train_svr(prepared_data['X_train'], prepared_data['y_train'])
        model_name = "SVR"
    
    # Evaluate model
    eval_results = evaluate_model(model, prepared_data['X_test'], prepared_data['y_test'])
    
    # Make predictions
    predicted_prices = predict_future_prices(
        model, 
        prepared_data['latest_sequence'], 
        prepared_data['scaler'], 
        forecast_horizon=forecast_days
    )
    
    # Create prediction dataframe
    last_date = data.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days)
    pred_df = pd.DataFrame({
        'Date': future_dates,
        'Predicted_Close': predicted_prices
    })
    pred_df.set_index('Date', inplace=True)
    
    # Display prediction metrics
    st.subheader("Model Performance")
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
    with metrics_col1:
        st.metric("R² Score", f"{eval_results['r2']:.4f}")
    
    with metrics_col2:
        st.metric("RMSE", f"{eval_results['rmse']:.4f}")
    
    with metrics_col3:
        st.metric("MAE", f"{eval_results['mae']:.4f}")
    
    # Create visualization
    st.subheader(f"Price Predictions ({model_name})")
    
    # Create figure
    fig = go.Figure()
    
    # Add actual historical prices
    fig.add_trace(go.Scatter(
        x=data.index[-30:],  # Show last 30 days
        y=data['Close'][-30:],
        mode='lines',
        name='Historical Prices',
        line=dict(color='blue')
    ))
    
    # Add predicted prices
    fig.add_trace(go.Scatter(
        x=pred_df.index,
        y=pred_df['Predicted_Close'],
        mode='lines+markers',
        name='Predicted Prices',
        line=dict(color='green', dash='dash'),
        marker=dict(size=8)
    ))
    
    # Add prediction interval (simplified)
    upper_bound = pred_df['Predicted_Close'] * (1 + eval_results['rmse'])
    lower_bound = pred_df['Predicted_Close'] * (1 - eval_results['rmse'])
    
    fig.add_trace(go.Scatter(
        x=pred_df.index,
        y=upper_bound,
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=pred_df.index,
        y=lower_bound,
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(0, 255, 0, 0.1)',
        name='Prediction Interval'
    ))
    
    # Update layout
    fig.update_layout(
        title=f"{etf_symbol} ETF Price Prediction for the Next {forecast_days} Trading Days",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display predicted values in a table
    st.subheader("Predicted Prices Table")
    st.dataframe(pred_df)
    
    # Add disclaimer
    st.caption("**Disclaimer**: These predictions are based on historical data and should not be used as financial advice. Past performance is not indicative of future results.")

# Application title
st.title("📈 ETF News Agent")
st.markdown("---")

# Sidebar for options
st.sidebar.title("Options")

# ETF selection
etf_symbol = st.sidebar.selectbox(
    "Select ETF",
    list(ETF_INFO.keys()),
    index=0,  # SPY default
    format_func=lambda x: f"{x} - {ETF_INFO[x]}"
)

period = st.sidebar.selectbox(
    "Historical data period",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=2  # 6mo default
)

company_filter = st.sidebar.text_input(
    f"Filter by {etf_symbol} component (e.g.: AAPL)",
    key="company_filter",
)

news_limit = st.sidebar.slider(
    "Number of news to display",
    min_value=5,
    max_value=20,
    value=10
)

# Check if the specified company is valid
if company_filter and not is_valid_etf_component(company_filter, etf_symbol):
    st.sidebar.error(f"{company_filter} is not a valid {etf_symbol} component.")
    company_filter = None

# Main display in two columns
col1, col2 = st.columns([1, 1])

# Column 1: Price and chart
with col1:
    # Get and display current price
    price_data = get_etf_price(etf_symbol)
    
    if price_data['current_price'] > 0:
        price_delta = f"{price_data['change']:.2f} ({price_data['change_percent']:.2f}%)"
        st.metric(
            label=f"{etf_symbol} ETF (Current Price)",
            value=f"${price_data['current_price']:.2f}",
            delta=price_delta
        )
    else:
        st.error(f"Unable to retrieve current {etf_symbol} ETF price")
    
    # Display update time
    st.caption(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display historical chart
    display_historical_chart(etf_symbol, period)
    
    # Show price predictions if checkbox is checked
    if st.checkbox("Show price predictions", value=False):
        data = get_etf_historical_data(etf_symbol, period)
        if not data.empty:
            display_price_predictions(data, etf_symbol, forecast_days=5)
        else:
            st.warning(f"Cannot make predictions: no historical data available for {etf_symbol}")

# Column 2: News
with col2:
    st.header(f"Latest news about {company_filter if company_filter else etf_symbol + ' ETF'}")
    
    # Retrieve and display news
    articles = get_news(query=company_filter if company_filter else etf_symbol, limit=news_limit)
    
    if not articles:
        st.info(f"No news found for {company_filter if company_filter else etf_symbol + ' ETF'}")
    
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
st.caption("2025 ETF News Agent - Developed with Streamlit")
