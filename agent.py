import requests
import json
from tools.date_normalization import normalize_datetime
from api_client import movie_client
from orchastrator import orchastrator
from orchastrator import OrchastratorResponse
from dotenv import load_dotenv
import os

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
mov =  movie_client.MovieClient()
def call_llm(query: str):
    """Send natural language query to LLM and get structured intent."""
    try:
        response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "openai/gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": 
                        """
                        You are an AI intent extraction assistant for a movie booking system.

                        Your job is to:
                        1. Understand the user query
                        2. Identify the user intent
                        3. Extract relevant fields

                        ---

                        ### INTENTS:
                        search_all_movies
                        movie_show_timetable
                        query_seats
                        book_movie
                        small_talk
                        unknown

                        ---

                        ### CRITICAL RULE:
                        Even if required information (movie, time, seats) is missing,
                        you MUST still return the correct intent.

                        DO NOT return "unknown" just because the query is incomplete.

                        ---

                        ### RULES:
                        - DO NOT explain anything
                        - Output ONLY valid JSON
                        - Extract fields ONLY if explicitly mentioned
                        - If a field is not present, return null
                        - DO NOT assume or generate values
                        - DO NOT depend on previous conversation

                        ---

                        ### FIELD DEFINITIONS:
                        - movie → name of movie (if explicitly mentioned)
                        - time → datetime in ISO format (ONLY if clearly mentioned)
                        - noOfSeats → number of seats
                        - seatNumbers → specific seat numbers (like ["A1", "A2"])

                        ---

                        ### SEAT SELECTION RULE:
                        - "noOfSeats" = number of seats required
                        - "seatNumbers" is OPTIONAL
                        - If "seatNumbers" is present → use those seats
                        - If null → system will auto-assign seats
                        - NEVER generate seatNumbers yourself
                        - NEVER generate time yourself
                        - NEVER generate movie yourself

                        ---

                        ### INTENT GUIDELINES:

                        - search_all_movies → user wants to browse/search movies
                        - movie_show_timetable → user wants show timings (even if movie/time missing)
                        - query_seats → user wants to select seats or view seating layout for a show
                        - book_movie → user wants to book tickets
                        - small_talk → greetings, thanks, personal questions
                        - unsupported_feature → valid request but not supported (e.g. theatres near me)
                        - unknown → unclear or unrelated input

                        ---

                        ### UNKNOWN INTENT:
                        Use "unknown" ONLY when:
                        - query is meaningless OR
                        - not related to movie booking

                        If entities are present, still extract them.

                        ---

                        ### OUTPUT FORMAT:
                        {
                        "intent": "search_all_movies | movie_show_timetable | query_seats | book_movie | get_booking | small_talk | unknown",
                        "movie": "string or null",
                        "time": "ISO datetime or null",
                        "noOfSeats": number or null,
                        "seatNumbers": ["A1", "A2"] or null
                        }

                        ---

                        ### EXAMPLES:

                        User: "Show all movies"
                        User: "Show me all movies near me."
                        User: "Show me movies"
                        User: "Show me all movies" etc.
                        Output:
                        {
                        "intent": "search_all_movies",
                        "movie": null,
                        "time": null,
                        "noOfSeats": null,
                        "seatNumbers": null
                        }

                        ---
                        User: "Show batman movies"
                        Output:
                        {
                        "intent": "search_all_movies",
                        "movie": "batman",
                        "time": null,
                        "noOfSeats": null,
                        "seatNumbers": null
                        }

                        ---

                        User: "Show movie timetable"
                        Output:
                        {
                        "intent": "movie_show_timetable",
                        "movie": null,
                        "time": null,
                        "noOfSeats": null,
                        "seatNumbers": null
                        }

                        ---

                        User: "Show shows today"
                        Output:
                        {
                        "intent": "movie_show_timetable",
                        "movie": null,
                        "time": "2026-03-26",
                        "noOfSeats": null,
                        "seatNumbers": null
                        }

                        ---

                        User: "Show shows for Dune"
                        Output:
                        {
                        "intent": "movie_show_timetable",
                        "movie": "Dune",
                        "time": null,
                        "noOfSeats": null,
                        "seatNumbers": null
                        }

                        ---

                        User: "Show shows for Dune today"
                        Output:
                        {
                        "intent": "movie_show_timetable",
                        "movie": "Dune",
                        "time": "2026-03-26",
                        "noOfSeats": null,
                        "seatNumbers": null
                        }

                        ---
                        
                        User: "Show seats"
                        Output:
                        {
                        "intent": "query_seats",
                        "movie": null,
                        "time": null,
                        "noOfSeats": null,
                        "seatNumbers": null
                        }

                        ---

                        User: "Book 3 tickets"
                        User: "Complete payment"
                        Output:
                        {
                        "intent": "book_movie",
                        "movie": null,
                        "time": null,
                        "noOfSeats": 3,
                        "seatNumbers": null
                        }

                        ---

                        User: "Dune"
                        Output:
                        {
                        "intent": "unknown",
                        "movie": "Dune",
                        "time": null,
                        "noOfSeats": null,
                        "seatNumbers": null
                        }
                        
                        User: "3"
                        Output:
                        {
                        "intent": "unknown",
                        "movie": null,
                        "time": null,
                        "noOfSeats": 3,
                        "seatNumbers": null
                        }

                        ---
                        
                        User: "A2, J2"
                        Output:
                        {
                        "intent": "unknown",
                        "movie": null,
                        "time": null,
                        "noOfSeats": null,
                        "seatNumbers": ["A2","J2"]
                        }

                        ---

                        User: "Hi"
                        Output:
                        {
                        "intent": "small_talk",
                        "movie": null,
                        "time": null,
                        "noOfSeats": null,
                        "seatNumbers": null
                        }

                        ---

                        
                        User: "Get my booking"
                        Output:
                        {
                        "intent": "get_booking",
                        "movie": null,
                        "time": null,
                        "noOfSeats": null,
                        "seatNumbers": null
                        }
                        
                        
                """
                },
                {"role": "user", "content": query}
            ],
            "temperature": 0.2
        })
    )
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error: {e}"

def generate_chatbot_response(o: OrchastratorResponse, q:str):
    """Ask LLM to turn raw API JSON into a natural language chatbot response."""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "openai/gpt-4o-mini",  # smaller + cheaper model for formatting
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            """
                                You are a movie booking assistant responsible for generating natural, conversational responses.

                                You will be given:
                                - An "intent" field
                                - A "data" object containing backend API response
                                - Original user query, use it to make responses more natural and context-aware, especially for small talk.

                                IMPORTANT:
                                The frontend (UI) will render all actual data (movies, shows, seats, booking details) using the "data" field.
                                Your job is ONLY to generate a conversational message to guide the user.

                                ---

                                ### CORE RULES:
                                - DO NOT list or display any data from the "data" object
                                - DO NOT repeat movie names, show timings, seat numbers, or booking details
                                - DO NOT include raw JSON or technical field names
                                - Keep responses short, natural, and user-friendly
                                - Focus on guiding the user on what they are seeing or what to do next

                                ---

                                ### INTENT-BASED RESPONSE GUIDELINES:

                                1. search_all_movies:
                                - Example tone:
                                "Here are the movies currently playing."

                                ---

                                2. movie_show_timetable:
                                - Example tone:
                                "Here are the available show timings."

                                ---

                                3. query_seats:
                                - Example tone:
                                "Here is the live seating layout for The Dark Knight. Pick any available seats or type them in chat like A1, A2."

                                ---


                                4. book_movie:
                                - If booking is created:
                                - If payment is pending:
                                    "Your booking has been created. Please complete the payment to confirm it."
                                - If payment is successful:
                                    "Your booking is confirmed. Enjoy your movie!"

                                ---

                                5. need_more_info:
                                - Ask for missing fields naturally
                                Example missing_field prompts:
                                movie → "Which movie would you like?"
                                time → "What time would you prefer?"
                                noOfSeats → "How many seats would you like to book?"
                                showId → "Please select the show you would like to book"
                                
                                6. unknown:
                                - If the user query is unclear or cannot be understood, respond politely and guide the user with examples of valid requests.
                                - Keep the tone friendly and helpful.
                                - Check the user query and respond in that context
                                Example:
                                "I’m not sure I understood that. You can try asking something like:
                                • 'Show me all movies playing today'
                                • 'Show shows for Dune this evening'
                                • 'Book 3 tickets for Dune at 5 PM today'"

                                7. small_talk:
                                - Respond naturally to casual or personal questions about the assistant
                                - Keep it short and friendly
                                - Example:
                                User - "Who are you?"
                                Chatbot - "I’m your movie booking assistant! I can help you find movies, check showtimes, and book tickets."


                                8. get_booking:
                                Retrieve booking details for the user
                                If bookingId is provided → fetch that specific booking
                                If not → return user’s recent bookings or ask for booking ID
                                Handle missing data gracefully
                                Keep response concise and helpful

                                Example (with bookingId):
                                “Here are your booking details: 2 seats for Oppenheimer at 7:30 PM. Enjoy your movie!”
                                
                                Example (no bookings found):
                                “I couldn’t find any bookings for you. Would you like to book a movie instead?”
                                
                                ### ADDITIONAL GUIDELINES:
                                - Do not assume or invent any missing details
                                - Do not mention internal fields like booking_id, payment_id, etc.
                                - Keep responses concise (1–2 sentences max)
                                - Maintain a friendly and helpful tone

                                ---

                                ### OUTPUT FORMAT:
                                Return ONLY plain text. No JSON."""
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"""
                            User query: {q}

                            Intent: {o.intent}

                            Data: {json.dumps(o.__dict__)}

                            Generate a conversational response based on the intent and user query.
                            """
                        )
                    }
                ],
                "temperature": 0.4
            })
        )
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "Sorry, I couldn't generate a response.")
    except Exception as e:
        return f"Error generating response: {e}"


# def format_response(api_response: dict):
#     # --- Raw API response ---
#     raw_data = api_response.get("data", {}).get("movies", [])

#     # --- Chatbot friendly response ---
#     if not raw_data:
#         chatbot_text = "❌ No movies found."
#     else:
#         chatbot_text = "🎬 Here are some movies:\n\n"
#         for m in raw_data:
#             title = m["title"]
#             year = m["release_date"].split("-")[0] if m.get("release_date") else "N/A"
#             poster = m.get("poster_url", "")
#             chatbot_text += f"• {title} ({year})\nPoster: {poster}\n\n"

#     return {
#         "raw": api_response,      # keep original API data
#         "chat_message": chatbot_text  # friendly text for chat
#     }


class ProcessQueryResponse:
    def __init__(self, data=None,intent="",chat_response="Sorry there is something wrong, please try again!"):
        self.api_data = data
        self.intent = intent
        self.chat_response = chat_response

async def process_query(query: str, user_token: str = None, userInput: dict = None,device_id:str = None) -> ProcessQueryResponse:
    try:
        intent_json = call_llm(query)
        print(f"Raw LLM response: {intent_json}")

        # cleanup JSON
        if intent_json.startswith("```"):
            intent_json = intent_json.strip("`").replace("json\n", "").replace("json", "", 1).strip()
        intent = json.loads(intent_json)

        # call backend APIs
        o = orchastrator(user_token, intent, userInput, device_id)
        
        chat_response = generate_chatbot_response(o, query)
            
        response = ProcessQueryResponse(
            intent=o.intent,
        )
        if chat_response:
            response.chat_response = chat_response
        if o.data:
            response.api_data = o.data
        # format into human-readable text
        return response

    except Exception as e:
        return f"⚠️ Error: {e}"
