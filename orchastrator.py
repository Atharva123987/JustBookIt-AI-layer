from api_client import movie_client
from tools.seats import count_available_seats
state = {}
mov =  movie_client.MovieClient()

class OrchastratorResponse:
    def __init__(self, data:dict, intent:str):
        self.data = data
        self.intent = intent

def safe_get(obj, key):
        if not obj:
            return None
        return obj.get(key) if isinstance(obj, dict) else getattr(obj, key, None)

def get_state(user_token, device_id):
    res = mov.get_user_state(user_token, device_id)
    data = res.get("data", {}) if res else {}
    return State.from_dict(data)


def update_state(user_token, state, device_id):
    mov.update_user_state(state.to_dict(),user_token,device_id)

def should_reset(old_intent, new_intent):
    INVALID = {"unknown", "small_talk", "unsupported_feature"}

    if not new_intent or new_intent in INVALID:
        return False

    return old_intent and old_intent != new_intent
    
class State:
    def __init__(self):
        self.movie = None
        self.noOfSeats = None
        self.seatNumbers = None
        self.movieId = None
        self.intent = None
        self.showId = None
        self.bookingId = None

    def SetMovie(self, movie): self.movie = movie
    def SetNoOfSeats(self, noOfSeats): self.noOfSeats = noOfSeats
    def SetSeatNumbers(self, seatNumbers): self.seatNumbers = seatNumbers
    def SetMovieId(self, movieId): self.movieId = movieId
    def SetShowId(self, showId): self.showId = showId
    def SetBookingId(self, bookingId): self.bookingId = bookingId
    def SetIntent(self, intent): self.intent = intent

    def to_dict(self):
        return {
            "movie": self.movie,
            "noOfSeats": self.noOfSeats,
            "seatNumbers": self.seatNumbers,
            "movieId": self.movieId,
            "intent": self.intent,
            "showId": self.showId,
        }

    @staticmethod
    def from_dict(data):
        s = State()
        if not data:
            return s

        s.movie = data.get("movie")
        s.noOfSeats = data.get("noOfSeats")
        s.seatNumbers = data.get("seatNumbers")
        s.movieId = data.get("movieId")
        s.intent = data.get("intent")
        s.showId = data.get("showId")
        s.bookingId = data.get("bookingId")
        return s    
    
def orchastrator(user_token, llmIntent, userInput, device_id) -> OrchastratorResponse:
    state = get_state(user_token,device_id)

    intentFromLLM = llmIntent.get("intent")

    # ---- extract fields ----
    movie = safe_get(userInput, "movie") or safe_get(llmIntent, "movie")
    noOfSeats = safe_get(userInput, "noOfSeats") or safe_get(llmIntent, "noOfSeats")
    seatNumbers = safe_get(userInput, "seatNumbers") or safe_get(llmIntent, "seatNumbers")
    movieId = safe_get(userInput, "movieId")
    showId = safe_get(userInput, "showId")
    bookingId = safe_get(userInput, "bookingId")

    

    INVALID_INTENTS = {"unknown", "small_talk", "unsupported_feature"}

    if intentFromLLM:
        if not state.intent or intentFromLLM not in INVALID_INTENTS:
            state.SetIntent(intentFromLLM)

    intent = state.intent
    print("state", state.__dict__)
    
    # ---- update state ----
    if movie: state.SetMovie(movie)
    if noOfSeats: state.SetNoOfSeats(noOfSeats)
    if seatNumbers: state.SetSeatNumbers(seatNumbers)
    if movieId: state.SetMovieId(movieId)
    if showId: state.SetShowId(showId)

    # ---- handle intents ----
    if intent in {"unknown", "small_talk", "unsupported_feature"}:
        update_state(user_token, state,device_id)
        return OrchastratorResponse({}, intent)

    if intent == "search_all_movies":
        res = mov.search_movies(state.movie)
        update_state(user_token, state,device_id)
        return OrchastratorResponse(res, intent)

    if intent == "need_more_info":
        update_state(user_token, state,device_id)
        return OrchastratorResponse(
            {"missing_fields": llmIntent.get("missing_fields")},
            intent,
        )

    if intent == "movie_show_timetable":
        if not state.movieId:
            if not state.movie:
                update_state(user_token, state,device_id)
                return OrchastratorResponse({"missing_field": "movie"}, "need_more_info")

            res = mov.search_movies(state.movie)
            state.SetMovieId(res["data"]["movies"][0]["id"])

        res1 = mov.get_movie_details(state.movieId)
        res2 = mov.get_movie_shows(state.movieId)

        state.SetIntent("unknown")
        update_state(user_token, state,device_id)

        return OrchastratorResponse(
            {"movie_details": res1, "show_timings": res2},
            intent,
        )

    if intent == "query_seat_availability":
        if not state.movie:
            update_state(user_token, state,device_id)
            return OrchastratorResponse({"missing_field": "movie"}, "need_more_info")

        if not state.movieId:
            res = mov.search_movies(state.movie)
            state.SetMovieId(res["data"]["movies"][0]["id"])

        if not state.showId:
            res2 = mov.get_movie_shows(state.movieId)
            state.SetShowId(res2["data"][0]["shows"][0]["3D"][0]["id"])

        res = mov.get_seat_availability(state.showId)

        state.SetIntent("unknown")
        update_state(user_token, state,device_id)

        return OrchastratorResponse(
            {"available_seats": count_available_seats(res)},
            intent,
        )

    if intent == "book_movie":
        if not state.noOfSeats:
            update_state(user_token, state,device_id)
            return OrchastratorResponse({"missing_field": "noOfSeats"}, "need_more_info")

        if not state.movieId:
            if not state.movie:
                return OrchastratorResponse({"missing_field": "movie"}, "need_more_info")
            res = mov.search_movies(state.movie)
            state.SetMovieId(res["data"]["movies"][0]["id"])

        if not state.showId:
            res2 = mov.get_movie_shows(state.movieId)
            state.SetShowId(res2["data"][0]["shows"][0]["3D"][0]["id"])

        res = mov.book_movie(state.showId, state.noOfSeats, state.seatNumbers)
        state = State()
        update_state(user_token, state,device_id)
        return OrchastratorResponse(res, intent)

    if intent == "get_booking":
        if not bookingId:
            return OrchastratorResponse({"missing_field": "bookingId"}, "need_more_info") 

        res = mov.get_booking(bookingId)
        state.SetIntent("unknown")
        update_state(user_token,state)
        return OrchastratorResponse(res, intent)
    raise Exception(f"Intent '{intent}' unhandled")