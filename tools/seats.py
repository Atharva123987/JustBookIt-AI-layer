def count_available_seats(show_data):
    count = 0

    data = (show_data or {}).get("data") or {}
    rows = data.get("seat_rows") or []

    for row in rows:
        for seat in row["seats"]:
            if seat["type"] != "AISLE" and seat["status"] == "available":
                count += 1

    return count
