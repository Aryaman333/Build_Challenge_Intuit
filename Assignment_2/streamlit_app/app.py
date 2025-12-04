"""Amazon Products Sales Data Analysis - Interactive Dashboard

Main Streamlit Application
"""

import streamlit as st
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from data_loader import load_data, get_summary_stats

# Page configuration
st.set_page_config(
    page_title="Amazon Products Sales Analysis",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #FF9900;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #232F3E;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF9900;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">Amazon Products Sales Analysis</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Interactive Data Exploration and Insights Dashboard</p>', unsafe_allow_html=True)

# Load data
@st.cache_data
def load_dataset():
    return load_data()

try:
    df = load_dataset()
    stats = get_summary_stats(df)
    
    # Welcome section
    st.markdown("---")
    st.markdown("### Welcome to the Analysis Dashboard")
    st.markdown("""
    This interactive dashboard provides comprehensive insights into Amazon products sales data.
    Explore pricing strategies, product performance, and market trends through interactive visualizations.
    
    **Use the sidebar** to navigate between different analysis sections.
    """)
    
    # Key metrics
    st.markdown("---")
    st.markdown("### Key Metrics Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Products",
            value=f"{stats['total_products']:,}",
            help="Total number of products in the dataset"
        )
    
    with col2:
        st.metric(
            label="Categories",
            value=stats['total_categories'],
            help="Number of unique product categories"
        )
    
    with col3:
        st.metric(
            label="Average Rating",
            value=f"{stats['avg_rating']:.2f}",
            help="Average product rating across all products"
        )
    
    with col4:
        st.metric(
            label="Median Price",
            value=f"${stats['median_price']:.2f}",
            help="Median discounted price"
        )
    
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            label="Best Sellers",
            value=f"{stats['best_sellers']:,}",
            help="Number of products with Best Seller badge"
        )
    
    with col6:
        st.metric(
            label="Sponsored Products",
            value=f"{stats['sponsored_products']:,}",
            help="Number of sponsored product listings"
        )
    
    with col7:
        st.metric(
            label="Avg Discount",
            value=f"{stats['avg_discount']:.1f}%",
            help="Average discount percentage"
        )
    
    with col8:
        st.metric(
            label="Total Reviews",
            value=f"{stats['total_reviews']:,.0f}",
            help="Total number of customer reviews"
        )
    
    # Quick insights
    st.markdown("---")
    st.markdown("### Quick Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Sponsored vs Organic**
        - {stats['sponsored_products']:,} sponsored products ({stats['sponsored_products']/stats['total_products']*100:.1f}%)
        - {stats['total_products'] - stats['sponsored_products']:,} organic products
        """)
    
    with col2:
        st.success(f"""
        **Best Seller Rate**
        - {stats['best_sellers']:,} products have Best Seller badge
        - That's {stats['best_sellers']/stats['total_products']*100:.1f}% of all products
        """)
    
    # Dataset sample
    st.markdown("---")
    st.markdown("### Dataset Sample")
    st.markdown("Preview of the first few products in the dataset:")
    
    display_cols = ['product_title', 'product_rating', 'total_reviews', 
                   'purchased_last_month', 'discounted_price', 'original_price',
                   'discount_percentage', 'product_category']
    
    st.dataframe(
        df[display_cols].head(10),
        use_container_width=True,
        hide_index=True
    )
    
    # Navigation guide
    st.markdown("---")
    st.markdown("### Navigation Guide")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Dataset Overview**
        - Complete dataset statistics
        - Data quality analysis
        - Missing value summary
        """)
    
    with col2:
        st.markdown("""
        **Exploratory Analysis**
        - Interactive filtering
        - Distribution visualizations
        - Correlation analysis
        """)
    
    with col3:
        st.markdown("""
        **Pricing Analysis**
        - Price distribution
        - Discount effectiveness
        - Price vs rating insights
        """)
    
    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown("""
        **Performance Metrics**
        - Top-rated products
        - High-volume sellers
        - Category comparisons
        """)
    
    with col5:
        st.markdown("""
        **Comparison Tools**
        - Multi-product comparison
        - Category benchmarking
        - Data export options
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p>Amazon Products Sales Data Analysis Dashboard</p>
        <p>Built with Streamlit • Data Analytics Assignment 2</p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please ensure the data file is in the correct location: `data/cleaned/amazon_products_sales_data_cleaned.csv`")
