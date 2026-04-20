import requests
from dotenv import load_dotenv
import os

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
class MovieClient:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
    
    def search_movies(self,  searchText=None):
        url = f"{self.base_url}/movie"
        print(f"Searching for movies: {searchText}")
        query_params = {"searchText": searchText} if searchText else {}
        response = self.session.get(url, params=query_params)
        return response.json()

    def get_movie_details(self, movieId:str):
        url = f"{self.base_url}/movie/{movieId}"
        print(f"Searching for movie details for movie id: {movieId}")
        response = self.session.get(url)
        return response.json()

    def get_movie_shows(self, movieId:str):
        url = f"{self.base_url}/movie/{movieId}/shows"
        print(f"Searching for movie shows for movie id: {movieId}")
        response = self.session.get(url)
        return response.json()
    
    def get_seat_availability(self, showId:str):
        url = f"{self.base_url}/movie/seats/{showId}"
        print(f"Searching seat availibility for show id: {showId}")
        response = self.session.get(url)
        return response.json()

    def book_movie(self, showId: str, noOfSeats: int, seatNumbers: list[str]):
        url = f"{self.base_url}/movie/book"
        body = {
            "showId": showId,
            "noOfSeats": noOfSeats,
            "seatNumbers": seatNumbers
        }
        print(f"Booking movie for id: {showId}")
        response = self.session.post(url, json=body)  # ✅ important
        return response.json()

    def get_user_state(self, user_token:str, device_id: str):
        url = f"{self.base_url}/state"
        print(f"Searching state for user")
        headers = {
        "Authorization": f"Bearer {user_token}",
        "X-Device-Id": device_id
        }
        response = self.session.get(url,headers=headers)
        return response.json()
        
    def update_user_state(self, state,user_token:str, device_id:str):
        url = f"{self.base_url}/state"
        print(f"Updating state for user")
        headers = {
        "Authorization": f"Bearer {user_token}",
        "X-Device-Id": device_id
        }
        response = self.session.post(url, json=state,headers=headers)  # ✅ important
        return response.json()
    
    def get_booking(self, bookingId:str):
        url = f"{self.base_url}/movie/book/{bookingId}"
        print(f"Getting booking for booking id: {bookingId}")
        response = self.session.get(url)
        return response.json()