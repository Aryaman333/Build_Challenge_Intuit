# Assignment 2: Quick Start Guide

### Installation
```bash
cd Assignment_2
pip install -r requirements.txt
```

### Running the Dashboard

**Option 1: Using the quick start script**
```bash
python run_dashboard.py
```

**Option 2: Direct Streamlit command**
```bash
cd streamlit_app
streamlit run app.py
```

The dashboard will open automatically at `http://localhost:8501`

## Dashboard Pages

### 1. Home (Main Page)
- Dataset overview and key metrics
- Quick statistics
- Dataset sample preview
- Navigation guide

### 2. Dataset Overview
- Complete statistics
- Data quality analysis  
- Missing value summary
- Category distributions
- Feature distributions

### 3. Exploratory Analysis
- Interactive filters (category, price, rating)
- Distribution analysis
- Correlation heatmaps
- Trend analysis
- Category comparisons

### 4. Pricing Analysis
- Price distribution by category
- Discount effectiveness
- Price vs rating analysis
- Value proposition insights
- Price segment performance

### 5. Performance Metrics
- Top products ranking
- Rating analysis
- Sales performance
- Best seller comparison
- Category-wise rankings

### 6. Comparison Tools
- Multi-product comparison
- Category benchmarking
- Feature correlation explorer
- Data export (CSV download)

## Key Features

### Interactive Filters
- Category selection
- Price range sliders
- Rating thresholds
- Dynamic data updates

### Visualizations
- Distribution plots (histograms, box plots)
- Correlation heatmaps
- Scatter plots with trendlines
- Radar charts
- Pie charts and bar charts
- Violin plots

### Data Export
- Filter and download custom datasets
- Export summary statistics
- CSV format support

## Usage Tips

1. **Start with Dataset Overview** to understand the data structure
2. **Use Exploratory Analysis** for detailed investigation with filters
3. **Check Pricing Analysis** for pricing strategy insights
4. **Review Performance Metrics** to identify top products
5. **Use Comparison Tools** for detailed product/category comparison
6. **Export Data** for further analysis in other tools

## Project Structure

```
Assignment_2/
├── data/
│   └── cleaned/
│       └── amazon_products_sales_data_cleaned.csv
├── streamlit_app/
│   ├── app.py                              # Main dashboard page
│   └── pages/
│       ├── 1_Dataset_Overview.py        # Data statistics
│       ├── 2_Exploratory_Analysis.py    # Interactive EDA
│       ├── 3_Pricing_Analysis.py         # Pricing insights
│       ├── 4_Performance_Metrics.py      # Rankings & metrics
│       └── 5_Comparison_Tools.py        # Comparison & export
├── scripts/
│   ├── data_loader.py                      # Data loading utilities
│   ├── visualization.py                    # Visualization functions
│   └── statistical_tests.py                # Statistical analysis
├── notebooks/                              # Jupyter notebooks (to be created)
├── requirements.txt                        # Python dependencies
├── run_dashboard.py                        # Quick start script
└── README.md                               # Full documentation
```

## Troubleshooting

### Port Already in Use
If port 8501 is busy, use:
```bash
streamlit run app.py --server.port 8502
```

### Module Not Found
Ensure you're in the correct directory:
```bash
cd Assignment_2/streamlit_app
```

### Data File Not Found
Verify the data file exists at:
```
Assignment_2/data/cleaned/amazon_products_sales_data_cleaned.csv
```

## Next Steps

1. Explore all dashboard pages
2. Try different filter combinations
3. Export data for custom analysis
4. Review insights and patterns
5. Create additional visualizations as needed