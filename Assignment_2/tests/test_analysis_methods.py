"""
Unit tests for data analysis methods using functional programming and stream operations.
Tests cover data_loader.py, statistical_tests.py, and analysis functions.
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from data_loader import (
    load_data, get_summary_stats, filter_by_category,
    filter_by_price_range, filter_by_rating, get_top_products,
    get_category_summary, clean_numeric_columns
)


class TestDataLoader(unittest.TestCase):
    """Test data loading and filtering functions."""
    
    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.df = load_data()
        if not isinstance(cls.df, pd.DataFrame):
            raise TypeError("Data should be a DataFrame")
        if len(cls.df) == 0:
            raise ValueError("Dataset should not be empty")
    
    def test_load_data_structure(self):
        """Test that data loads with expected columns."""
        required_cols = ['product_title', 'product_rating', 'discounted_price', 
                        'product_category', 'total_reviews']
        for col in required_cols:
            self.assertIn(col, self.df.columns, f"Missing column: {col}")
    
    def test_get_summary_stats(self):
        """Test summary statistics generation."""
        stats = get_summary_stats(self.df)
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_products', stats)
        self.assertIn('avg_rating', stats)
        self.assertEqual(stats['total_products'], len(self.df))
        self.assertGreater(stats['avg_rating'], 0)
        self.assertLessEqual(stats['avg_rating'], 5)
    
    def test_filter_by_category(self):
        """Test category filtering using stream-like operations."""
        # Get a valid category
        categories = self.df['product_category'].unique()
        if len(categories) > 0:
            test_category = categories[0]
            filtered = filter_by_category(self.df, test_category)
            
            # Verify all results match category (stream filter operation)
            self.assertTrue(all(filtered['product_category'] == test_category))
            self.assertGreater(len(filtered), 0)
    
    def test_filter_by_price_range(self):
        """Test price range filtering (stream filter operation)."""
        min_price, max_price = 50, 200
        filtered = filter_by_price_range(self.df, min_price, max_price)
        
        # Verify filter conditions
        self.assertTrue(all(filtered['discounted_price'] >= min_price))
        self.assertTrue(all(filtered['discounted_price'] <= max_price))
    
    def test_filter_by_rating(self):
        """Test rating filtering (stream filter operation)."""
        min_rating = 4.5
        filtered = filter_by_rating(self.df, min_rating)
        
        # Verify filter with lambda-like condition
        self.assertTrue(all(filtered['product_rating'] >= min_rating))
    
    def test_get_top_products(self):
        """Test top products retrieval (stream limit operation)."""
        n = 5
        top_products = get_top_products(self.df, by='product_rating', n=n)
        
        self.assertLessEqual(len(top_products), n)
        if len(top_products) > 1:
            # Verify sorted order (stream sorted operation)
            ratings = top_products['product_rating'].tolist()
            self.assertEqual(ratings, sorted(ratings, reverse=True))
    
    def test_get_category_summary(self):
        """Test category aggregation (stream groupBy and aggregate)."""
        summary = get_category_summary(self.df)
        
        self.assertIsInstance(summary, pd.DataFrame)
        self.assertIn('product_count', summary.columns)
        self.assertIn('product_rating', summary.columns)
        
        # Verify aggregation results
        self.assertTrue(all(summary['product_count'] > 0))


class TestFunctionalOperations(unittest.TestCase):
    """Test functional programming operations used in notebooks."""
    
    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.df = load_data()
    
    def test_lambda_transformation(self):
        """Test lambda-based transformations (map operation)."""
        # Test creating computed column with lambda
        result = self.df.assign(
            value_score=lambda x: x['product_rating'] * np.log1p(x['total_reviews'].fillna(0))
        )
        
        self.assertIn('value_score', result.columns)
        self.assertEqual(len(result), len(self.df))
        # Value score can be NaN if rating is NaN, so check non-NaN values
        valid_scores = result['value_score'].dropna()
        if len(valid_scores) > 0:
            self.assertTrue(all(valid_scores >= 0))
    
    def test_chained_filtering(self):
        """Test method chaining for stream-like operations."""
        # Chain multiple filters (stream operations)
        result = (
            self.df
            .query('product_rating >= 4.0')
            .query('discounted_price >= 20')
            .sort_values('total_reviews', ascending=False)
            .head(10)
        )
        
        self.assertLessEqual(len(result), 10)
        if len(result) > 0:
            self.assertTrue(all(result['product_rating'] >= 4.0))
            self.assertTrue(all(result['discounted_price'] >= 20))
    
    def test_groupby_aggregation(self):
        """Test groupBy and aggregate operations (stream collect)."""
        # Multi-column aggregation
        result = (
            self.df
            .groupby('product_category')
            .agg({
                'product_rating': 'mean',
                'discounted_price': ['mean', 'median'],
                'product_title': 'count'
            })
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), self.df['product_category'].nunique())
    
    def test_custom_aggregator_with_lambda(self):
        """Test custom aggregation functions with lambda."""
        # Custom aggregator using lambda
        result = (
            self.df
            .groupby('product_category')
            .agg({
                'product_rating': lambda x: (x >= 4.5).sum(),  # Count high ratings
                'discounted_price': lambda x: x.quantile(0.75)  # 75th percentile
            })
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(all(result['product_rating'] >= 0))
    
    def test_reduce_operation(self):
        """Test reduce-like operation for data aggregation."""
        from functools import reduce
        
        # Get discount stats per category
        category_discounts = self.df.groupby('product_category')['discount_percentage'].apply(list).to_dict()
        
        # Reduce operation to calculate stats
        def discount_reducer(acc, item):
            category, discounts = item
            valid = [d for d in discounts if pd.notna(d) and d > 0]
            if valid:
                acc[category] = {'count': len(valid), 'avg': np.mean(valid)}
            return acc
        
        result = reduce(discount_reducer, category_discounts.items(), {})
        
        self.assertIsInstance(result, dict)
        for category, stats in result.items():
            self.assertIn('count', stats)
            self.assertIn('avg', stats)
            self.assertGreater(stats['count'], 0)
            self.assertGreater(stats['avg'], 0)


class TestDataQuality(unittest.TestCase):
    """Test data quality and validation."""
    
    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.df = load_data()
    
    def test_numeric_columns_validity(self):
        """Test that numeric columns contain valid values."""
        numeric_cols = ['product_rating', 'discounted_price', 'total_reviews', 'discount_percentage']
        
        for col in numeric_cols:
            if col in self.df.columns:
                valid_data = self.df[col].dropna()
                if len(valid_data) > 0:
                    self.assertTrue(all(valid_data >= 0), f"{col} should be non-negative")
    
    def test_clean_numeric_columns(self):
        """Test numeric column cleaning function."""
        cleaned = clean_numeric_columns(self.df.copy())
        
        numeric_cols = ['product_rating', 'total_reviews', 'discounted_price']
        for col in numeric_cols:
            if col in cleaned.columns:
                self.assertTrue(
                    pd.api.types.is_numeric_dtype(cleaned[col]),
                    f"{col} should be numeric"
                )


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)
