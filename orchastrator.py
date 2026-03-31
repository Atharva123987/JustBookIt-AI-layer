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
class State:
    def __init__(self):
        self.movie = None
        self.time = None
        self.noOfSeats = None
        self.seatNumbers = None
        self.movieId = None
        self.intent = None
        self.showId = None
    
    def SetMovie(self, movie):
        self.movie = movie
    def SetTime(self, time):
        self.time = time
    def SetNoOfSeats(self, noOfSeats):
        self.noOfSeats = noOfSeats
    def SetSeatNumbers(self, seatNumbers):
        self.seatNumbers = seatNumbers
    def SetMovieId(self, movieId):
        self.movieId = movieId
    def SetShowId(self, showId):
        self.showId = showId
    def SetIntent(self, intent):
        self.intent = intent
        
state = State()
def orchastrator(llmIntent, userInput) -> OrchastratorResponse:
    # Returns intent string and data object
    intentFromLLM = llmIntent.get("intent")
    movie = safe_get(userInput, "movie") or safe_get(llmIntent, "movie")
    time = safe_get(userInput, "time") or safe_get(llmIntent, "time")
    noOfSeats = safe_get(userInput, "noOfSeats") or safe_get(llmIntent, "noOfSeats")
    seatNumbers = safe_get(userInput, "seatNumbers") or safe_get(llmIntent, "seatNumbers")
    movieId = safe_get(userInput, "movieId")
    showId = safe_get(userInput, "showId")
    
    if movie:
        state.SetMovie(movie)
    if time:
        state.SetTime(time)
    if noOfSeats:
        state.SetNoOfSeats(noOfSeats)
    if seatNumbers:
        state.SetSeatNumbers(seatNumbers)
    if movieId:
        state.SetMovieId(movieId)
    if showId:
        state.SetShowId(showId)
    
    INVALID_INTENTS = {"unknown", "small_talk", "unsupported_feature"}

    if intentFromLLM:
        if not state.intent:
            # ✅ Always set if state intent is empty
            state.SetIntent(intentFromLLM)
        elif intentFromLLM not in INVALID_INTENTS:
            # ✅ Only overwrite if valid
            state.SetIntent(intentFromLLM)
        
    intent = state.intent
    print("state",state.__dict__)    
    if intent not in ["search_all_movies","movie_show_timetable" ,"query_seat_availability" ,"book_movie","unknown", "unsupported_feature"]:
        raise Exception("Intent is invalid")
    elif intent == "unknown" or intent == "small_talk" or intent == "unsupported_feature":
        return OrchastratorResponse({}, intent)
    elif intent == "search_all_movies":
        print(f"Calling backend API for: {state.movie}")
        api_result = mov.search_movies(state.movie)
        return OrchastratorResponse(api_result, intent)
    elif intent == "need_more_info":
        return OrchastratorResponse({"missing_fields":llmIntent.get("missing_fields")}, intent)
    elif intent == "movie_show_timetable":
        if not state.movieId:
            if not state.movie:
                return OrchastratorResponse({"missing_field":"movie"}, "need_more_info")
            res = mov.search_movies(state.movie)
            state.SetMovieId(res["data"]["movies"][0]["id"])
            
        print(f"Calling backend API for: {state.movieId}")
        res1 = mov.get_movie_details(state.movieId)
        res2 = mov.get_movie_shows(state.movieId)
        api_result = {"movie_details":res1, "show_timings":res2}
        state.SetIntent("unknown")
        return OrchastratorResponse(api_result, intent)
    elif intent == "query_seat_availability":
        # Unhandled
        if not state.showId:
            if not state.movieId:
                if not state.movie:
                    return OrchastratorResponse({"missing_field":"movie"}, "need_more_info")
                res = mov.search_movies(state.movie)
                state.SetMovieId(res["data"]["movies"][0]["id"])
            if not state.time:
                return OrchastratorResponse({"missing_field":"time"}, "need_more_info")
            res2 = mov.get_movie_shows(state.movieId,state.time)
            showType = '3D'
            state.SetShowId(res2["data"][0]["shows"][0][showType][0]['id'])

        res = mov.get_seat_availability(state.showId)
        state.SetIntent("unknown")
        return OrchastratorResponse({"available_seats":count_available_seats(res)},intent)
    elif intent == "book_movie":
        if not state.showId:
            if not state.movieId:
                if not state.movie:
                    return OrchastratorResponse({"missing_field":"movie"}, "need_more_info")
                res = mov.search_movies(state.movie)
                state.SetMovieId(res["data"]["movies"][0]["id"])
            if not state.time:
                return OrchastratorResponse({"missing_field":"time"}, "need_more_info")
            res2 = mov.get_movie_shows(state.movieId,state.time)
            showType = '3D'
            state.SetShowId(res2["data"][0]["shows"][0][showType][0]['id'])
        if not state.noOfSeats:
            return OrchastratorResponse({"missing_field":"noOfSeats"}, "need_more_info")
        res = mov.book_movie(state.showId, state.noOfSeats, state.seatNumbers)
        return OrchastratorResponse(res,intent)
    else:
        raise Exception(f"Intent '{intent}' unhandled")
    # if intent["intent"] in ["search_movies", "shows","movie_details"]:
    #         print(f"Calling backend API for: {intent.get("movie", "")}")
    #         api_result = mov.search_movies(intent.get("movie", ""))
    #     elif intent["intent"] == "seating":
    #         api_result = {}  # placeholder
    #     elif intent["intent"] == "book":
    #         api_result = {}  # placeholder
    #     else:
    #         api_result = {}