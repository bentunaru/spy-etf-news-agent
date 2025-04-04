"""
Module to manage ETF data (SPY for S&P 500 and QQQ for Nasdaq-100)
"""
import pandas as pd
import yfinance as yf

# Dictionary mapping ETF symbols to their descriptions
ETF_INFO = {
    "SPY": "SPDR S&P 500 ETF Trust (tracks the S&P 500 Index)",
    "QQQ": "Invesco QQQ Trust (tracks the Nasdaq-100 Index)"
}

def get_etf_components(etf_symbol="SPY"):
    """
    Retrieves the list of companies that make up the selected ETF
    
    Args:
        etf_symbol (str): ETF symbol ("SPY" for S&P 500, "QQQ" for Nasdaq-100)
        
    Returns:
        pd.DataFrame: DataFrame containing the symbol and name of ETF components
    """
    # Use the specified ETF
    ticker = yf.Ticker(etf_symbol)
    
    # Retrieve the list of components
    try:
        # This method gives the current components
        components = pd.DataFrame(ticker.info['components'])
        # Rename columns for clarity
        components.columns = ['Symbol', 'Name']
        return components
    except (KeyError, TypeError):
        # Alternative method if the first one fails
        if etf_symbol == "SPY":
            table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            df = table[0]
            return df[['Symbol', 'Security']].rename(columns={'Security': 'Name'})
        elif etf_symbol == "QQQ":
            table = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
            df = table[3]  # The table with the component list
            return df[['Ticker', 'Company']].rename(columns={'Ticker': 'Symbol', 'Company': 'Name'})
        else:
            return pd.DataFrame(columns=['Symbol', 'Name'])

def get_etf_price(etf_symbol="SPY"):
    """
    Retrieves the current price of the selected ETF
    
    Args:
        etf_symbol (str): ETF symbol ("SPY" for S&P 500, "QQQ" for Nasdaq-100)
        
    Returns:
        dict: Dictionary containing the current price and price change
    """
    try:
        # Use the specified ETF
        ticker = yf.Ticker(etf_symbol)
        data = ticker.history(period="5d")  # Request more days to ensure enough data
        
        if len(data) >= 2:
            current_price = data['Close'].iloc[-1]
            previous_price = data['Close'].iloc[-2]
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100
            
            return {
                'symbol': etf_symbol,
                'current_price': current_price,
                'change': change,
                'change_percent': change_percent
            }
        else:
            # Fallback if we don't have enough data
            return {
                'symbol': etf_symbol,
                'current_price': data['Close'].iloc[-1] if len(data) > 0 else 0,
                'change': 0,
                'change_percent': 0
            }
    except Exception as e:
        # In case of error, return default values
        print(f"Error retrieving {etf_symbol} data: {e}")
        return {
            'symbol': etf_symbol,
            'current_price': 0,
            'change': 0,
            'change_percent': 0
        }

def get_etf_historical_data(etf_symbol="SPY", period="6mo"):
    """
    Retrieves historical data for the selected ETF over a given period
    
    Args:
        etf_symbol (str): ETF symbol ("SPY" for S&P 500, "QQQ" for Nasdaq-100)
        period (str): Period for historical data (default: "6mo" for 6 months)
        
    Returns:
        pd.DataFrame: DataFrame containing historical data (Open, High, Low, Close, Volume)
    """
    try:
        # Use the specified ETF
        ticker = yf.Ticker(etf_symbol)
        data = ticker.history(period=period)
        
        if len(data) > 0:
            return data
        else:
            print(f"No historical data retrieved for {etf_symbol} ETF")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error retrieving historical data for {etf_symbol} ETF: {e}")
        return pd.DataFrame()

def is_valid_etf_component(symbol, etf_symbol="SPY"):
    """
    Checks if the given symbol corresponds to a component of the selected ETF
    
    Args:
        symbol (str): Symbol of the company to check
        etf_symbol (str): ETF symbol ("SPY" for S&P 500, "QQQ" for Nasdaq-100)
        
    Returns:
        bool: True if the company is part of the ETF, False otherwise
    """
    components = get_etf_components(etf_symbol)
    return symbol.upper() in components['Symbol'].values

# For backwards compatibility
get_sp500_companies = lambda: get_etf_components("SPY")
get_sp500_price = lambda: get_etf_price("SPY")
get_sp500_historical_data = lambda period="6mo": get_etf_historical_data("SPY", period)
is_valid_sp500_company = lambda symbol: is_valid_etf_component(symbol, "SPY")
