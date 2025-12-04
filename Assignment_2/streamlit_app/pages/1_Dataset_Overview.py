"""Dataset Overview Page - Comprehensive data statistics and quality analysis."""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from data_loader import load_data, get_summary_stats, get_category_summary, get_missing_value_summary
from visualization import plot_pie, create_summary_table

st.set_page_config(page_title="Dataset Overview", page_icon=":bar_chart:", layout="wide")

st.title("Dataset Overview")
st.markdown("Complete statistics and data quality analysis")

# Load data
@st.cache_data
def load_dataset():
    return load_data()

df = load_dataset()

# Tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["Statistics", "Data Quality", "Categories", "Distributions"])

with tab1:
    st.header("Dataset Statistics")
    
    stats = get_summary_stats(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("General Statistics")
        general_stats = {
            'Total Products': f"{stats['total_products']:,}",
            'Total Categories': stats['total_categories'],
            'Total Reviews': f"{stats['total_reviews']:,.0f}",
            'Data Collection Date': df['data_collected_at'].min().strftime('%Y-%m-%d')
        }
        st.table(create_summary_table(general_stats))
    
    with col2:
        st.subheader("Product Metrics")
        product_stats = {
            'Average Rating': f"{stats['avg_rating']:.2f}",
            'Median Price': f"${stats['median_price']:.2f}",
            'Average Discount': f"{stats['avg_discount']:.1f}%",
            'Best Sellers': f"{stats['best_sellers']:,}"
        }
        st.table(create_summary_table(product_stats))
    
    st.markdown("---")
    
    # Numeric columns summary
    st.subheader("Numeric Features Summary")
    numeric_cols = ['product_rating', 'total_reviews', 'purchased_last_month',
                   'discounted_price', 'original_price', 'discount_percentage']
    st.dataframe(df[numeric_cols].describe().T, use_container_width=True)

with tab2:
    st.header("Data Quality Analysis")
    
    # Missing values
    st.subheader("Missing Values Analysis")
    missing_df = get_missing_value_summary(df)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.dataframe(missing_df, use_container_width=True)
    
    with col2:
        st.metric("Total Missing Values", f"{missing_df['missing_count'].sum():,}")
        st.metric("Columns with Missing Data", f"{(missing_df['missing_count'] > 0).sum()}")
    
    # Visualize missing values
    fig = px.bar(missing_df[missing_df['missing_count'] > 0].reset_index(),
                 x='index', y='missing_percentage',
                 title='Missing Values Percentage by Column',
                 labels={'index': 'Column', 'missing_percentage': 'Missing %'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Data types
    st.subheader("Data Types")
    dtype_df = pd.DataFrame({
        'Column': df.dtypes.index,
        'Data Type': df.dtypes.values.astype(str),
        'Non-Null Count': df.count().values,
        'Unique Values': [df[col].nunique() for col in df.columns]
    })
    st.dataframe(dtype_df, use_container_width=True, hide_index=True)

with tab3:
    st.header("Category Analysis")
    
    category_summary = get_category_summary(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Product Count by Category")
        fig = px.bar(category_summary.reset_index(),
                     x='product_category', y='product_count',
                     title='Products per Category',
                     labels={'product_count': 'Number of Products', 'product_category': 'Category'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Category Distribution")
        fig = plot_pie(df, 'product_category', 'Product Categories Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Category Performance Metrics")
    st.dataframe(category_summary, use_container_width=True)

with tab4:
    st.header("Feature Distributions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Rating Distribution")
        fig = px.histogram(df, x='product_rating', nbins=50,
                          title='Product Rating Distribution',
                          labels={'product_rating': 'Rating'})
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Price Distribution")
        fig = px.histogram(df, x='discounted_price', nbins=50,
                          title='Price Distribution',
                          labels={'discounted_price': 'Price (USD)'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Discount Distribution")
        fig = px.histogram(df, x='discount_percentage', nbins=50,
                          title='Discount Percentage Distribution',
                          labels={'discount_percentage': 'Discount %'})
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Reviews Distribution")
        fig = px.histogram(df[df['total_reviews'] < df['total_reviews'].quantile(0.95)],
                          x='total_reviews', nbins=50,
                          title='Review Count Distribution (95th percentile)',
                          labels={'total_reviews': 'Number of Reviews'})
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.info("Tip: Use the tabs above to explore different aspects of the dataset.")
