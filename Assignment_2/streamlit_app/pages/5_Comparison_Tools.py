"""Comparison Tools Page - Multi-product and category comparison with data export."""

import streamlit as st
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from data_loader import load_data

st.set_page_config(page_title="Comparison Tools", page_icon=":mag:", layout="wide")

st.title("Comparison & Analysis Tools")
st.markdown("Compare products, categories, and export filtered data")

# Load data
@st.cache_data
def load_dataset():
    return load_data()

df = load_dataset()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Product Comparison", "Category Benchmark", "Feature Explorer", "Data Export"])

with tab1:
    st.header("Multi-Product Comparison")
    
    # Product selection
    st.subheader("Select Products to Compare")
    
    categories = sorted(df['product_category'].unique().tolist())
    selected_cat = st.selectbox("Filter by Category", ['All'] + categories)
    
    if selected_cat != 'All':
        product_list = df[df['product_category'] == selected_cat]['product_title'].tolist()
    else:
        product_list = df['product_title'].tolist()
    
    selected_products = st.multiselect(
        "Choose products (up to 10)",
        product_list,
        default=product_list[:3] if len(product_list) >= 3 else product_list,
        max_selections=10
    )
    
    if selected_products:
        comparison_df = df[df['product_title'].isin(selected_products)]
        
        # Comparison table
        st.subheader("Comparison Table")
        comparison_cols = ['product_title', 'product_rating', 'total_reviews',
                          'purchased_last_month', 'discounted_price', 'original_price',
                          'discount_percentage', 'product_category']
        st.dataframe(comparison_df[comparison_cols], use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Rating comparison
            fig = px.bar(comparison_df, x='product_title', y='product_rating',
                        title='Rating Comparison',
                        labels={'product_title': 'Product', 'product_rating': 'Rating'},
                        color='product_rating',
                        color_continuous_scale='RdYlGn')
            fig.update_layout(xaxis=dict(tickangle=45))
            st.plotly_chart(fig, use_container_width=True)
            
            # Review count comparison
            fig = px.bar(comparison_df, x='product_title', y='total_reviews',
                        title='Review Count Comparison',
                        labels={'product_title': 'Product', 'total_reviews': 'Reviews'},
                        color='total_reviews',
                        color_continuous_scale='Blues')
            fig.update_layout(xaxis=dict(tickangle=45))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Price comparison
            fig = go.Figure()
            fig.add_trace(go.Bar(x=comparison_df['product_title'],
                                y=comparison_df['original_price'],
                                name='Original Price',
                                marker_color='lightgray'))
            fig.add_trace(go.Bar(x=comparison_df['product_title'],
                                y=comparison_df['discounted_price'],
                                name='Discounted Price',
                                marker_color='#FF9900'))
            fig.update_layout(title='Price Comparison',
                            barmode='group',
                            xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Purchases comparison
            fig = px.bar(comparison_df, x='product_title', y='purchased_last_month',
                        title='Purchase Volume Comparison',
                        labels={'product_title': 'Product', 'purchased_last_month': 'Purchases Last Month'},
                        color='purchased_last_month',
                        color_continuous_scale='Greens')
            fig.update_layout(xaxis=dict(tickangle=45))
            st.plotly_chart(fig, use_container_width=True)
        
        # Radar chart
        st.subheader("Multi-Metric Comparison (Normalized)")
        
        # Normalize metrics for radar chart
        metrics_to_compare = ['product_rating', 'total_reviews', 'purchased_last_month',
                             'discounted_price', 'discount_percentage']
        
        fig = go.Figure()
        
        for _, row in comparison_df.iterrows():
            values = []
            for metric in metrics_to_compare:
                max_val = df[metric].max()
                if max_val > 0:
                    normalized = (row[metric] / max_val) * 100
                else:
                    normalized = 0
                values.append(normalized)
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=[m.replace('_', ' ').title() for m in metrics_to_compare],
                fill='toself',
                name=row['product_title'][:50]
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select products above to compare them")

with tab2:
    st.header("Category Benchmarking")
    
    # Category statistics
    category_stats = df.groupby('product_category').agg({
        'product_title': 'count',
        'product_rating': 'mean',
        'total_reviews': ['mean', 'sum'],
        'purchased_last_month': ['mean', 'sum'],
        'discounted_price': 'mean',
        'discount_percentage': 'mean'
    }).round(2)
    
    category_stats.columns = ['Product Count', 'Avg Rating', 'Avg Reviews', 'Total Reviews',
                              'Avg Purchases', 'Total Purchases', 'Avg Price', 'Avg Discount %']
    
    st.subheader("Category Performance Metrics")
    st.dataframe(category_stats, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Category comparison - Rating
        fig = px.bar(category_stats.reset_index(),
                    x='product_category', y='Avg Rating',
                    title='Average Rating by Category',
                    labels={'product_category': 'Category', 'Avg Rating': 'Average Rating'},
                    color='Avg Rating',
                    color_continuous_scale='RdYlGn')
        fig.update_layout(xaxis=dict(tickangle=45))
        st.plotly_chart(fig, use_container_width=True)
        
        # Category comparison - Price
        fig = px.bar(category_stats.reset_index(),
                    x='product_category', y='Avg Price',
                    title='Average Price by Category',
                    labels={'product_category': 'Category', 'Avg Price': 'Average Price ($)'},
                    color='Avg Price',
                    color_continuous_scale='Viridis')
        fig.update_layout(xaxis=dict(tickangle=45))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category comparison - Total Purchases
        fig = px.bar(category_stats.reset_index(),
                    x='product_category', y='Total Purchases',
                    title='Total Purchase Volume by Category',
                    labels={'product_category': 'Category', 'Total Purchases': 'Total Purchases'},
                    color='Total Purchases',
                    color_continuous_scale='Blues')
        fig.update_layout(xaxis=dict(tickangle=45))
        st.plotly_chart(fig, use_container_width=True)
        
        # Category comparison - Discount
        fig = px.bar(category_stats.reset_index(),
                    x='product_category', y='Avg Discount %',
                    title='Average Discount by Category',
                    labels={'product_category': 'Category', 'Avg Discount %': 'Average Discount (%)'},
                    color='Avg Discount %',
                    color_continuous_scale='Reds')
        fig.update_layout(xaxis=dict(tickangle=45))
        st.plotly_chart(fig, use_container_width=True)
    
    # Category heatmap
    st.subheader("Category Metrics Heatmap (Normalized)")
    
    # Normalize for heatmap
    heatmap_data = category_stats[['Avg Rating', 'Avg Reviews', 'Avg Purchases', 'Avg Price', 'Avg Discount %']].copy()
    for col in heatmap_data.columns:
        heatmap_data[col] = (heatmap_data[col] - heatmap_data[col].min()) / (heatmap_data[col].max() - heatmap_data[col].min())
    
    fig = px.imshow(heatmap_data.T,
                    labels=dict(x="Category", y="Metric", color="Normalized Value"),
                    title="Category Performance Heatmap (Normalized 0-1)",
                    aspect="auto",
                    color_continuous_scale='RdYlGn')
    fig.update_layout(xaxis=dict(tickangle=45))
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Feature Correlation Explorer")
    
    # Select features to explore
    numeric_features = ['product_rating', 'total_reviews', 'purchased_last_month',
                       'discounted_price', 'original_price', 'discount_percentage']
    
    col1, col2 = st.columns(2)
    
    with col1:
        x_feature = st.selectbox("X-Axis Feature", numeric_features, index=0)
    
    with col2:
        y_feature = st.selectbox("Y-Axis Feature", numeric_features, index=2)
    
    color_by = st.selectbox("Color By", ['product_category', 'is_best_seller', 'is_sponsored', 'price_category'])
    
    # Add price category if needed
    if 'price_category' not in df.columns:
        df['price_category'] = pd.cut(df['discounted_price'],
                                     bins=[0, 50, 100, 200, float('inf')],
                                     labels=['Budget', 'Mid-range', 'Premium', 'Luxury'])
    
    # Scatter plot
    fig = px.scatter(df, x=x_feature, y=y_feature,
                    color=color_by,
                    title=f'{y_feature.replace("_", " ").title()} vs {x_feature.replace("_", " ").title()}',
                    labels={x_feature: x_feature.replace('_', ' ').title(),
                           y_feature: y_feature.replace('_', ' ').title()},
                    hover_data=['product_title'])
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation matrix
    st.subheader("Correlation Matrix")
    
    corr_matrix = df[numeric_features].corr()
    
    fig = px.imshow(corr_matrix,
                    labels=dict(color="Correlation"),
                    title="Feature Correlation Matrix",
                    color_continuous_scale='RdBu',
                    aspect="auto",
                    text_auto='.2f')
    st.plotly_chart(fig, use_container_width=True)
    
    # Distribution comparison
    st.subheader("Distribution Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(df, x=x_feature, color=color_by,
                          title=f'{x_feature.replace("_", " ").title()} Distribution',
                          labels={x_feature: x_feature.replace('_', ' ').title()},
                          marginal='box')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.histogram(df, x=y_feature, color=color_by,
                          title=f'{y_feature.replace("_", " ").title()} Distribution',
                          labels={y_feature: y_feature.replace('_', ' ').title()},
                          marginal='box')
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Data Export Tools")
    
    st.markdown("### Filter and Export Data")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        export_categories = st.multiselect("Categories", sorted(df['product_category'].unique().tolist()),
                                          default=sorted(df['product_category'].unique().tolist()))
    
    with col2:
        min_rating_export = st.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.1)
    
    with col3:
        price_range_export = st.slider("Price Range",
                                       float(df['discounted_price'].min()),
                                       float(df['discounted_price'].max()),
                                       (float(df['discounted_price'].min()),
                                        float(df['discounted_price'].max())))
    
    # Apply filters
    export_df = df[
        (df['product_category'].isin(export_categories)) &
        (df['product_rating'] >= min_rating_export) &
        (df['discounted_price'] >= price_range_export[0]) &
        (df['discounted_price'] <= price_range_export[1])
    ]
    
    st.info(f"Filtered dataset: {len(export_df):,} products (from {len(df):,} total)")
    
    # Preview
    st.subheader("Preview Filtered Data")
    st.dataframe(export_df.head(20), use_container_width=True, hide_index=True)
    
    # Download button
    st.markdown("---")
    st.subheader("Download Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name="amazon_products_filtered.csv",
            mime="text/csv"
        )
    
    with col2:
        # Summary statistics
        summary_csv = export_df.describe().to_csv().encode('utf-8')
        st.download_button(
            label="Download Summary Statistics",
            data=summary_csv,
            file_name="summary_statistics.csv",
            mime="text/csv"
        )
    
    # Export summary
    st.subheader("Export Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Products", f"{len(export_df):,}")
        st.metric("Avg Rating", f"{export_df['product_rating'].mean():.2f}")
    
    with col2:
        st.metric("Avg Price", f"${export_df['discounted_price'].mean():.2f}")
        st.metric("Total Reviews", f"{export_df['total_reviews'].sum():,.0f}")
    
    with col3:
        st.metric("Categories", export_df['product_category'].nunique())
        st.metric("Best Sellers", (export_df['is_best_seller'] == 'Best Seller').sum())

st.markdown("---")
st.info("Tip: Use comparison tools to identify patterns and make data-driven decisions!")
