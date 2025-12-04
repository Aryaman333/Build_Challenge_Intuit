"""Visualization utilities for Amazon Products Sales Analysis."""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


def plot_distribution(data, column, title=None, bins=30, color='steelblue'):
    """Plot distribution of a numeric column."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(data[column].dropna(), bins=bins, color=color, edgecolor='black', alpha=0.7)
    ax.set_xlabel(column.replace('_', ' ').title())
    ax.set_ylabel('Frequency')
    ax.set_title(title or f'Distribution of {column.replace("_", " ").title()}')
    ax.grid(axis='y', alpha=0.3)
    return fig


def plot_category_bar(data, category_col='product_category', value_col='product_rating', agg='mean'):
    """Plot bar chart for category comparison."""
    if agg == 'mean':
        summary = data.groupby(category_col)[value_col].mean().sort_values(ascending=False)
    elif agg == 'sum':
        summary = data.groupby(category_col)[value_col].sum().sort_values(ascending=False)
    elif agg == 'count':
        summary = data.groupby(category_col)[value_col].count().sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    summary.plot(kind='bar', ax=ax, color='teal', edgecolor='black')
    ax.set_xlabel(category_col.replace('_', ' ').title())
    ax.set_ylabel(f'{agg.title()} of {value_col.replace("_", " ").title()}')
    ax.set_title(f'{value_col.replace("_", " ").title()} by {category_col.replace("_", " ").title()} ({agg})')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    return fig


def plot_correlation_heatmap(data, numeric_cols=None):
    """Plot correlation heatmap."""
    if numeric_cols is None:
        numeric_cols = data.select_dtypes(include=[np.number]).columns
    
    correlation = data[numeric_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, linewidths=1, ax=ax)
    ax.set_title('Correlation Heatmap')
    plt.tight_layout()
    return fig


def plot_scatter(data, x_col, y_col, color_col=None, title=None):
    """Plot scatter plot."""
    fig = px.scatter(data, x=x_col, y=y_col, color=color_col,
                     title=title or f'{y_col} vs {x_col}',
                     labels={x_col: x_col.replace('_', ' ').title(),
                            y_col: y_col.replace('_', ' ').title()},
                     hover_data=['product_title'] if 'product_title' in data.columns else None)
    return fig


def plot_box(data, category_col, value_col, title=None):
    """Plot box plot for category comparison."""
    fig = px.box(data, x=category_col, y=value_col,
                 title=title or f'{value_col.replace("_", " ").title()} by {category_col.replace("_", " ").title()}',
                 labels={category_col: category_col.replace('_', ' ').title(),
                        value_col: value_col.replace('_', ' ').title()})
    return fig


def plot_pie(data, column, title=None, top_n=10):
    """Plot pie chart."""
    value_counts = data[column].value_counts().head(top_n)
    
    fig = go.Figure(data=[go.Pie(labels=value_counts.index, values=value_counts.values)])
    fig.update_layout(title=title or f'Distribution of {column.replace("_", " ").title()}')
    return fig


def plot_price_rating_scatter(data, category=None):
    """Plot price vs rating scatter with trend line."""
    if category:
        data = data[data['product_category'] == category]
    
    fig = px.scatter(data, x='discounted_price', y='product_rating',
                     color='product_category', size='total_reviews',
                     hover_data=['product_title'],
                     title='Price vs Rating Analysis',
                     labels={'discounted_price': 'Price (USD)',
                            'product_rating': 'Rating (1-5)'},
                     trendline='ols')
    return fig


def plot_top_products(data, n=10, by='product_rating'):
    """Plot top N products."""
    top = data.nlargest(n, by)[['product_title', by]].set_index('product_title')
    
    fig, ax = plt.subplots(figsize=(12, 8))
    top[by].plot(kind='barh', ax=ax, color='coral', edgecolor='black')
    ax.set_xlabel(by.replace('_', ' ').title())
    ax.set_ylabel('Product')
    ax.set_title(f'Top {n} Products by {by.replace("_", " ").title()}')
    ax.invert_yaxis()
    plt.tight_layout()
    return fig


def plot_discount_impact(data):
    """Plot discount percentage impact on purchases."""
    fig = px.scatter(data, x='discount_percentage', y='purchased_last_month',
                     color='product_category',
                     title='Discount Impact on Purchase Volume',
                     labels={'discount_percentage': 'Discount (%)',
                            'purchased_last_month': 'Purchases Last Month'},
                     hover_data=['product_title', 'discounted_price'])
    return fig


def create_summary_table(summary_dict):
    """Create formatted summary table."""
    df = pd.DataFrame(list(summary_dict.items()), columns=['Metric', 'Value'])
    df = df.set_index('Metric')
    return df
