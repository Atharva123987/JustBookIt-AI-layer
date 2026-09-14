import requests
from dotenv import load_dotenv
import os
from typing import List

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
if not BACKEND_URL:
    raise Exception("BACKEND_URL is not set in environment")


class MovieClient:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()

    def _request(self, response):
        try:
            data = response.json()
        except Exception:
            data = response.text

        if response.status_code == 500:
            raise Exception(f"HTTP {response.status_code}: {data}")
        return data

    def search_movies(self, searchText=None, limitResults=True):
        url = f"{self.base_url}/movie"
        print(f"Searching for movies: {searchText}")
        query_params = {"searchText": searchText} if searchText else {}
        query_params["pageSize"] = 99 if not limitResults else None

        response = self.session.get(url, params=query_params, timeout=10)
        return self._request(response)

    def get_movie_details(self, movieId: str):
        url = f"{self.base_url}/movie/{movieId}"
        print(f"Searching for movie details for movie id: {movieId}")
        response = self.session.get(url, timeout=10)
        return self._request(response)

    def get_movie_shows(self, movieId: str):
        url = f"{self.base_url}/movie/{movieId}/shows"
        print(f"Searching for movie shows for movie id: {movieId}")
        response = self.session.get(url, timeout=10)
        return self._request(response)

    def get_seat_availability(self, showId: str):
        url = f"{self.base_url}/movie/seats/{showId}"
        print(f"Searching seat availibility for show id: {showId}")
        response = self.session.get(url, timeout=10)
        return self._request(response)

    def book_movie(self, showId: str, noOfSeats: int, seatNumbers: List[str]):
        url = f"{self.base_url}/movie/book"
        body = {"showId": showId, "noOfSeats": noOfSeats, "seatNumbers": seatNumbers}
        print(f"Booking movie for id: {showId}")
        response = self.session.post(url, json=body, timeout=10)
        return self._request(response)

    def get_user_state(self, user_token: str, device_id: str):
        url = f"{self.base_url}/state"
        print(f"Searching state for user")
        headers = {"Authorization": f"Bearer {user_token}", "X-Device-Id": device_id}
        response = self.session.get(url, headers=headers, timeout=10)
        return self._request(response)

    def update_user_state(self, state, user_token: str, device_id: str):
        url = f"{self.base_url}/state"
        print(f"Updating state for user")
        headers = {"Authorization": f"Bearer {user_token}", "X-Device-Id": device_id}
        response = self.session.post(
            url, json=state, headers=headers, timeout=10
        )  # ✅ important
        return self._request(response)

    def get_booking(self, bookingId: str):
        url = f"{self.base_url}/movie/book/{bookingId}"
        print(f"Getting booking for booking id: {bookingId}")
        response = self.session.get(url, timeout=10)
        return self._request(response)

    def clear_state(self, user_token, device_id):
        url = f"{self.base_url}/state/clear"
        print(f"Clearing state for user")
        headers = {"Authorization": f"Bearer {user_token}", "X-Device-Id": device_id}
        response = self.session.delete(url, headers=headers, timeout=10)
        return self._request(response)

    def create_or_update_knowledge_chunk(self, chunk):
        url = f"{self.base_url}/knowledge"
        print(f"Creating/Updating knowledge chunk")

        response = self.session.patch(url, json=chunk, timeout=10)
        return self._request(response)
