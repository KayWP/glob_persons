import pandas as pd
import calendar

def expand_date_logic(date_val):
    """
    Parses a date string and returns (min_date, max_date).
    Supports: 
    - YYYY -> (YYYY-01-01, YYYY-12-31)
    - YYYY-MM -> (YYYY-MM-01, YYYY-MM-LastDay)
    - YYYY-MM-DD -> (YYYY-MM-DD, YYYY-MM-DD)
    """
    if pd.isna(date_val) or str(date_val).strip() == "":
        return None, None
    
    date_str = str(date_val).strip()
    parts = date_str.split('-')
    
    try:
        # Case 1: Year only (e.g., "1691")
        if len(parts) == 1:
            year = int(parts[0])
            return f"{year}-01-01", f"{year}-12-31"
        
        # Case 2: Year and Month (e.g., "1708-02")
        elif len(parts) == 2:
            year, month = int(parts[0]), int(parts[1])
            last_day = calendar.monthrange(year, month)[1]
            return f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last_day}"
        
        # Case 3: Specific Day (e.g., "1710-05-15")
        elif len(parts) == 3:
            # Min and Max are the same for a specific day
            return date_str, date_str
            
    except (ValueError, IndexError):
        # Handles cases where input might be malformed
        return None, None

    return None, None

# --- Application to your DataFrame ---

# Example data including a full date
data = {
    'startDate': ["1691", "1708-02", "1710-05-15", "1719"],
    'endDate': ["1691", "1708-02", "1710-05-15", "1719"]
}
df = pd.DataFrame(data)

# Apply the logic to both startDate and endDate
for col in ['startDate', 'endDate']:
    results = df[col].apply(expand_date_logic)
    df[f'{col}_min'] = results.apply(lambda x: x[0])
    df[f'{col}_max'] = results.apply(lambda x: x[1])

# Displaying the result
print(df.to_string())