"""
Module for price prediction models for ETFs (SPY and QQQ)
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def prepare_time_series_data(data, lookback=30, forecast_horizon=5, test_size=0.2):
    """
    Prepare time series data for prediction models
    
    Args:
        data (pd.DataFrame): Historical price data with 'Close' column
        lookback (int): Number of previous days to use for prediction
        forecast_horizon (int): Number of days to forecast
        test_size (float): Proportion of data to use for testing
    
    Returns:
        dict: Dictionary containing prepared datasets for training and testing
    """
    # Use adjusted close price
    close_prices = data['Close'].values.reshape(-1, 1)
    
    # Scale the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_prices = scaler.fit_transform(close_prices)
    
    # Create sequences
    X, y = [], []
    for i in range(lookback, len(scaled_prices) - forecast_horizon):
        X.append(scaled_prices[i-lookback:i, 0])
        y.append(scaled_prices[i:i+forecast_horizon, 0])
    
    X, y = np.array(X), np.array(y)
    
    # Split into train and test sets
    train_size = int(len(X) * (1 - test_size))
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    return {
        'X_train': X_train, 'y_train': y_train,
        'X_test': X_test, 'y_test': y_test,
        'scaler': scaler, 'latest_sequence': scaled_prices[-lookback:, 0]
    }

def train_linear_regression(X_train, y_train):
    """
    Train a simple linear regression model
    
    Args:
        X_train (numpy.ndarray): Training features
        y_train (numpy.ndarray): Training targets
        
    Returns:
        LinearRegression: Trained model
    """
    model = LinearRegression()
    # Reshape for sklearn compatibility
    model.fit(X_train, y_train)
    return model

def train_random_forest(X_train, y_train):
    """
    Train a random forest regression model
    
    Args:
        X_train (numpy.ndarray): Training features
        y_train (numpy.ndarray): Training targets
        
    Returns:
        RandomForestRegressor: Trained model
    """
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

def train_svr(X_train, y_train):
    """
    Train an SVR model
    
    Args:
        X_train (numpy.ndarray): Training features
        y_train (numpy.ndarray): Training targets
        
    Returns:
        SVR: Trained model
    """
    model = SVR(kernel='rbf', C=100, gamma=0.1, epsilon=0.1)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """
    Evaluate the model performance
    
    Args:
        model: Trained prediction model
        X_test (numpy.ndarray): Test features
        y_test (numpy.ndarray): Test targets
        
    Returns:
        dict: Dictionary with evaluation metrics
    """
    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    return {
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'predictions': predictions
    }

def predict_future_prices(model, latest_data, scaler, forecast_horizon=5):
    """
    Predict future prices
    
    Args:
        model: Trained prediction model
        latest_data: The most recent data points (scaled)
        scaler: The scaler used to transform the data
        forecast_horizon: Number of days to forecast
    
    Returns:
        list: Predicted prices (unscaled)
    """
    # Reshape for prediction
    latest_data_reshaped = latest_data.reshape(1, -1)
    
    # Make prediction
    scaled_prediction = model.predict(latest_data_reshaped)[0]
    
    # Inverse transform to get actual prices
    pred_array = scaled_prediction.reshape(-1, 1)
    prediction = scaler.inverse_transform(pred_array)
    
    return prediction.flatten()
