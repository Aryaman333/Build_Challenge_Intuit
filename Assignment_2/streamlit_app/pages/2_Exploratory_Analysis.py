"""Exploratory Analysis Page - Interactive filtering and visualization."""

import streamlit as st
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from data_loader import load_data, filter_by_category, filter_by_price_range, filter_by_rating

st.set_page_config(page_title="Exploratory Analysis", page_icon=":chart_with_upwards_trend:", layout="wide")

st.title("Exploratory Data Analysis")
st.markdown("Interactive filtering and dynamic visualizations")

# Load data
@st.cache_data
def load_dataset():
    return load_data()

df = load_dataset()

# Sidebar filters
st.sidebar.header("Filters")

# Category filter
categories = ['All'] + sorted(df['product_category'].unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", categories)

# Price range filter
price_range = st.sidebar.slider(
    "Price Range (USD)",
    float(df['discounted_price'].min()),
    float(df['discounted_price'].quantile(0.95)),
    (float(df['discounted_price'].min()), float(df['discounted_price'].quantile(0.95)))
)

# Rating filter
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.1)

# Apply filters
filtered_df = df.copy()

if selected_category != 'All':
    filtered_df = filter_by_category(filtered_df, selected_category)

filtered_df = filter_by_price_range(filtered_df, price_range[0], price_range[1])
filtered_df = filter_by_rating(filtered_df, min_rating)

# Display filter results
st.sidebar.markdown("---")
st.sidebar.metric("Filtered Products", f"{len(filtered_df):,}")
st.sidebar.metric("Original Products", f"{len(df):,}")

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Products Shown", f"{len(filtered_df):,}")

with col2:
    st.metric("Avg Rating", f"{filtered_df['product_rating'].mean():.2f}")

with col3:
    st.metric("Avg Price", f"${filtered_df['discounted_price'].mean():.2f}")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Distributions", "Correlations", "Trends", "Comparisons"])

with tab1:
    st.header("Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rating distribution
        fig = px.histogram(filtered_df, x='product_rating',
                          title='Rating Distribution',
                          labels={'product_rating': 'Rating'},
                          color_discrete_sequence=['#FF9900'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Discount distribution
        fig = px.histogram(filtered_df, x='discount_percentage',
                          title='Discount Percentage Distribution',
                          labels={'discount_percentage': 'Discount %'},
                          color_discrete_sequence=['#146EB4'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Price distribution
        fig = px.histogram(filtered_df, x='discounted_price',
                          title='Price Distribution',
                          labels={'discounted_price': 'Price (USD)'},
                          color_discrete_sequence=['#232F3E'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Reviews distribution
        fig = px.histogram(filtered_df[filtered_df['total_reviews'] < filtered_df['total_reviews'].quantile(0.95)],
                          x='total_reviews',
                          title='Review Count Distribution',
                          labels={'total_reviews': 'Number of Reviews'},
                          color_discrete_sequence=['#00A8E1'])
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Correlation Analysis")
    
    # Correlation heatmap
    numeric_cols = ['product_rating', 'total_reviews', 'purchased_last_month',
                   'discounted_price', 'original_price', 'discount_percentage']
    
    corr_matrix = filtered_df[numeric_cols].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    fig.update_layout(title='Correlation Heatmap', height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # Scatter plots
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.scatter(filtered_df, x='discounted_price', y='product_rating',
                        color='product_category',
                        title='Price vs Rating',
                        labels={'discounted_price': 'Price (USD)', 'product_rating': 'Rating'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(filtered_df, x='total_reviews', y='purchased_last_month',
                        color='product_category',
                        title='Reviews vs Purchase Volume',
                        labels={'total_reviews': 'Total Reviews', 'purchased_last_month': 'Purchases Last Month'})
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Trend Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price vs Discount
        fig = px.scatter(filtered_df, x='discount_percentage', y='discounted_price',
                        color='product_rating',
                        title='Discount % vs Final Price',
                        labels={'discount_percentage': 'Discount %', 'discounted_price': 'Price (USD)'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Rating vs Reviews
        fig = px.scatter(filtered_df, x='product_rating', y='total_reviews',
                        color='product_category',
                        title='Rating vs Review Count',
                        labels={'product_rating': 'Rating', 'total_reviews': 'Total Reviews'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Purchases vs Rating
        fig = px.scatter(filtered_df, x='product_rating', y='purchased_last_month',
                        color='discount_percentage',
                        title='Rating vs Purchase Volume',
                        labels={'product_rating': 'Rating', 'purchased_last_month': 'Purchases Last Month'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Discount impact on purchases
        fig = px.scatter(filtered_df, x='discount_percentage', y='purchased_last_month',
                        color='product_category',
                        title='Discount Impact on Purchases',
                        labels={'discount_percentage': 'Discount %', 'purchased_last_month': 'Purchases Last Month'})
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Category Comparisons")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Box plot for ratings by category
        fig = px.box(filtered_df, x='product_category', y='product_rating',
                    title='Rating Distribution by Category',
                    labels={'product_category': 'Category', 'product_rating': 'Rating'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Box plot for price by category
        fig = px.box(filtered_df, x='product_category', y='discounted_price',
                    title='Price Distribution by Category',
                    labels={'product_category': 'Category', 'discounted_price': 'Price (USD)'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Violin plot for discounts
        fig = px.violin(filtered_df, x='product_category', y='discount_percentage',
                       title='Discount Distribution by Category',
                       labels={'product_category': 'Category', 'discount_percentage': 'Discount %'},
                       box=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # Sponsored vs Organic comparison
        fig = px.histogram(filtered_df, x='product_category', color='is_sponsored',
                          title='Sponsored vs Organic by Category',
                          labels={'product_category': 'Category'},
                          barmode='group')
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.info("Tip: Use the sidebar filters to narrow down your analysis and explore specific segments.")
