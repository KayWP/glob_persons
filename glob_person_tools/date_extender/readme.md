# Historical Date Range Expander

Handling dates from the 1600s and earlier is notoriously tricky in standard data environments because many libraries (like Pandas' `Timestamp`) hit a "floor" at the year 1677. This utility bypasses those limits by treating dates as strings and logic-based ranges.

## 🚀 Overview

This script takes partial or full date strings and "expands" them into their logical start and end boundaries. This is ideal for historical research data where precision varies by record.

### Key Features
* **Epoch-Proof:** Works with any year (1000 AD, 1600 AD, etc.) by avoiding nanosecond-limited timestamps.
* **Leap Year Intelligence:** Accurately calculates the last day of February for any given year using `calendar.monthrange`.
* **Zero-Padding:** Ensures all dates are output as `YYYY-MM-DD` for consistent alphabetical sorting.

---

## 📊 Logic Transformation

| Input Format | Example | `_min` Result | `_max` Result | Logic Applied |
| :--- | :--- | :--- | :--- | :--- |
| **Year Only** | `1691` | `1691-01-01` | `1691-12-31` | Full calendar year |
| **Year-Month** | `1708-02` | `1708-02-01` | `1708-02-28` | Start/End of specific month |
| **Full Date** | `1710-05-15` | `1710-05-15` | `1710-05-15` | No expansion needed |

---

## 🛠️ Implementation

### Requirements
* **Python 3.x**
* **Pandas** (for DataFrame handling)

### Sample Code
```python
import pandas as pd
import calendar

def expand_date_logic(date_val):
    if pd.isna(date_val) or str(date_val).strip() == "":
        return None, None
    
    date_str = str(date_val).strip()
    parts = date_str.split('-')
    
    try:
        if len(parts) == 1: # YYYY
            return f"{parts[0]}-01-01", f"{parts[0]}-12-31"
        elif len(parts) == 2: # YYYY-MM
            year, month = int(parts[0]), int(parts[1])
            last_day = calendar.monthrange(year, month)[1]
            return f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last_day}"
        elif len(parts) == 3: # YYYY-MM-DD
            return date_str, date_str
    except:
        return None, None