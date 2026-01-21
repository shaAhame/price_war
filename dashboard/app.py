# dashboard/app.py - Streamlit dashboard for price analysis

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
import json

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

def find_price_wars(df, my_prices=None, threshold=5):
    """Find products where competitors are significantly cheaper than your shop"""
    alerts = []
    
    # Get your shop's products from the dataframe
    your_products = df[df['is_own_shop'] == True]
    competitor_products = df[df['is_own_shop'] == False]
    
    if your_products.empty and not my_prices:
        return pd.DataFrame()
    
    if not your_products.empty:
        # Compare your actual scraped products with competitors
        for _, your_product in your_products.iterrows():
            my_name = your_product['product']
            my_price = your_product['price_LKR']
            
            if pd.isna(my_price):
                continue
            
            # Find similar products in competitors
            keywords = [w for w in my_name.split() if len(w) > 3]
            
            for keyword in keywords[:2]:  # Use first 2 meaningful keywords
                matches = competitor_products[
                    competitor_products['product'].str.contains(keyword, case=False, na=False)
                ]
                
                for _, competitor in matches.iterrows():
                    comp_price = competitor['price_LKR']
                    if pd.notna(comp_price) and pd.notna(my_price):
                        price_diff = ((my_price - comp_price) / my_price) * 100
                        
                        if price_diff > threshold:
                            alerts.append({
                                'my_product': my_name,
                                'my_price': my_price,
                                'competitor': competitor['site'],
                                'competitor_product': competitor['product'],
                                'competitor_price': comp_price,
                                'savings_percent': round(price_diff, 1),
                                'savings_amount': my_price - comp_price
                            })
    elif my_prices:
        # Fallback to manual prices if available
        for my_product, my_price in my_prices.items():
            keywords = [w for w in my_product.split() if len(w) > 3]
            
            for keyword in keywords[:2]:
                matches = competitor_products[
                    competitor_products['product'].str.contains(keyword, case=False, na=False)
                ]
                
                for _, row in matches.iterrows():
                    competitor_price = row['price_LKR']
                    if pd.notna(competitor_price):
                        price_diff = ((my_price - competitor_price) / my_price) * 100
                        
                        if price_diff > threshold:
                            alerts.append({
                                'my_product': my_product,
                                'my_price': my_price,
                                'competitor': row['site'],
                                'competitor_product': row['product'],
                                'competitor_price': competitor_price,
                                'savings_percent': round(price_diff, 1),
                                'savings_amount': my_price - competitor_price
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
        # Create comparison chart
        comparison_data = []
        
        for _, your_prod in your_products_df.iterrows():
            # Find cheapest competitor for similar product
            keywords = [w for w in your_prod['product'].split() if len(w) > 3]
            
            min_comp_price = None
            min_comp_site = None
            
            for keyword in keywords[:2]:  # Use first 2 keywords
                matches = competitor_products_df[
                    competitor_products_df['product'].str.contains(keyword, case=False, na=False)
                ]
                
                if not matches.empty:
                    cheapest = matches.loc[matches['price_LKR'].idxmin()]
                    if min_comp_price is None or cheapest['price_LKR'] < min_comp_price:
                        min_comp_price = cheapest['price_LKR']
                        min_comp_site = cheapest['site']
            
            if min_comp_price:
                comparison_data.append({
                    'Product': your_prod['product'][:30] + '...' if len(your_prod['product']) > 30 else your_prod['product'],
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
                title='Your Prices vs Cheapest Competitor Prices',
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
        for category in filtered_competitor_df['category'].unique()[:5]:  # Show top 5 categories
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
            
            # Search for similar products
            keywords = [w for w in selected_product.split() if len(w) > 3]
            
            similar_products = pd.DataFrame()
            for keyword in keywords[:3]:
                matches = competitor_products_df[
                    competitor_products_df['product'].str.contains(keyword, case=False, na=False)
                ]
                similar_products = pd.concat([similar_products, matches])
            
            similar_products = similar_products.drop_duplicates()
            
            if not similar_products.empty:
                st.markdown(f"**Your Price:** LKR {your_price:,.0f}")
                st.markdown("**Similar Products from Competitors:**")
                
                comparison_table = similar_products[['site', 'product', 'price_LKR']].copy()
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
                st.info("No similar products found from competitors")
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