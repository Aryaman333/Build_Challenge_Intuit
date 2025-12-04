"""Data loading and preprocessing utilities for Amazon Products Sales Analysis."""

import pandas as pd
import numpy as np
from pathlib import Path


def load_data(file_path=None):
    """Load the Amazon products sales data."""
    if file_path is None:
        file_path = Path(__file__).parent.parent / 'data' / 'cleaned' / 'amazon_products_sales_data_cleaned.csv'
    
    df = pd.read_csv(file_path)
    df['data_collected_at'] = pd.to_datetime(df['data_collected_at'])
    if 'delivery_date' in df.columns:
        df['delivery_date'] = pd.to_datetime(df['delivery_date'], errors='coerce')
    
    return df


def get_summary_stats(df):
    """Get summary statistics for the dataset."""
    return {
        'total_products': len(df),
        'total_categories': df['product_category'].nunique(),
        'avg_rating': df['product_rating'].mean(),
        'median_price': df['discounted_price'].median(),
        'avg_discount': df['discount_percentage'].mean(),
        'total_reviews': df['total_reviews'].sum(),
        'best_sellers': (df['is_best_seller'] == 'Best Seller').sum(),
        'sponsored_products': (df['is_sponsored'] == 'Sponsored').sum()
    }


def filter_by_category(df, category):
    """Filter dataframe by product category."""
    return df[df['product_category'] == category]


def filter_by_price_range(df, min_price, max_price):
    """Filter dataframe by price range."""
    return df[(df['discounted_price'] >= min_price) & (df['discounted_price'] <= max_price)]


def filter_by_rating(df, min_rating):
    """Filter dataframe by minimum rating."""
    return df[df['product_rating'] >= min_rating]


def get_top_products(df, by='product_rating', n=10, category=None):
    """Get top N products based on specified metric."""
    if category:
        df = filter_by_category(df, category)
    return df.nlargest(n, by)[['product_title', 'product_rating', 'total_reviews', 
                                 'discounted_price', 'product_category']]


def get_category_summary(df):
    """Get summary statistics by category."""
    return df.groupby('product_category').agg({
        'product_rating': 'mean',
        'total_reviews': 'sum',
        'purchased_last_month': 'sum',
        'discounted_price': 'mean',
        'discount_percentage': 'mean',
        'product_title': 'count'
    }).rename(columns={'product_title': 'product_count'}).round(2)


def get_missing_value_summary(df):
    """Get summary of missing values."""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    return pd.DataFrame({
        'missing_count': missing,
        'missing_percentage': missing_pct
    }).sort_values('missing_count', ascending=False)


def clean_numeric_columns(df):
    """Ensure numeric columns are properly formatted."""
    numeric_cols = ['product_rating', 'total_reviews', 'purchased_last_month',
                   'discounted_price', 'original_price', 'discount_percentage']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df
