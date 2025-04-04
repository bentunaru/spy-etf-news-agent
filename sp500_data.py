"""
Module to manage SPY ETF data (which tracks the S&P 500)
"""
import pandas as pd
import yfinance as yf

def get_sp500_companies():
    """
    Retrieves the list of companies that make up the S&P 500 (via the SPY ETF)
    
    Returns:
        pd.DataFrame: DataFrame containing the symbol and name of S&P 500 companies
    """
    # Use SPY (ETF that tracks the S&P 500) instead of ^GSPC
    spy = yf.Ticker("SPY")
    
    # Retrieve the list of components
    try:
        # This method gives the current components of the S&P 500
        spy_components = pd.DataFrame(spy.info['components'])
        # Rename columns for clarity
        spy_components.columns = ['Symbol', 'Name']
        return spy_components
    except (KeyError, TypeError):
        # Alternative method if the first one fails
        table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = table[0]
        return df[['Symbol', 'Security']].rename(columns={'Security': 'Name'})

def get_sp500_price():
    """
    Retrieves the current price of the SPY ETF
    
    Returns:
        dict: Dictionary containing the current price and price change
    """
    try:
        # Use SPY (ETF that tracks the S&P 500)
        spy = yf.Ticker("SPY")
        data = spy.history(period="5d")  # Request more days to ensure enough data
        
        if len(data) >= 2:
            current_price = data['Close'].iloc[-1]
            previous_price = data['Close'].iloc[-2]
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100
            
            return {
                'current_price': current_price,
                'change': change,
                'change_percent': change_percent
            }
        else:
            # Fallback if we don't have enough data
            return {
                'current_price': data['Close'].iloc[-1] if len(data) > 0 else 0,
                'change': 0,
                'change_percent': 0
            }
    except Exception as e:
        # In case of error, return default values
        print(f"Error retrieving SPY data: {e}")
        return {
            'current_price': 0,
            'change': 0,
            'change_percent': 0
        }

def get_sp500_historical_data(period="6mo"):
    """
    Retrieves historical data for the SPY ETF over a given period (6 months by default)
    
    Args:
        period (str): Period for historical data (default: "6mo" for 6 months)
        
    Returns:
        pd.DataFrame: DataFrame containing historical data (Open, High, Low, Close, Volume)
    """
    try:
        # Use SPY (ETF that tracks the S&P 500)
        spy = yf.Ticker("SPY")
        data = spy.history(period=period)
        
        if len(data) > 0:
            return data
        else:
            print("No historical data retrieved for SPY ETF")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error retrieving historical data for SPY ETF: {e}")
        return pd.DataFrame()

def is_valid_sp500_company(symbol):
    """
    Checks if the given symbol corresponds to an S&P 500 company
    
    Args:
        symbol (str): Symbol of the company to check
        
    Returns:
        bool: True if the company is part of the S&P 500, False otherwise
    """
    companies = get_sp500_companies()
    return symbol.upper() in companies['Symbol'].values
