import re

def parse_price(price_str):
    """
    Parse a price string into an integer.
    Handles formats like:
    - "Rs. 1,200.00" -> 1200
    - "LKR 1,200" -> 1200
    - "1,200.00" -> 1200
    - "1.200,00" -> 1200
    """
    if not price_str:
        return None
        
    # regex: find substring starting with a digit, containing digits, dots, commas
    match = re.search(r'(\d[\d,.]*)', str(price_str))
    if not match:
        return None
        
    clean_str = match.group(1)
    
    # Remove trailing non-digits (like a trailing dot)
    while clean_str and not clean_str[-1].isdigit():
        clean_str = clean_str[:-1]

    try:
        # Handle "1,200.00" format (common in LK/US)
        if '.' in clean_str and ',' in clean_str:
            if clean_str.rindex('.') > clean_str.rindex(','):
                # Format: 1,200.00 -> Remove comma, then float
                clean_str = clean_str.replace(',', '')
                return int(float(clean_str))
            else:
                # Format: 1.200,00 -> Remove dot, replace comma with dot (European)
                clean_str = clean_str.replace('.', '').replace(',', '.')
                return int(float(clean_str))
        
        # Handle "1200.00"
        elif '.' in clean_str:
            return int(float(clean_str))
        
        # Handle "1,200"
        elif ',' in clean_str:
            clean_str = clean_str.replace(',', '')
            return int(clean_str)
            
        # Handle "1200"
        else:
            return int(clean_str)
            
    except ValueError:
        return None
