def count_available_seats(show_data):
    count = 0

    rows = show_data["data"]["seat_rows"]

    for row in rows:
        for seat in row["seats"]:
            if seat["type"] != "AISLE" and seat["status"] == "available":
                count += 1

    return count