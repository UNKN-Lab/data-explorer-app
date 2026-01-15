import pandas as pd
import os

# Lấy đường dẫn tuyệt đối của thư mục chứa file này
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_BASE_DIR, "data")


def get_data():
    """
    Load processed data with climate groups.
    Returns DataFrame with cleaned/processed Walmart sales data including Climate_Group column.
    """
    # Ưu tiên file đã xử lý với climate
    processed_path = os.path.join(_DATA_DIR, "Walmart_Sales_processed_with_climate.csv")
    if os.path.exists(processed_path):
        df = pd.read_csv(processed_path)
    else:
        # Fallback to cleaned data
        cleaned_path = os.path.join(_DATA_DIR, "Walmart_Sales_cleaned.csv")
        if os.path.exists(cleaned_path):
            df = pd.read_csv(cleaned_path)
        else:
            # Last resort: raw data
            df = pd.read_csv(os.path.join(_DATA_DIR, "Walmart_Sales.csv"))
    
    # Parse Date column to datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    return df


def get_raw_data():
    """
    Load raw Walmart sales data (original unprocessed).
    Returns DataFrame with raw data.
    """
    raw_path = os.path.join(_DATA_DIR, "Walmart_Sales.csv")
    df = pd.read_csv(raw_path)
    
    # Parse Date column to datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    return df

