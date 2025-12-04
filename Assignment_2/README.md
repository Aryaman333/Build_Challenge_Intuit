# Assignment 2: Amazon Products Sales Data Analysis

##  Project Overview
This project provides comprehensive analysis and interactive visualization of Amazon products sales data, focusing on pricing strategies, product performance, and market insights.

##  Dataset Information
- **Source**: Amazon Products Sales Data (Cleaned)
- **Size**: 42,675 products
- **Features**: 17 columns
- **Categories**: Electronics (Phones, Laptops, and more)
- **Time Period**: August-September 2025

### Dataset Features
| Feature | Type | Description |
|---------|------|-------------|
| `product_title` | String | Product name and description |
| `product_rating` | Float | Average product rating (0-5 scale) |
| `total_reviews` | Float | Number of customer reviews |
| `purchased_last_month` | Float | Units sold in the last month |
| `discounted_price` | Float | Current selling price (USD) |
| `original_price` | Float | Original listing price (USD) |
| `discount_percentage` | Float | Percentage discount offered |
| `is_best_seller` | String | Best seller badge status |
| `is_sponsored` | String | Sponsored/Organic listing |
| `has_coupon` | String | Coupon availability |
| `buy_box_availability` | String | Add to cart availability |
| `delivery_date` | String | Expected delivery date |
| `sustainability_tags` | String | Environmental/sustainability labels |
| `product_category` | String | Product category classification |
| `product_image_url` | String | Product image URL |
| `product_page_url` | String | Amazon product page URL |
| `data_collected_at` | String | Data collection timestamp |

##  Analysis Objectives

### 1. Exploratory Data Analysis (EDA)
- Understand dataset structure and quality
- Identify missing values and outliers
- Analyze distributions of key metrics
- Explore relationships between variables

### 2. Pricing Strategy Analysis
- Price distribution across categories
- Discount effectiveness on sales
- Price vs quality (rating) relationship
- Premium vs budget product performance

### 3. Product Performance Metrics
- Top-rated products identification
- High-volume sellers analysis
- Best seller characteristics
- Category-wise performance comparison

### 4. Marketing Effectiveness
- Sponsored vs organic product comparison
- Coupon impact on purchase volume
- Sustainability tags influence on ratings
- Review count correlation with sales

### 5. Statistical Insights
- Correlation analysis between features
- Category-specific trends
- Temporal patterns (if applicable)
- Predictive insights for product success

##  Project Structure
```
Assignment_2/
├── data/
│   └── cleaned/
│       └── amazon_products_sales_data_cleaned.csv
├── scripts/
│   ├── data_loader.py
│   ├── visualization.py
│   └── statistical_tests.py
├── streamlit_app/
│   ├── app.py
│   ├── pages/
│      ├── 1_Dataset_Overview.py
│      ├── 2_Exploratory_Analysis.py
│      ├── 3_Pricing_Analysis.py
│      ├── 4_Performance_Metrics.py
│      └── 5_Comparison_Tools.py
│   
├── requirements.txt
├── README.md
├── run_dashboard.py
└── QUICKSTART.md
```

##  Getting Started

### Prerequisites
```bash
pip install -r requirements.txt
```

### Running Analysis Notebooks
```bash
cd notebooks
jupyter notebook
# Open and run notebooks in order: 01 -> 02 -> 03
```

### Running Streamlit Dashboard
```bash
cd streamlit_app
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## Interactive Dashboard Features

### 1. Dataset Overview
- Key statistics and metrics
- Data quality summary
- Category distribution
- Missing value visualization

### 2. Exploratory Analysis
- Interactive filters (category, price range, rating)
- Dynamic visualizations
- Distribution plots
- Correlation heatmaps

### 3. Pricing Analysis
- Price distribution by category
- Discount effectiveness
- Price vs rating scatter plots
- Premium vs budget comparison

### 4. Performance Metrics
- Top products by category
- Rating distribution analysis
- Review count analysis
- Sales volume trends

### 5. Comparison Tools
- Multi-product comparison
- Category benchmarking
- Feature correlation explorer
- Export filtered data

## Analysis Workflow

1. **Data Loading & Validation**
   - Load dataset and verify structure
   - Check data types and convert if needed
   - Handle missing values

2. **Exploratory Analysis**
   - Univariate analysis (distributions)
   - Bivariate analysis (relationships)
   - Multivariate analysis (patterns)

3. **Statistical Testing**
   - Hypothesis testing
   - Correlation analysis
   - Significance tests

4. **Visualization**
   - Create insightful charts
   - Build interactive dashboards
   - Export publication-ready figures

5. **Insights & Recommendations**
   - Document key findings
   - Provide actionable insights
   - Suggest business strategies

## Learning Outcomes
- Data cleaning and preprocessing techniques
- Exploratory data analysis methodologies
- Statistical hypothesis testing
- Interactive dashboard development
- Data visualization best practices
- Business insights derivation
