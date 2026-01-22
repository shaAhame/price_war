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
            # Check if it's "1.200" (thousands sep) or "1200.00" (decimal)
            # If 3 digits after dot, it MIGHT be thousands, but usually .00 is 2 digits.
            # Safe bet: python float handles x.y correctly.
            # But "1.200" in LKR usually means 1200. 
            # If we assume standard English locale for LKR:
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

test_cases = [
    ("Rs. 1,200.00", 1200),
    ("LKR 1,200", 1200),
    ("1,200.00", 1200),
    ("120000", 120000), # This should remain 120000 if it's just digits
    ("1,200", 1200),
    ("Rs. 135,000", 135000),
    ("1.250,00", 1250),
    ("invalid", None),
    ("", None),
]

print("Testing parse_price...")
failed = False
for input_str, expected in test_cases:
    result = parse_price(input_str)
    if result != expected:
        print(f"FAILED: '{input_str}' -> {result} (Expected: {expected})")
        failed = True
    else:
        print(f"PASSED: '{input_str}' -> {result}")

if not failed:
    print("\nALL TESTS PASSED")
else:
    print("\nSOME TESTS FAILED")
