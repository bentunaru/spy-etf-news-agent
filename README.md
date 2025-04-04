# ETF News Agent

This agent retrieves the latest news and data about ETFs and their components. Currently supports:
- **SPY ETF**: SPDR S&P 500 ETF Trust (tracks the S&P 500 Index)
- **QQQ ETF**: Invesco QQQ Trust (tracks the Nasdaq-100 Index)

## Features

- Retrieval of the latest news about the selected ETF
- Historical data retrieval for ETFs over different time periods
- News filtering by ETF component companies
- Multiple data sources (News API, Yahoo Finance)
- Formatted display of results in two interfaces:
  - Console interface: text output
  - Web interface: interactive Streamlit application with modern graphics and layouts
- **Advanced trend analysis**:
  - Colored linear regression line (green for bullish trend, red for bearish trend)
  - Trend statistics (R², P-value, Standard Error)
  - Visual indication of trend direction and strength
- **Machine Learning price predictions**:
  - Multiple prediction models (Linear Regression, Random Forest, Support Vector Regression)
  - Interactive prediction visualization with confidence intervals
  - Model performance metrics (R², RMSE, MAE)
  - Customizable prediction parameters

## Installation

1. Clone this repository
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Create a `.env` file and add your News API key (free at [newsapi.org](https://newsapi.org/))
```
NEWS_API_KEY=your_api_key_here
```

## Usage

### Console Interface

To run the agent via command line:

```
python sp500_news_agent.py
```

Optional arguments:
- `--source`: Choose the data source ('newsapi' or 'yahoo', default: all)
- `--etf`: Choose ETF to analyze ('SPY' or 'QQQ', default: 'SPY')
- `--company`: Filter news for a specific ETF component company (for example: 'AAPL')
- `--limit`: Limit the number of results (default: 10)

Example:
```
python sp500_news_agent.py --source newsapi --etf QQQ --company AAPL --limit 5
```

### Streamlit Web Interface

To launch the interactive web application:

```
streamlit run app.py
```

Web interface features:
- **ETF Selection**: Choose between SPY (S&P 500) and QQQ (Nasdaq-100) ETFs
- Display of the current ETF price with variation
- Interactive historical data chart with:
  - Candlestick chart for prices
  - Bar chart for volume
  - Linear regression line for trend analysis (green/red depending on direction)
  - Options for different time periods (1 month to 5 years)
- Trend statistics (slope, R², P-value, standard error)
- News section with expandable articles
- Sidebar with filtering options:
  - ETF selection (SPY or QQQ)
  - Historical data period
  - ETF component company filtering
  - Number of news to display
- **Price predictions**:
  - Enable price predictions via checkbox
  - Select from multiple ML models
  - View predicted prices for next 5 trading days
  - Assess model reliability through performance metrics
  - Visualize prediction intervals to understand uncertainty

## Price Prediction Feature

The price prediction functionality uses machine learning to forecast ETF prices:

1. **Available Models**:
   - **Linear Regression**: Simple, interpretable model for trend-based predictions
   - **Random Forest**: Ensemble model that can capture non-linear patterns
   - **Support Vector Regression**: Robust model that performs well with complex data

2. **How to Use**:
   - Select your desired ETF (SPY or QQQ) from the sidebar
   - Select a historical data period from the sidebar
   - Check the "Show price predictions" option below the historical chart
   - Choose your preferred prediction model
   - Adjust parameters as needed
   - Review the predicted prices and model performance metrics

3. **Interpretation**:
   - The prediction chart shows historical prices in blue
   - Predicted future prices appear as a dashed green line
   - The shaded green area represents the prediction confidence interval
   - Wider intervals indicate higher uncertainty in the prediction

## Project Structure

- `etf_data.py`: Module for retrieving ETF data (price, component companies, historical data)
- `news_fetcher.py`: Module for retrieving news from different sources
- `sp500_news_agent.py`: Main console application
- `app.py`: Streamlit web application
- `price_prediction.py`: ML models for ETF price forecasting
- `.env`: Configuration file for API keys

## Main Dependencies

- `yfinance`: Financial data retrieval
- `pandas`: Data manipulation
- `newsapi-python`: News API access
- `streamlit`: Interactive web interface
- `plotly`: Interactive data visualizations
- `matplotlib`: Visualization support
- `scipy`: Statistical analysis and regression calculation
- `python-dotenv`: Environment variable management
- `scikit-learn`: Machine learning models for price prediction

## Notes

- If you encounter issues with News API, check that your API key is valid and that you haven't exceeded your request quota.
- The application supports two ETFs:
  - **SPY**: SPDR S&P 500 ETF Trust - tracks the performance of the S&P 500 Index
  - **QQQ**: Invesco QQQ Trust - tracks the Nasdaq-100 Index of the largest non-financial companies
- Trend analyses are based on statistical calculations such as linear regression but do not constitute investment advice.
- Price predictions are for educational purposes only and should not be used for actual trading decisions. Past performance is not indicative of future results.
