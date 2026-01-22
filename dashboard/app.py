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
    """Extract model number with variant (e.g., '17 pro max', '15', '16 plus')"""
    product_lower = product_name.lower()
    
    # iPhone patterns
    iphone_pattern = r'iphone\s+(\d+(?:\s*(?:pro\s*max|pro|plus|mini|e))?)'
    match = re.search(iphone_pattern, product_lower)
    if match:
        model = match.group(1).strip()
        # Normalize spacing
        model = re.sub(r'\s+', ' ', model)
        return model
    
    # iPad patterns
    if 'ipad' in product_lower:
        ipad_pattern = r'ipad\s+(\w+(?:\s+\w+)*)'
        match = re.search(ipad_pattern, product_lower)
        if match:
            return match.group(1).strip()
    
    # MacBook patterns
    if 'macbook' in product_lower:
        mac_pattern = r'macbook\s+(\w+(?:\s+\w+)*)'
        match = re.search(mac_pattern, product_lower)
        if match:
            return match.group(1).strip()
    
    # AirPods patterns
    if 'airpod' in product_lower:
        airpod_pattern = r'airpods?\s+(\w+(?:\s+\w+)*)'
        match = re.search(airpod_pattern, product_lower)
        if match:
            return match.group(1).strip()
    
    # Watch patterns
    if 'watch' in product_lower:
        watch_pattern = r'watch\s+(\w+(?:\s+\w+)*)'
        match = re.search(watch_pattern, product_lower)
        if match:
            return match.group(1).strip()
    
    return None

def extract_storage(product_name):
    """Extract storage capacity (e.g., '128GB', '256GB', '1TB')"""
    # Look for storage patterns
    storage_pattern = r'(\d+\s*(?:GB|TB))'
    match = re.search(storage_pattern, product_name, re.IGNORECASE)
    
    if match:
        storage = match.group(1).upper().replace(' ', '')
        return storage
    
    return None

def normalize_storage(storage):
    """Normalize storage format (e.g., '1TB' -> '1024GB' for comparison)"""
    if not storage:
        return None
    
    storage_upper = storage.upper()
    
    if 'TB' in storage_upper:
        # Convert TB to GB
        tb_value = int(re.findall(r'\d+', storage_upper)[0])
        return f"{tb_value * 1024}GB"
    
    return storage_upper

def models_match(model1, model2):
    """Check if two model numbers match exactly"""
    if not model1 or not model2:
        return False
    
    # Normalize
    m1 = model1.lower().strip()
    m2 = model2.lower().strip()
    
    # Remove extra spaces
    m1 = re.sub(r'\s+', ' ', m1)
    m2 = re.sub(r'\s+', ' ', m2)
    
    # Exact match
    if m1 == m2:
        return True
    
    # Remove all spaces for comparison
    m1_nospace = m1.replace(' ', '')
    m2_nospace = m2.replace(' ', '')
    
    return m1_nospace == m2_nospace

def find_price_wars(df, my_prices=None, threshold=5):
    """Find products where competitors are significantly cheaper - with simplistic matching"""
    alerts = []
    
    your_products = df[df['is_own_shop'] == True].copy()
    competitor_products = df[df['is_own_shop'] == False].copy()
    
    # Filter out zero prices
    your_products = your_products[your_products['price_LKR'] > 0]
    competitor_products = competitor_products[competitor_products['price_LKR'] > 0]
    
    if your_products.empty:
        return pd.DataFrame()
    
    for _, your_product in your_products.iterrows():
        my_name = your_product['product']
        my_price = your_product['price_LKR']
        
        # Extract details
        my_model = extract_model_number(my_name)
        my_storage = extract_storage(my_name)
        
        if not my_model:
            continue
        
        # Find partial matches
        for _, competitor in competitor_products.iterrows():
            comp_name = competitor['product']
            comp_price = competitor['price_LKR']
            
            # Simple containment check
            # e.g. if "iPhone 13" is in competitor name
            if my_model.lower() in comp_name.lower():
                
                # If I have storage defined, competitor must match it if they have it
                comp_storage = extract_storage(comp_name)
                if my_storage and comp_storage:
                     if normalize_storage(my_storage) != normalize_storage(comp_storage):
                        continue
                
                # Calculate price difference
                price_diff = ((my_price - comp_price) / my_price) * 100
                
                # Only show significant and realistic differences
                if threshold < price_diff < 95:
                    alerts.append({
                        'my_product': my_name,
                        'my_price': my_price,
                        'competitor': competitor['site'],
                        'competitor_product': comp_name,
                        'competitor_price': comp_price,
                        'savings_percent': round(price_diff, 1),
                        'savings_amount': my_price - comp_price,
                        'model': my_model,
                        'storage': my_storage
                    })
    
    return pd.DataFrame(alerts).drop_duplicates() if alerts else pd.DataFrame()

# Main app
st.title("📊 IdealZ Competitor Price Monitor")
st.markdown("**Real-time price comparison with competitors**")
st.markdown("---")

# Load data
df = load_data()
my_prices_json = load_my_prices()

if df.empty:
    st.error("⚠️ No data available. Please run the scraper first!")
    st.info("Run: `python scraper/main_scraper.py`")
    st.stop()

# Clean data - remove zero prices
df = df[df['price_LKR'] > 0]

# Separate your shop from competitors
your_products_df = df[df['is_own_shop'] == True]
competitor_products_df = df[df['is_own_shop'] == False]

# Sidebar filters
st.sidebar.header("🔍 Filters")

all_sites = sorted(competitor_products_df['site'].unique()) if not competitor_products_df.empty else []
sites = st.sidebar.multiselect(
    "Competitor Sites", 
    all_sites,
    default=all_sites
)

all_categories = sorted(df['category'].unique())
categories = st.sidebar.multiselect(
    "Categories", 
    all_categories,
    default=all_categories
)

if not competitor_products_df.empty:
    min_price = int(competitor_products_df['price_LKR'].min())
    max_price = int(competitor_products_df['price_LKR'].max())
    
    # Set reasonable default range (exclude outliers)
    q1 = competitor_products_df['price_LKR'].quantile(0.25)
    q3 = competitor_products_df['price_LKR'].quantile(0.75)
    
    price_range = st.sidebar.slider(
        "Price Range (LKR)", 
        min_price,
        max_price,
        (min_price, max_price)
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
    st.metric("Sites Monitored", df['site'].nunique())
with col4:
    if not filtered_competitor_df.empty:
        avg_price = filtered_competitor_df['price_LKR'].median()  # Use median to avoid outliers
        st.metric("Median Competitor Price", f"LKR {avg_price:,.0f}")
    else:
        st.metric("Median Competitor Price", "N/A")

# Price War Alerts
st.markdown("---")
st.header("🚨 Price War Alerts")

alerts_df = find_price_wars(df, my_prices_json, threshold=5)

if not alerts_df.empty:
    # Sort by savings percent
    alerts_df = alerts_df.sort_values('savings_percent', ascending=False)
    
    st.markdown(f'<div class="alert-box alert-danger">⚠️ <b>{len(alerts_df)} exact matches found where competitors are cheaper!</b></div>', 
                unsafe_allow_html=True)
    
    # Show alerts in a cleaner format
    for idx, alert in alerts_df.head(15).iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                **{alert['my_product']}** (LKR {alert['my_price']:,.0f})  
                vs **{alert['competitor']}**: {alert['competitor_product']} (LKR {alert['competitor_price']:,.0f})
                """)
            
            with col2:
                st.error(f"**{alert['savings_percent']:.1f}% cheaper**  \n💰 Save LKR {alert['savings_amount']:,.0f}")
            
            st.divider()
else:
    st.markdown('<div class="alert-box alert-success">✅ Your pricing is competitive! No exact matches found where competitors are significantly cheaper.</div>', 
                unsafe_allow_html=True)

# Visualizations
st.markdown("---")
st.header("📈 Price Analysis")

tab1, tab2, tab3, tab4 = st.tabs(["🏪 Your vs Competitors", "📊 By Category", "🔍 Product Finder", "📝 Raw Data"])

with tab4:
    st.subheader("📝 Raw Data Inspector")
    st.markdown("Use this to check if prices are being parsed correctly.")
    
    if not df.empty:
        st.dataframe(
            df.sort_values(by=['site', 'product']), 
            use_container_width=True,
            column_config={
                "price_LKR": st.column_config.NumberColumn(
                    "Price (LKR)",
                    format="LKR %d"
                )
            }
        )
    else:
        st.info("No data available.")

with tab1:
    st.subheader("Price Comparison: Same Model & Storage")
    
    if not your_products_df.empty and not competitor_products_df.empty:
        comparison_data = []
        
        for _, your_prod in your_products_df.iterrows():
            my_model = extract_model_number(your_prod['product'])
            my_storage = extract_storage(your_prod['product'])
            
            if not my_model:
                continue
            
            # Find cheapest exact match
            min_price = None
            min_site = None
            
            for _, comp in competitor_products_df.iterrows():
                comp_model = extract_model_number(comp['product'])
                comp_storage = extract_storage(comp['product'])
                
                if not models_match(my_model, comp_model):
                    continue
                
                # Storage must match
                if my_storage and comp_storage:
                    if normalize_storage(my_storage) != normalize_storage(comp_storage):
                        continue
                elif my_storage or comp_storage:
                    continue
                
                if min_price is None or comp['price_LKR'] < min_price:
                    min_price = comp['price_LKR']
                    min_site = comp['site']
            
            if min_price:
                product_label = f"{my_model.upper()}"
                if my_storage:
                    product_label += f" {my_storage}"
                
                comparison_data.append({
                    'Product': product_label,
                    'Your Price': your_prod['price_LKR'],
                    'Best Competitor': min_price,
                    'Site': min_site,
                    'Difference': your_prod['price_LKR'] - min_price
                })
        
        if comparison_data:
            comp_df = pd.DataFrame(comparison_data)
            
            # Chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Your Price',
                x=comp_df['Product'],
                y=comp_df['Your Price'],
                marker_color='#2196F3',
                text=comp_df['Your Price'].apply(lambda x: f'LKR {x:,.0f}'),
                textposition='outside'
            ))
            fig.add_trace(go.Bar(
                name='Best Competitor',
                x=comp_df['Product'],
                y=comp_df['Best Competitor'],
                marker_color='#FF9800',
                text=comp_df['Best Competitor'].apply(lambda x: f'LKR {x:,.0f}'),
                textposition='outside'
            ))
            
            fig.update_layout(
                title='Your Prices vs Best Competitor (Exact Matches Only)',
                xaxis_title='Product (Model + Storage)',
                yaxis_title='Price (LKR)',
                barmode='group',
                height=500,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Table
            st.dataframe(
                comp_df.style.apply(
                    lambda x: ['background-color: #ffebee' if v > 0 else 'background-color: #e8f5e9' for v in x], 
                    subset=['Difference']
                ),
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No exact competitor matches found for your products")
    else:
        st.warning("Need both your products and competitor data")

with tab2:
    st.subheader("Average Prices by Category")
    
    if not filtered_competitor_df.empty:
        cat_avg = filtered_competitor_df.groupby('category')['price_LKR'].agg(['mean', 'count']).reset_index()
        cat_avg.columns = ['Category', 'Avg Price', 'Count']
        
        fig = px.bar(
            cat_avg, 
            x='Category', 
            y='Avg Price',
            text='Count',
            title='Average Competitor Prices by Category',
            labels={'Avg Price': 'Average Price (LKR)', 'Count': 'Products'}
        )
        fig.update_traces(texttemplate='%{text} products', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, height=500)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(cat_avg, hide_index=True, use_container_width=True)
    else:
        st.info("No data available")

with tab3:
    st.subheader("🔍 Find Competitor Prices for Your Products")
    
    if not your_products_df.empty:
        selected = st.selectbox(
            "Select your product:",
            your_products_df['product'].tolist(),
            index=0
        )
        
        if selected:
            your_prod = your_products_df[your_products_df['product'] == selected].iloc[0]
            your_price = your_prod['price_LKR']
            
            my_model = extract_model_number(selected)
            my_storage = extract_storage(selected)
            
            st.info(f"**Model:** {my_model.upper() if my_model else 'Unknown'} | **Storage:** {my_storage if my_storage else 'N/A'} | **Your Price:** LKR {your_price:,.0f}")
            
            # Find exact matches
            matches = []
            for _, comp in competitor_products_df.iterrows():
                comp_model = extract_model_number(comp['product'])
                comp_storage = extract_storage(comp['product'])
                
                if not models_match(my_model, comp_model):
                    continue
                
                if my_storage and comp_storage:
                    if normalize_storage(my_storage) != normalize_storage(comp_storage):
                        continue
                elif my_storage or comp_storage:
                    continue
                
                matches.append({
                    'Site': comp['site'],
                    'Product': comp['product'],
                    'Price (LKR)': comp['price_LKR'],
                    'Difference (LKR)': comp['price_LKR'] - your_price,
                    'Difference (%)': round(((comp['price_LKR'] - your_price) / your_price) * 100, 1)
                })
            
            if matches:
                match_df = pd.DataFrame(matches).sort_values('Price (LKR)')
                
                st.success(f"Found {len(matches)} exact matches!")
                st.dataframe(match_df, hide_index=True, use_container_width=True)
            else:
                st.warning("No exact competitor matches found for this product")

# All Products Table
st.markdown("---")
st.header("📋 All Products")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Your Products")
    if not your_products_df.empty:
        st.dataframe(
            your_products_df[['product', 'price_LKR']].rename(columns={'price_LKR': 'Price (LKR)'}),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No products from your shop")

with col2:
    st.subheader("Competitor Products")
    if not filtered_competitor_df.empty:
        display_df = filtered_competitor_df[['site', 'product', 'price_LKR']].sort_values('price_LKR')
        display_df.columns = ['Site', 'Product', 'Price (LKR)']
        
        st.dataframe(display_df, hide_index=True, use_container_width=True, height=400)
        
        # Download
        csv = filtered_competitor_df.to_csv(index=False)
        st.download_button(
            "⬇️ Download CSV",
            csv,
            f"competitors_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )
    else:
        st.info("No competitor data")

# Footer
st.markdown("---")
if 'scraped_at' in df.columns and not df.empty:
    st.caption(f"📅 Last updated: {df['scraped_at'].iloc[0]}")