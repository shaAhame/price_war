# config.py - Central configuration for all scraping targets

SCRAPING_URLS = {
    # IdealZ (Your Shop)
    "IdealZ All Products": "https://idealzpricelist.netlify.app/",
    
    # LuxuryX.lk
    "LuxuryX Android/Samsung": "https://luxuryx.lk/android-price",
    "LuxuryX Apple iPhone": "https://luxuryx.lk/iphone-price-in-sri-lanka",
    "LuxuryX Apple iPad": "https://luxuryx.lk/ipad-price-in-sri-lanka",
    "LuxuryX MacBook": "https://luxuryx.lk/macbook-price-in-sri-lanka",
    "LuxuryX AirPods": "https://luxuryx.lk/airpod-price-in-sri-lanka",
    
    # Francium.lk
    "Francium iPhone": "https://francium.lk/collections/iphone",
    "Francium iPad": "https://francium.lk/collections/ipad",
    "Francium MacBook": "https://francium.lk/collections/mac",
    "Francium AirPods": "https://francium.lk/collections/airpods",
    "Francium Watch": "https://francium.lk/collections/watch",
    
    # PresentSolution.lk
    "PresentSolution iPhone": "https://presentsolution.lk/product-category/iphone/",
    "PresentSolution iPad": "https://presentsolution.lk/product-category/ipad/",
    "PresentSolution MacBook": "https://presentsolution.lk/product-category/macbook/",
    "PresentSolution AirPods": "https://presentsolution.lk/product-category/airpods/",
    "PresentSolution Watch": "https://presentsolution.lk/product-category/apple-watch/",
    
    # DoctorMobile.lk
    "DoctorMobile iPhone": "https://doctormobile.lk/product-category/iphone/",
    "DoctorMobile Samsung": "https://doctormobile.lk/product-category/samsung/",
    "DoctorMobile iPad": "https://doctormobile.lk/product-category/ipad/",
    "DoctorMobile AirPods": "https://doctormobile.lk/product-category/airpods/",
    "DoctorMobile Watch": "https://doctormobile.lk/product-category/apple-watch/",
    
    # GeniusMobile.lk
    "GeniusMobile iPhone": "https://www.geniusmobile.lk/product-category/iphones/",
    "GeniusMobile Samsung": "https://www.geniusmobile.lk/product-category/samsung/",
    "GeniusMobile iPad": "https://www.geniusmobile.lk/product-category/ipads/",
    "GeniusMobile AirPods": "https://www.geniusmobile.lk/product-category/airpods/",
    
    # LifeMobile.lk
    "LifeMobile iPhone": "https://lifemobile.lk/product-category/iphone/",
    "LifeMobile Samsung": "https://lifemobile.lk/product-category/samsung-phone/",
    "LifeMobile iPad": "https://lifemobile.lk/product-category/ipad/",
    "LifeMobile AirPods": "https://lifemobile.lk/product-category/airpods/",
    "LifeMobile Watch": "https://lifemobile.lk/product-category/apple-watch/",
    
    # GQMobiles.lk
    "GQMobiles iPhone": "https://gqmobiles.lk/product-category/iphone/",
    "GQMobiles Samsung": "https://gqmobiles.lk/product-category/samsung/",
    "GQMobiles iPad": "https://gqmobiles.lk/product-category/ipad/",
    "GQMobiles AirPods": "https://gqmobiles.lk/product-category/airpods/",
    
    # XMobile.lk
    "XMobile iPhone": "https://xmobile.lk/product-category/apple-products/iphone/",
    "XMobile Samsung": "https://xmobile.lk/product-category/samsung/",
    "XMobile iPad": "https://xmobile.lk/product-category/apple-products/ipad/",
    "XMobile AirPods": "https://xmobile.lk/product-category/apple-products/airpods/",
    "XMobile Watch": "https://xmobile.lk/product-category/apple-products/apple-watch/",
}

# Your shop's prices (auto-updated by scraper, or manually maintain as backup)
MY_PRICES = {
    # These will be auto-populated from scraping your website
    # Manually add as backup if IdealZ scraper fails
}

# Email alert settings (optional - for future use)
ALERT_EMAIL = "your-email@gmail.com"
PRICE_THRESHOLD_PERCENT = 5  # Alert if competitor is 5% cheaper