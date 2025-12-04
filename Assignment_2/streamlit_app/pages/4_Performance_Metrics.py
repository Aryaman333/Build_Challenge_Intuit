"""Performance Metrics Page - Analyze top products, ratings, and sales performance."""

import streamlit as st
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from data_loader import load_data, get_top_products

st.set_page_config(page_title="Performance Metrics", page_icon=":star:", layout="wide")

st.title("Performance Metrics & Rankings")
st.markdown("Discover top performers, analyze ratings, and identify high-volume sellers")

# Load data
@st.cache_data
def load_dataset():
    return load_data()

df = load_dataset()

# Sidebar
st.sidebar.header("Performance Filters")
category_filter = st.sidebar.selectbox("Category", ['All'] + sorted(df['product_category'].unique().tolist()))
metric_choice = st.sidebar.selectbox("Rank By", ['product_rating', 'total_reviews', 'purchased_last_month'])
top_n = st.sidebar.slider("Number of Products to Show", 5, 50, 10)

# Filter data
if category_filter != 'All':
    filtered_df = df[df['product_category'] == category_filter]
else:
    filtered_df = df.copy()

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Highest Rating", f"{filtered_df['product_rating'].max():.1f}")

with col2:
    most_reviewed = filtered_df['total_reviews'].max()
    st.metric("Most Reviews", f"{most_reviewed:,.0f}")

with col3:
    best_seller = filtered_df['purchased_last_month'].max()
    st.metric("Top Seller (Month)", f"{best_seller:,.0f} units")

with col4:
    best_sellers_count = (filtered_df['is_best_seller'] == 'Best Seller').sum()
    st.metric("Best Seller Badges", f"{best_sellers_count:,}")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Top Products", "Rating Analysis", "Sales Performance", "Best Sellers"])

with tab1:
    st.header(f"Top {top_n} Products by {metric_choice.replace('_', ' ').title()}")
    
    top_products = get_top_products(filtered_df, by=metric_choice, n=top_n)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.dataframe(top_products, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("Quick Stats")
        st.metric("Avg Rating", f"{top_products['product_rating'].mean():.2f}")
        st.metric("Avg Price", f"${top_products['discounted_price'].mean():.2f}")
        st.metric("Avg Reviews", f"{top_products['total_reviews'].mean():,.0f}")
    
    st.markdown("---")
    
    # Visualize top products
    top_viz = filtered_df.nlargest(top_n, metric_choice)
    
    fig = px.bar(top_viz, x=metric_choice, y='product_title',
                orientation='h',
                title=f'Top {top_n} Products by {metric_choice.replace("_", " ").title()}',
                labels={metric_choice: metric_choice.replace('_', ' ').title()},
                color=metric_choice,
                color_continuous_scale='Viridis')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=600)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Rating Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rating distribution
        fig = px.histogram(filtered_df, x='product_rating', nbins=50,
                          title='Rating Distribution',
                          labels={'product_rating': 'Rating'},
                          color_discrete_sequence=['#FF9900'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Rating by category
        fig = px.box(filtered_df, x='product_category', y='product_rating',
                    title='Rating Distribution by Category',
                    labels={'product_category': 'Category', 'product_rating': 'Rating'},
                    color='product_category')
        fig.update_layout(xaxis=dict(tickangle=45))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Rating vs Reviews
        fig = px.scatter(filtered_df, x='total_reviews', y='product_rating',
                        color='product_category',
                        title='Rating vs Review Count',
                        labels={'total_reviews': 'Number of Reviews', 'product_rating': 'Rating'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Rating categories
        rating_bins = pd.cut(filtered_df['product_rating'],
                            bins=[0, 3, 3.5, 4, 4.5, 5],
                            labels=['Poor (<3)', 'Fair (3-3.5)', 'Good (3.5-4)',
                                   'Very Good (4-4.5)', 'Excellent (4.5+)'])
        rating_dist = rating_bins.value_counts()
        
        fig = px.pie(values=rating_dist.values, names=rating_dist.index,
                    title='Rating Category Distribution',
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)
    
    # Rating statistics by category
    st.subheader("Rating Statistics by Category")
    rating_stats = filtered_df.groupby('product_category')['product_rating'].agg([
        ('Count', 'count'),
        ('Mean', 'mean'),
        ('Median', 'median'),
        ('Std Dev', 'std'),
        ('Min', 'min'),
        ('Max', 'max')
    ]).round(2)
    st.dataframe(rating_stats, use_container_width=True)

with tab3:
    st.header("Sales Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Purchase volume distribution
        fig = px.histogram(filtered_df[filtered_df['purchased_last_month'] < filtered_df['purchased_last_month'].quantile(0.95)],
                          x='purchased_last_month', nbins=50,
                          title='Purchase Volume Distribution (95th percentile)',
                          labels={'purchased_last_month': 'Purchases Last Month'},
                          color_discrete_sequence=['#146EB4'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Purchases vs Rating
        # Filter out rows with NaN in total_reviews for size parameter
        scatter_df = filtered_df.dropna(subset=['total_reviews'])
        fig = px.scatter(scatter_df, x='product_rating', y='purchased_last_month',
                        color='product_category',
                        size='total_reviews',
                        title='Rating vs Purchase Volume (bubble size = reviews)',
                        labels={'product_rating': 'Rating', 'purchased_last_month': 'Purchases Last Month'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Total purchases by category
        purchases_by_cat = filtered_df.groupby('product_category')['purchased_last_month'].sum().sort_values(ascending=False)
        
        fig = px.bar(x=purchases_by_cat.index, y=purchases_by_cat.values,
                    title='Total Purchase Volume by Category',
                    labels={'x': 'Category', 'y': 'Total Purchases'},
                    color=purchases_by_cat.values,
                    color_continuous_scale='Teal')
        fig.update_layout(xaxis=dict(tickangle=45))
        st.plotly_chart(fig, use_container_width=True)
        
        # Reviews vs Purchases
        fig = px.scatter(filtered_df, x='total_reviews', y='purchased_last_month',
                        color='product_rating',
                        title='Review Count vs Purchase Volume',
                        labels={'total_reviews': 'Total Reviews', 'purchased_last_month': 'Purchases Last Month'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Top selling products
    st.subheader(f"Top {min(20, top_n)} Best Selling Products")
    top_sellers = filtered_df.nlargest(min(20, top_n), 'purchased_last_month')[
        ['product_title', 'purchased_last_month', 'product_rating', 'total_reviews', 
         'discounted_price', 'product_category']
    ]
    st.dataframe(top_sellers, use_container_width=True, hide_index=True)

with tab4:
    st.header("Best Seller Analysis")
    
    # Best seller comparison
    best_seller_df = filtered_df[filtered_df['is_best_seller'] == 'Best Seller']
    regular_df = filtered_df[filtered_df['is_best_seller'] != 'Best Seller']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Best Seller Products", f"{len(best_seller_df):,}")
        st.metric("Regular Products", f"{len(regular_df):,}")
        st.metric("Best Seller %", f"{len(best_seller_df)/len(filtered_df)*100:.1f}%")
    
    with col2:
        if len(best_seller_df) > 0:
            st.metric("Avg Rating (Best Sellers)", f"{best_seller_df['product_rating'].mean():.2f}")
            st.metric("Avg Price (Best Sellers)", f"${best_seller_df['discounted_price'].mean():.2f}")
            st.metric("Avg Reviews (Best Sellers)", f"{best_seller_df['total_reviews'].mean():,.0f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Best seller distribution by category
        if len(best_seller_df) > 0:
            bs_by_cat = best_seller_df['product_category'].value_counts()
            fig = px.bar(x=bs_by_cat.index, y=bs_by_cat.values,
                        title='Best Sellers by Category',
                        labels={'x': 'Category', 'y': 'Number of Best Sellers'},
                        color=bs_by_cat.values,
                        color_continuous_scale='Oranges')
            fig.update_layout(xaxis=dict(tickangle=45))
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Comparison: Best Sellers vs Regular
        if len(best_seller_df) > 0 and len(regular_df) > 0:
            comparison_data = pd.DataFrame({
                'Metric': ['Avg Rating', 'Avg Price', 'Avg Reviews', 'Avg Purchases'],
                'Best Sellers': [
                    best_seller_df['product_rating'].mean(),
                    best_seller_df['discounted_price'].mean(),
                    best_seller_df['total_reviews'].mean(),
                    best_seller_df['purchased_last_month'].mean()
                ],
                'Regular Products': [
                    regular_df['product_rating'].mean(),
                    regular_df['discounted_price'].mean(),
                    regular_df['total_reviews'].mean(),
                    regular_df['purchased_last_month'].mean()
                ]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Best Sellers', x=comparison_data['Metric'],
                                y=comparison_data['Best Sellers'], marker_color='gold'))
            fig.add_trace(go.Bar(name='Regular Products', x=comparison_data['Metric'],
                                y=comparison_data['Regular Products'], marker_color='silver'))
            fig.update_layout(title='Best Sellers vs Regular Products Comparison',
                            barmode='group')
            st.plotly_chart(fig, use_container_width=True)
    
    # Best seller products list
    if len(best_seller_df) > 0:
        st.subheader("All Best Seller Products")
        display_cols = ['product_title', 'product_rating', 'total_reviews',
                       'purchased_last_month', 'discounted_price', 'product_category']
        st.dataframe(best_seller_df[display_cols].sort_values('product_rating', ascending=False),
                    use_container_width=True, hide_index=True)

st.markdown("---")
st.info("Insight: Analyze what makes top products successful and identify patterns among best sellers.")
