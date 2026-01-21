# dashboard/app.py - Streamlit dashboard for price analysis

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
import json
import re

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="IdealZ Competitor Price Monitor",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {font-size:20px !important; font-weight: bold;}
    .alert-box {padding: 10px; border-radius: 5px; margin: 10px 0;}
    .alert-danger {background-color: #ffebee; border-left: 5px solid #f44336;}
    .alert-warning {background-color: #fff3e0; border-left: 5px solid #ff9800;}
    .alert-success {background-color: #e8f5e9; border-left: 5px solid #4caf50;}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data():
    """Load data from CSV - tries both GitHub and local"""
    csv_urls = [
        'data/all_products.csv',  # Local first
        'https://raw.githubusercontent.com/shaAhame/price_war/main/data/all_products.csv',  # GitHub
    ]
    
    for url in csv_urls:
        try:
            df = pd.read_csv(url)
            df['price_LKR'] = pd.to_numeric(df['price_LKR'], errors='coerce')
            df['is_own_shop'] = df.get('is_own_shop', False).fillna(False)
            return df
        except Exception as e:
            continue
    
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_my_prices():
    """Load your shop's prices from JSON"""
    try:
        urls = [
            'data/my_prices.json',  # Local first
            'https://raw.githubusercontent.com/shaAhame/price_war/main/data/my_prices.json',  # GitHub
        ]
        
        for url in urls:
            try:
                if url.startswith('http'):
                    import requests
                    response = requests.get(url)
                    return response.json()
                else:
                    with open(url, 'r') as f:
                        return json.load(f)
            except:
                continue
    except:
        pass
    
    return {}

def extract_model_number(product_name):
    """Extract iPhone model number (e.g., '15 Pro', '14', '16 Pro Max')"""
    # Look for patterns like "iPhone 15 Pro Max", "iPhone 14", etc.
    pattern = r'iPhone\s+(\d+(?:\s+(?:Pro|Plus|Max|Mini|SE|e|E))*)'
    match = re.search(pattern, product_name, re.IGNORECASE)
    
    if match:
        return match.group(1).strip().lower()
    
    # Also check for iPad, MacBook, AirPods
    if 'ipad' in product_name.lower():
        pattern = r'iPad\s+(\w+(?:\s+\w+)*)'
        match = re.search(pattern, product_name, re.IGNORECASE)
        if match:
            return match.group(1).strip().lower()
    
    if 'macbook' in product_name.lower():
        pattern = r'MacBook\s+(\w+(?:\s+\w+)*)'
        match = re.search(pattern, product_name, re.IGNORECASE)
        if match:
            return match.group(1).strip().lower()
    
    if 'airpod' in product_name.lower():
        pattern = r'AirPod[s]?\s+(\w+(?:\s+\w+)*)'
        match = re.search(pattern, product_name, re.IGNORECASE)
        if match:
            return match.group(1).strip().lower()
    
    if 'watch' in product_name.lower():
        pattern = r'Watch\s+(\w+(?:\s+\w+)*)'
        match = re.search(pattern, product_name, re.IGNORECASE)
        if match:
            return match.group(1).strip().lower()
    
    return None

def extract_storage(product_name):
    """Extract storage capacity (e.g., '128GB', '256GB')"""
    pattern = r'(\d+(?:GB|TB))'
    match = re.search(pattern, product_name, re.IGNORECASE)
    
    if match:
        return match.group(1).upper()
    
    return None

def models_match(model1, model2):
    """Check if two model numbers are the same"""
    if not model1 or not model2:
        return False
    
    # Normalize
    m1 = model1.lower().strip()
    m2 = model2.lower().strip()
    
    # Exact match
    if m1 == m2:
        return True
    
    # Handle variations (e.g., "15 pro" vs "15pro")
    m1_clean = m1.replace(' ', '')
    m2_clean = m2.replace(' ', '')
    
    return m1_clean == m2_clean

def find_price_wars(df, my_prices=None, threshold=5):
    """Find products where competitors are significantly cheaper - with smart matching"""
    alerts = []
    
    your_products = df[df['is_own_shop'] == True]
    competitor_products = df[df['is_own_shop'] == False]
    
    if your_products.empty and not my_prices:
        return pd.DataFrame()
    
    if not your_products.empty:
        for _, your_product in your_products.iterrows():
            my_name = your_product['product']
            my_price = your_product['price_LKR']
            
            if pd.isna(my_price) or my_price == 0:
                continue
            
            # Extract model number from your product
            my_model = extract_model_number(my_name)
            my_storage = extract_storage(my_name)
            
            # Find similar products
            for _, competitor in competitor_products.iterrows():
                comp_price = competitor['price_LKR']
                comp_name = competitor['product']
                
                # Skip if competitor price is 0 or invalid
                if pd.isna(comp_price) or comp_price == 0:
                    continue
                
                # Extract competitor model
                comp_model = extract_model_number(comp_name)
                comp_storage = extract_storage(comp_name)
                
                # Only compare if models match
                if not models_match(my_model, comp_model):
                    continue
                
                # Check storage capacity similarity (if both have storage info)
                if my_storage and comp_storage and my_storage != comp_storage:
                    continue
                
                # Calculate price difference
                price_diff = ((my_price - comp_price) / my_price) * 100
                
                if price_diff > threshold and price_diff < 100:  # Reasonable range
                    alerts.append({
                        'my_product': my_name,
                        'my_price': my_price,
                        'competitor': competitor['site'],
                        'competitor_product': comp_name,
                        'competitor_price': comp_price,
                        'savings_percent': round(price_diff, 1),
                        'savings_amount': my_price - comp_price
                    })
    
    elif my_prices:
        # Fallback to manual prices
        for my_product, my_price in my_prices.items():
            if my_price == 0:
                continue
            
            my_model = extract_model_number(my_product)
            my_storage = extract_storage(my_product)
            
            for _, competitor in competitor_products.iterrows():
                comp_price = competitor['price_LKR']
                comp_name = competitor['product']
                
                if pd.isna(comp_price) or comp_price == 0:
                    continue
                
                comp_model = extract_model_number(comp_name)
                comp_storage = extract_storage(comp_name)
                
                if not models_match(my_model, comp_model):
                    continue
                
                if my_storage and comp_storage and my_storage != comp_storage:
                    continue
                
                price_diff = ((my_price - comp_price) / my_price) * 100
                
                if threshold < price_diff < 100:
                    alerts.append({
                        'my_product': my_product,
                        'my_price': my_price,
                        'competitor': competitor['site'],
                        'competitor_product': comp_name,
                        'competitor_price': comp_price,
                        'savings_percent': round(price_diff, 1),
                        'savings_amount': my_price - comp_price
                    })
    
    return pd.DataFrame(alerts).drop_duplicates() if alerts else pd.DataFrame()

# Main app
st.title("📊 IdealZ Competitor Price Monitor")
st.markdown("**Track your prices vs 8 competitors in real-time**")
st.markdown("---")

# Load data
df = load_data()
my_prices_json = load_my_prices()

if df.empty:
    st.error("⚠️ No data available. Please run the scraper first!")
    st.info("Run: `python scraper/main_scraper.py`")
    st.stop()

# Separate your shop from competitors
your_products_df = df[df['is_own_shop'] == True]
competitor_products_df = df[df['is_own_shop'] == False]

# Filter out products with 0 prices
your_products_df = your_products_df[your_products_df['price_LKR'] > 0]
competitor_products_df = competitor_products_df[competitor_products_df['price_LKR'] > 0]

# Sidebar filters
st.sidebar.header("🔍 Filters")
sites = st.sidebar.multiselect(
    "Sites", 
    sorted(competitor_products_df['site'].unique()) if not competitor_products_df.empty else [],
    default=sorted(competitor_products_df['site'].unique())[:3] if not competitor_products_df.empty else []
)

categories = st.sidebar.multiselect(
    "Categories", 
    sorted(df['category'].unique()),
    default=sorted(df['category'].unique())[:5] if len(df['category'].unique()) > 5 else sorted(df['category'].unique())
)

if not competitor_products_df.empty:
    price_range = st.sidebar.slider(
        "Price Range (LKR)", 
        int(competitor_products_df['price_LKR'].min()), 
        int(competitor_products_df['price_LKR'].max()),
        (int(competitor_products_df['price_LKR'].min()), int(competitor_products_df['price_LKR'].max()))
    )
else:
    price_range = (0, 1000000)

# Filter data
filtered_competitor_df = competitor_products_df[
    (competitor_products_df['site'].isin(sites)) & 
    (competitor_products_df['category'].isin(categories)) &
    (competitor_products_df['price_LKR'] >= price_range[0]) &
    (competitor_products_df['price_LKR'] <= price_range[1])
] if not competitor_products_df.empty else pd.DataFrame()

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Your Products", len(your_products_df))
with col2:
    st.metric("Competitor Products", len(filtered_competitor_df))
with col3:
    st.metric("Total Sites Monitored", df['site'].nunique())
with col4:
    avg_comp_price = filtered_competitor_df['price_LKR'].mean() if not filtered_competitor_df.empty else 0
    st.metric("Avg Competitor Price", f"LKR {avg_comp_price:,.0f}" if avg_comp_price > 0 else "N/A")

# Price War Alerts
st.markdown("---")
st.header("🚨 Price War Alerts - Competitors Undercutting You")

alerts_df = find_price_wars(df, my_prices_json)

# Filter out invalid alerts
if not alerts_df.empty:
    alerts_df = alerts_df[
        (alerts_df['competitor_price'] > 0) & 
        (alerts_df['savings_percent'] > 0) & 
        (alerts_df['savings_percent'] < 100)
    ]

if not alerts_df.empty:
    # Sort by savings percent
    alerts_df = alerts_df.sort_values('savings_percent', ascending=False)
    
    st.markdown(f'<div class="alert-box alert-danger">⚠️ <b>{len(alerts_df)} competitors have lower prices!</b></div>', 
                unsafe_allow_html=True)
    
    # Show top 15 alerts
    st.subheader("🔥 Top Price Threats")
    for idx, alert in alerts_df.head(15).iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            **Your Product:** {alert['my_product']} (LKR {alert['my_price']:,.0f})  
            **Competitor:** {alert['competitor']} - "{alert['competitor_product']}"  
            **Their Price:** LKR {alert['competitor_price']:,.0f} 
            """)
        with col2:
            st.error(f"**-{alert['savings_percent']}%**  \nLKR {alert['savings_amount']:,.0f} cheaper")
        st.markdown("---")
else:
    st.markdown('<div class="alert-box alert-success">✅ Great! You have competitive pricing across the board!</div>', 
                unsafe_allow_html=True)

# Visualizations
st.markdown("---")
st.header("📈 Price Analysis")

tab1, tab2, tab3, tab4 = st.tabs(["📊 By Category", "🏪 Your vs Competitors", "💰 Cheapest Deals", "🔍 Price Comparison"])

with tab1:
    # Average price by category
    if not filtered_competitor_df.empty:
        cat_avg = filtered_competitor_df.groupby('category')['price_LKR'].mean().reset_index()
        fig = px.bar(cat_avg, x='category', y='price_LKR', 
                     title='Average Competitor Price by Category',
                     labels={'price_LKR': 'Price (LKR)', 'category': 'Category'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No competitor data to display")

with tab2:
    # Your prices vs competitors
    st.subheader("Your Shop vs Market")
    
    if not your_products_df.empty and not competitor_products_df.empty:
        comparison_data = []
        
        for _, your_prod in your_products_df.iterrows():
            my_model = extract_model_number(your_prod['product'])
            my_storage = extract_storage(your_prod['product'])
            
            min_comp_price = None
            min_comp_site = None
            
            for _, comp in competitor_products_df.iterrows():
                comp_model = extract_model_number(comp['product'])
                comp_storage = extract_storage(comp['product'])
                
                # Only compare matching models and storage
                if not models_match(my_model, comp_model):
                    continue
                
                if my_storage and comp_storage and my_storage != comp_storage:
                    continue
                
                if comp['price_LKR'] == 0:
                    continue
                
                if min_comp_price is None or comp['price_LKR'] < min_comp_price:
                    min_comp_price = comp['price_LKR']
                    min_comp_site = comp['site']
            
            if min_comp_price:
                comparison_data.append({
                    'Product': your_prod['product'][:40] + '...' if len(your_prod['product']) > 40 else your_prod['product'],
                    'Your Price': your_prod['price_LKR'],
                    'Cheapest Competitor': min_comp_price,
                    'Competitor': min_comp_site
                })
        
        if comparison_data:
            comp_df = pd.DataFrame(comparison_data)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Your Price',
                x=comp_df['Product'],
                y=comp_df['Your Price'],
                marker_color='#1f77b4'
            ))
            fig.add_trace(go.Bar(
                name='Cheapest Competitor',
                x=comp_df['Product'],
                y=comp_df['Cheapest Competitor'],
                marker_color='#ff7f0e'
            ))
            
            fig.update_layout(
                title='Your Prices vs Cheapest Competitor Prices (Same Model & Storage)',
                xaxis_title='Product',
                yaxis_title='Price (LKR)',
                barmode='group',
                height=500,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show table
            st.dataframe(comp_df, hide_index=True, use_container_width=True)
        else:
            st.info("No matching competitor products found for comparison")
    else:
        st.warning("Need both your products and competitor products for comparison")

with tab3:
    # Cheapest products per category
    st.subheader("🏆 Best Deals by Category")
    
    if not filtered_competitor_df.empty:
        for category in filtered_competitor_df['category'].unique()[:5]:
            cat_data = filtered_competitor_df[filtered_competitor_df['category'] == category].nsmallest(5, 'price_LKR')
            if not cat_data.empty:
                st.markdown(f"**{category}**")
                st.dataframe(
                    cat_data[['site', 'product', 'price_LKR']].rename(
                        columns={'price_LKR': 'Price (LKR)'}
                    ),
                    hide_index=True,
                    use_container_width=True
                )
    else:
        st.info("No data available")

with tab4:
    # Direct price comparison table
    st.subheader("🔍 Find Best Deals for Specific Products")
    
    if not your_products_df.empty and not competitor_products_df.empty:
        selected_product = st.selectbox(
            "Select your product to compare:",
            your_products_df['product'].tolist()
        )
        
        if selected_product:
            your_prod = your_products_df[your_products_df['product'] == selected_product].iloc[0]
            your_price = your_prod['price_LKR']
            
            my_model = extract_model_number(selected_product)
            my_storage = extract_storage(selected_product)
            
            similar_products = []
            
            for _, comp in competitor_products_df.iterrows():
                comp_model = extract_model_number(comp['product'])
                comp_storage = extract_storage(comp['product'])
                
                if not models_match(my_model, comp_model):
                    continue
                
                if my_storage and comp_storage and my_storage != comp_storage:
                    continue
                
                if comp['price_LKR'] > 0:
                    similar_products.append(comp)
            
            if similar_products:
                similar_df = pd.DataFrame(similar_products)
                
                st.markdown(f"**Your Price:** LKR {your_price:,.0f}")
                st.markdown(f"**Model:** {my_model if my_model else 'N/A'} | **Storage:** {my_storage if my_storage else 'N/A'}")
                st.markdown("**Similar Products from Competitors:**")
                
                comparison_table = similar_df[['site', 'product', 'price_LKR']].copy()
                comparison_table['Price Difference'] = comparison_table['price_LKR'] - your_price
                comparison_table['% Difference'] = ((comparison_table['price_LKR'] - your_price) / your_price * 100).round(1)
                
                comparison_table = comparison_table.sort_values('price_LKR')
                comparison_table.columns = ['Site', 'Product', 'Price (LKR)', 'Diff (LKR)', 'Diff (%)']
                
                st.dataframe(
                    comparison_table,
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info(f"No similar products found for {my_model} {my_storage}")
    else:
        st.warning("Need product data to compare")

# Full data table
st.markdown("---")
st.header("📋 All Competitor Products")

if not filtered_competitor_df.empty:
    st.dataframe(
        filtered_competitor_df[['site', 'category', 'product', 'price_LKR']].sort_values('price_LKR'),
        hide_index=True,
        use_container_width=True
    )
    
    # Download button
    csv = filtered_competitor_df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Data as CSV",
        data=csv,
        file_name=f"competitor_prices_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.info("No data to display")

# Footer
st.markdown("---")
if 'scraped_at' in df.columns and not df.empty:
    st.caption(f"Last updated: {df['scraped_at'].iloc[0]}")
else:
    st.caption("Data timestamp not available")