"""
Streamlined unit tests for Amazon Products Sales Analysis.
Tests cover critical functionality, edge cases, and data quality.
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import warnings

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from data_loader import (
    load_data, get_summary_stats, filter_by_category,
    filter_by_price_range, filter_by_rating, get_top_products,
    get_category_summary, clean_numeric_columns, get_missing_value_summary
)
from visualization import (
    plot_distribution, plot_category_bar, plot_correlation_heatmap,
    create_summary_table
)


class TestDataLoadingAndQuality(unittest.TestCase):
    """Test data loading, structure, types, and quality constraints."""
    
    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.df = load_data()
        if not isinstance(cls.df, pd.DataFrame):
            raise TypeError("Data should be a DataFrame")
        if len(cls.df) == 0:
            raise ValueError("Dataset should not be empty")
    
    def test_data_structure_and_types(self):
        """Test data structure, required columns, and data types."""
        # Check required columns
        required_cols = ['product_title', 'product_rating', 'discounted_price', 
                        'product_category', 'total_reviews']
        for col in required_cols:
            self.assertIn(col, self.df.columns, f"Missing column: {col}")
        
        # Check data types
        self.assertTrue(pd.api.types.is_numeric_dtype(self.df['product_rating']))
        self.assertTrue(pd.api.types.is_numeric_dtype(self.df['discounted_price']))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.df['data_collected_at']))
    
    def test_load_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        with self.assertRaises(FileNotFoundError):
            load_data('nonexistent_file.csv')
    
    def test_data_validity_and_constraints(self):
        """Test data validity: ratings, discounts, prices, and consistency."""
        # Check rating range [0, 5]
        valid_ratings = self.df['product_rating'].dropna()
        self.assertTrue(all((valid_ratings >= 0) & (valid_ratings <= 5)),
                    "Ratings should be between 0 and 5")
        
        # Check discount percentage [0, 100]
        valid_discounts = self.df['discount_percentage'].dropna()
        self.assertTrue(all((valid_discounts >= 0) & (valid_discounts <= 100)),
                    "Discounts should be between 0% and 100%")
        
        # Check price consistency
        price_data = self.df[['discounted_price', 'original_price']].dropna()
        inconsistent = price_data[price_data['discounted_price'] > price_data['original_price']]
        self.assertEqual(len(inconsistent), 0,
                        f"Found {len(inconsistent)} products with discounted price > original price")
        
        # Check positive prices
        for col in ['discounted_price', 'original_price']:
            if col in self.df.columns:
                valid_prices = self.df[col].dropna()
                self.assertTrue(all(valid_prices > 0), f"{col} should be positive")
        
        # Check no infinite values
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            self.assertFalse(np.isinf(self.df[col]).any(), f"{col} contains infinite values")

class TestSummaryAndAggregation(unittest.TestCase):
    """Test summary statistics and aggregation operations."""
    
    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.df = load_data()
    
    def test_summary_stats_normal_and_edge_cases(self):
        """Test summary statistics with normal data, empty DataFrame, and nulls."""
        # Normal case
        stats = get_summary_stats(self.df)
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['total_products'], len(self.df))
        self.assertGreater(stats['avg_rating'], 0)
        self.assertLessEqual(stats['avg_rating'], 5)
        
        # Empty DataFrame
        empty_df = pd.DataFrame(columns=self.df.columns)
        empty_stats = get_summary_stats(empty_df)
        self.assertEqual(empty_stats['total_products'], 0)
        
        # With nulls
        df_with_nulls = self.df.copy()
        df_with_nulls.loc[:10, 'product_rating'] = np.nan
        null_stats = get_summary_stats(df_with_nulls)
        self.assertIsInstance(null_stats, dict)
    
    def test_missing_value_summary(self):
        """Test missing value summary computation."""
        missing_summary = get_missing_value_summary(self.df)
        
        self.assertIsInstance(missing_summary, pd.DataFrame)
        self.assertIn('missing_count', missing_summary.columns)
        self.assertIn('missing_percentage', missing_summary.columns)
        self.assertEqual(len(missing_summary), len(self.df.columns))
    
    def test_category_aggregation_all_cases(self):
        """Test category aggregation with normal, empty, and single category cases."""
        # Normal case
        summary = get_category_summary(self.df)
        self.assertIsInstance(summary, pd.DataFrame)
        self.assertIn('product_count', summary.columns)
        self.assertTrue(all(summary['product_count'] > 0))
        
        # Empty DataFrame
        empty_df = pd.DataFrame(columns=self.df.columns)
        empty_summary = get_category_summary(empty_df)
        self.assertEqual(len(empty_summary), 0)
        
        # Single category
        single_cat_df = self.df[self.df['product_category'] == self.df['product_category'].iloc[0]]
        single_summary = get_category_summary(single_cat_df)
        self.assertEqual(len(single_summary), 1)


class TestFilteringOperations(unittest.TestCase):
    """Test filtering functions with normal and edge cases."""
    
    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.df = load_data()
    
    def test_category_filter_all_cases(self):
        """Test category filtering: valid, nonexistent, and null categories."""
        # Valid category
        categories = self.df['product_category'].unique()
        if len(categories) > 0:
            test_category = categories[0]
            filtered = filter_by_category(self.df, test_category)
            self.assertTrue(all(filtered['product_category'] == test_category))
            self.assertGreater(len(filtered), 0)
        
        # Nonexistent category
        filtered = filter_by_category(self.df, 'NonexistentCategory123')
        self.assertEqual(len(filtered), 0)
        
        # Null category
        filtered = filter_by_category(self.df, None)
        self.assertIsInstance(filtered, pd.DataFrame)
    
    def test_price_range_filter_all_cases(self):
        """Test price filtering: valid, invalid, negative, and extreme ranges."""
        # Valid range
        filtered = filter_by_price_range(self.df, 50, 200)
        self.assertTrue(all(filtered['discounted_price'] >= 50))
        self.assertTrue(all(filtered['discounted_price'] <= 200))
        
        # Invalid range (min > max)
        filtered = filter_by_price_range(self.df, 200, 50)
        self.assertEqual(len(filtered), 0)
        
        # Negative prices
        filtered = filter_by_price_range(self.df, -100, -10)
        self.assertEqual(len(filtered), 0)
        
        # Extreme range
        filtered = filter_by_price_range(self.df, 0, 1000000)
        self.assertGreater(len(filtered), 0)
    
    def test_rating_filter_all_cases(self):
        """Test rating filtering: valid, boundary, and edge cases."""
        # Valid rating
        filtered = filter_by_rating(self.df, 4.5)
        self.assertTrue(all(filtered['product_rating'] >= 4.5))
        
        # Boundary: 0 (should include all)
        filtered_0 = filter_by_rating(self.df, 0)
        self.assertGreater(len(filtered_0), 0)
        
        # Boundary: 5 (only perfect ratings)
        filtered_5 = filter_by_rating(self.df, 5)
        if len(filtered_5) > 0:
            self.assertTrue(all(filtered_5['product_rating'] == 5))
        
        # Above max rating
        filtered_high = filter_by_rating(self.df, 5.5)
        self.assertEqual(len(filtered_high), 0)
        
        # Negative rating (should return non-null ratings)
        filtered_neg = filter_by_rating(self.df, -1)
        self.assertGreater(len(filtered_neg), 0)


class TestTopProductsRetrieval(unittest.TestCase):
    """Test top products retrieval with various scenarios."""
    
    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.df = load_data()
    
    def test_top_products_all_scenarios(self):
        """Test top products with valid, zero, negative, and excessive n values."""
        # Normal case
        top = get_top_products(self.df, by='product_rating', n=5)
        self.assertLessEqual(len(top), 5)
        if len(top) > 1:
            ratings = top['product_rating'].tolist()
            self.assertEqual(ratings, sorted(ratings, reverse=True))
        
        # With category filter
        category = self.df['product_category'].iloc[0]
        top_cat = get_top_products(self.df, by='product_rating', n=5, category=category)
        self.assertTrue(all(top_cat['product_category'] == category))
        
        # n=0
        top_zero = get_top_products(self.df, by='product_rating', n=0)
        self.assertEqual(len(top_zero), 0)
        
        # n > total
        top_large = get_top_products(self.df, by='product_rating', n=len(self.df) + 100)
        self.assertEqual(len(top_large), len(self.df))
        
        # Negative n
        top_neg = get_top_products(self.df, by='product_rating', n=-5)
        self.assertLessEqual(len(top_neg), 0)
    
    def test_top_products_multiple_metrics(self):
        """Test top products by different sorting metrics."""
        metrics = ['product_rating', 'total_reviews', 'discounted_price']
        
        for metric in metrics:
            if metric in self.df.columns:
                top = get_top_products(self.df, by=metric, n=5)
                self.assertLessEqual(len(top), 5)
                if len(top) > 0:
                    self.assertIn(metric, top.columns)
                    values = top[metric].dropna().tolist()
                    if len(values) > 1:
                        self.assertEqual(values, sorted(values, reverse=True))
    
    def test_top_products_invalid_column(self):
        """Test top products with invalid sorting column."""
        with self.assertRaises(KeyError):
            get_top_products(self.df, by='nonexistent_column', n=5)


class TestDataCleaning(unittest.TestCase):
    """Test data cleaning and transformation functions."""
    
    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.df = load_data()
    
    def test_clean_numeric_columns_all_cases(self):
        """Test cleaning with valid, string numbers, and invalid values."""
        # Normal cleaning
        cleaned = clean_numeric_columns(self.df.copy())
        numeric_cols = ['product_rating', 'total_reviews', 'discounted_price']
        for col in numeric_cols:
            if col in cleaned.columns:
                self.assertTrue(pd.api.types.is_numeric_dtype(cleaned[col]))
        
        # With string numbers
        dirty_df = self.df.copy()
        dirty_df.loc[0, 'product_rating'] = '4.5'
        dirty_df.loc[1, 'total_reviews'] = '100'
        cleaned = clean_numeric_columns(dirty_df)
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned['product_rating']))
        
        # With invalid values
        dirty_df = self.df.copy()
        dirty_df.loc[0, 'product_rating'] = 'invalid'
        dirty_df.loc[1, 'discounted_price'] = 'N/A'
        cleaned = clean_numeric_columns(dirty_df)
        self.assertTrue(pd.isna(cleaned.loc[0, 'product_rating']))
        self.assertTrue(pd.isna(cleaned.loc[1, 'discounted_price']))


class TestFunctionalOperations(unittest.TestCase):
    """Test functional programming operations (map, filter, reduce)."""
    
    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.df = load_data()
    
    def test_lambda_transformations(self):
        """Test lambda-based transformations with normal and null data."""
        # Normal transformation
        result = self.df.assign(
            value_score=lambda x: x['product_rating'] * np.log1p(x['total_reviews'].fillna(0))
        )
        self.assertIn('value_score', result.columns)
        valid_scores = result['value_score'].dropna()
        if len(valid_scores) > 0:
            self.assertTrue(all(valid_scores >= 0))
        
        # With nulls
        df_with_nulls = self.df.copy()
        df_with_nulls.loc[:10, 'product_rating'] = np.nan
        result = df_with_nulls.assign(
            value_score=lambda x: x['product_rating'] * np.log1p(x['total_reviews'].fillna(0))
        )
        self.assertIn('value_score', result.columns)
    
    def test_chained_filtering(self):
        """Test method chaining with valid and empty results."""
        # Valid chain
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
        
        # Empty result chain
        result = (
            self.df
            .query('product_rating >= 5.5')  # Impossible
            .head(10)
        )
        self.assertEqual(len(result), 0)
    
    def test_aggregation_operations(self):
        """Test groupBy, custom aggregators, and reduce operations."""
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
        
        # Custom lambda aggregator
        result = (
            self.df
            .groupby('product_category')
            .agg({
                'product_rating': lambda x: (x >= 4.5).sum(),
                'discounted_price': lambda x: x.quantile(0.75)
            })
        )
        self.assertTrue(all(result['product_rating'] >= 0))
        
        # Reduce operation
        from functools import reduce
        category_discounts = self.df.groupby('product_category')['discount_percentage'].apply(list).to_dict()
        
        def discount_reducer(acc, item):
            category, discounts = item
            valid = [d for d in discounts if pd.notna(d) and d > 0]
            if valid:
                acc[category] = {'count': len(valid), 'avg': np.mean(valid)}
            return acc
        
        result = reduce(discount_reducer, category_discounts.items(), {})
        self.assertIsInstance(result, dict)
        for stats in result.values():
            self.assertGreater(stats['count'], 0)


class TestVisualization(unittest.TestCase):
    """Test visualization functions and edge cases."""
    
    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.df = load_data()
    
    def test_summary_table_creation(self):
        """Test summary table with normal and empty data."""
        # Normal case
        summary_dict = {'Total Products': 1000, 'Avg Rating': 4.5}
        table = create_summary_table(summary_dict)
        self.assertIsInstance(table, pd.DataFrame)
        self.assertEqual(len(table), 2)
        
        # Empty case
        table = create_summary_table({})
        self.assertEqual(len(table), 0)
    
    def test_plot_functions(self):
        """Test various plot creation functions."""
        # Distribution plot
        fig = plot_distribution(self.df, 'product_rating')
        self.assertIsNotNone(fig)
        
        # Distribution with nulls
        df_nulls = self.df.copy()
        df_nulls.loc[:100, 'product_rating'] = np.nan
        fig = plot_distribution(df_nulls, 'product_rating')
        self.assertIsNotNone(fig)
        
        # Category bar plot
        fig = plot_category_bar(self.df)
        self.assertIsNotNone(fig)
        
        # Correlation heatmap
        fig = plot_correlation_heatmap(self.df)
        self.assertIsNotNone(fig)
        
        # Minimal data
        minimal_df = self.df.head(1)
        fig = plot_distribution(minimal_df, 'product_rating')
        self.assertIsNotNone(fig)


class TestPerformance(unittest.TestCase):
    """Test performance of operations on large datasets."""
    
    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.df = load_data()
    
    def test_operation_performance(self):
        """Test that key operations complete efficiently."""
        import time
        
        # Filter operation
        start = time.time()
        filter_by_price_range(self.df, 0, 1000)
        filter_time = time.time() - start
        self.assertLess(filter_time, 1.0, "Filter should complete in < 1 second")
        
        # Aggregation operation
        start = time.time()
        get_category_summary(self.df)
        agg_time = time.time() - start
        self.assertLess(agg_time, 2.0, "Aggregation should complete in < 2 seconds")


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)
