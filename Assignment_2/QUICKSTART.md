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

## Usage Tips

1. **Start with Dataset Overview** to understand the data structure
2. **Use Exploratory Analysis** for detailed investigation with filters
3. **Check Pricing Analysis** for pricing strategy insights
4. **Review Performance Metrics** to identify top products
5. **Use Comparison Tools** for detailed product/category comparison
6. **Export Data** for further analysis in other tools

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