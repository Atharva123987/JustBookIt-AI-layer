from datetime import datetime, timedelta

def normalize_datetime(intent):
    """
    Convert natural language date from LLM into YYYY-MM-DDTHH:MM:SS format.
    Handles phrases like 'tomorrow night', 'next Friday evening'.
    """
    date_str = intent.get("date", "").lower()
    print(f"Original date: {date_str}")

    if not date_str:
        return ""

    dt = None
 
    # Simple handling for relative keywords
    if "day after tomorrow" in date_str:
        dt = datetime.now() + timedelta(days=2)
    elif "tomorrow" in date_str:
        dt = datetime.now() + timedelta(days=1)
    elif "today" in date_str:
        dt = datetime.now()

    # Assign default time based on 'morning/afternoon/evening/night'
    if dt:
        if "morning" in date_str:
            dt = dt.replace(hour=8, minute=0, second=0)
        elif "afternoon" in date_str:
            dt = dt.replace(hour=14, minute=0, second=0)
        elif "evening" in date_str:
            dt = dt.replace(hour=18, minute=0, second=0)
        elif "night" in date_str:
            dt = dt.replace(hour=20, minute=0, second=0)
        else:
            dt = dt.replace(hour=12, minute=0, second=0)  # default midday

        normalized_datetime = dt.strftime("%Y-%m-%dT%H:%M:%S")
        return normalized_datetime

    # Fallback to dateparser if no relative keyword matched
    try:
        import dateparser
        dt = dateparser.parse(date_str, settings={'PREFER_DATES_FROM':'future'})
        if dt:
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:
        pass

    print(f"Date parsing failed for: {date_str}")
    return ""
