"""Pricing Analysis Page - Deep dive into pricing strategies and discount effectiveness."""

import streamlit as st
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from data_loader import load_data

st.set_page_config(page_title="Pricing Analysis", page_icon=":moneybag:", layout="wide")

st.title("Pricing Strategy Analysis")
st.markdown("Explore pricing patterns, discount effectiveness, and value propositions")

# Load data
@st.cache_data
def load_dataset():
    return load_data()

df = load_dataset()

# Calculate price metrics
df['price_difference'] = df['original_price'] - df['discounted_price']
df['price_category'] = pd.cut(df['discounted_price'],
                               bins=[0, 50, 100, 200, float('inf')],
                               labels=['Budget (<$50)', 'Mid-range ($50-$100)',
                                      'Premium ($100-$200)', 'Luxury (>$200)'])

# Sidebar
st.sidebar.header("Price Filters")
selected_category = st.sidebar.selectbox("Product Category", ['All'] + sorted(df['product_category'].unique().tolist()))

if selected_category != 'All':
    filtered_df = df[df['product_category'] == selected_category]
else:
    filtered_df = df.copy()

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Median Price", f"${filtered_df['discounted_price'].median():.2f}")

with col2:
    st.metric("Avg Discount", f"{filtered_df['discount_percentage'].mean():.1f}%")

with col3:
    st.metric("Max Discount", f"{filtered_df['discount_percentage'].max():.1f}%")

with col4:
    avg_savings = filtered_df['price_difference'].mean()
    st.metric("Avg Savings", f"${avg_savings:.2f}")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Price Distribution", "Discount Analysis", "Value Analysis", "Price Segments"])

with tab1:
    st.header("Price Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price histogram
        fig = px.histogram(filtered_df, x='discounted_price', nbins=50,
                          title='Current Price Distribution',
                          labels={'discounted_price': 'Price (USD)'},
                          color_discrete_sequence=['#FF9900'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Price by category
        fig = px.box(filtered_df, x='product_category', y='discounted_price',
                    title='Price Range by Category',
                    labels={'product_category': 'Category', 'discounted_price': 'Price (USD)'})
        fig.update_layout(xaxis=dict(tickangle=45))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Original vs Discounted price
        price_comparison = filtered_df.groupby('product_category').agg({
            'original_price': 'mean',
            'discounted_price': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=price_comparison['product_category'],
                            y=price_comparison['original_price'],
                            name='Original Price',
                            marker_color='lightgray'))
        fig.add_trace(go.Bar(x=price_comparison['product_category'],
                            y=price_comparison['discounted_price'],
                            name='Discounted Price',
                            marker_color='#FF9900'))
        fig.update_layout(title='Original vs Discounted Price by Category',
                         barmode='group',
                         xaxis_title='Category',
                         yaxis_title='Average Price (USD)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Price category distribution
        price_cat_counts = filtered_df['price_category'].value_counts()
        fig = px.pie(values=price_cat_counts.values,
                    names=price_cat_counts.index,
                    title='Product Distribution by Price Segment')
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Discount Effectiveness Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Discount distribution
        fig = px.histogram(filtered_df, x='discount_percentage', nbins=50,
                          title='Discount Percentage Distribution',
                          labels={'discount_percentage': 'Discount %'},
                          color_discrete_sequence=['#146EB4'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Discount vs Purchases
        fig = px.scatter(filtered_df, x='discount_percentage', y='purchased_last_month',
                        color='product_rating',
                        title='Discount Impact on Purchase Volume',
                        labels={'discount_percentage': 'Discount %',
                               'purchased_last_month': 'Purchases Last Month'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Discount by category
        fig = px.violin(filtered_df, x='product_category', y='discount_percentage',
                       title='Discount Distribution by Category',
                       labels={'product_category': 'Category', 'discount_percentage': 'Discount %'},
                       box=True, color='product_category')
        fig.update_layout(xaxis=dict(tickangle=45))
        st.plotly_chart(fig, use_container_width=True)
        
        # Discount vs Rating
        fig = px.scatter(filtered_df, x='discount_percentage', y='product_rating',
                        color='product_category',
                        title='Discount vs Product Rating',
                        labels={'discount_percentage': 'Discount %', 'product_rating': 'Rating'})
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Price-Quality Value Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price vs Rating scatter
        # Filter out rows with NaN in total_reviews for size parameter
        scatter_df = filtered_df.dropna(subset=['total_reviews'])
        fig = px.scatter(scatter_df, x='discounted_price', y='product_rating',
                        color='product_category',
                        size='total_reviews',
                        title='Price vs Rating (bubble size = reviews)',
                        labels={'discounted_price': 'Price (USD)', 'product_rating': 'Rating'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Value score (rating per dollar)
        filtered_df['value_score'] = filtered_df['product_rating'] / filtered_df['discounted_price'] * 100
        top_value = filtered_df.nlargest(10, 'value_score')[['product_title', 'product_rating', 
                                                               'discounted_price', 'value_score']]
        st.subheader("Top 10 Best Value Products")
        st.dataframe(top_value, use_container_width=True, hide_index=True)
    
    with col2:
        # Rating distribution by price category
        fig = px.box(filtered_df, x='price_category', y='product_rating',
                    title='Rating Distribution by Price Segment',
                    labels={'price_category': 'Price Segment', 'product_rating': 'Rating'},
                    color='price_category')
        st.plotly_chart(fig, use_container_width=True)
        
        # Purchases by price category
        purchases_by_price = filtered_df.groupby('price_category')['purchased_last_month'].sum()
        fig = px.bar(x=purchases_by_price.index, y=purchases_by_price.values,
                    title='Total Purchases by Price Segment',
                    labels={'x': 'Price Segment', 'y': 'Total Purchases'},
                    color=purchases_by_price.values,
                    color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Price Segmentation Insights")
    
    # Price segment analysis
    segment_analysis = filtered_df.groupby('price_category').agg({
        'product_title': 'count',
        'product_rating': 'mean',
        'total_reviews': 'mean',
        'purchased_last_month': 'sum',
        'discount_percentage': 'mean'
    }).round(2)
    segment_analysis.columns = ['Product Count', 'Avg Rating', 'Avg Reviews', 
                                'Total Purchases', 'Avg Discount %']
    
    st.subheader("Price Segment Performance Metrics")
    st.dataframe(segment_analysis, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Segment performance radar
        categories = segment_analysis.index.tolist()
        
        fig = go.Figure()
        for metric in ['Avg Rating', 'Avg Discount %']:
            normalized_values = (segment_analysis[metric] / segment_analysis[metric].max()).tolist()
            fig.add_trace(go.Scatterpolar(
                r=normalized_values,
                theta=categories,
                fill='toself',
                name=metric
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            title='Price Segment Performance (Normalized)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Market share by price segment
        fig = px.pie(filtered_df, names='price_category',
                    title='Market Share by Price Segment',
                    hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.info("Insight: Explore how pricing strategies correlate with product performance and customer satisfaction.")
