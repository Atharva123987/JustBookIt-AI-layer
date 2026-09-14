import datetime

import requests
import json
from tools.date_normalization import normalize_datetime
from api_client import movie_client, embedding_client
from orchastrator import orchastrator
from orchastrator import OrchastratorResponse
from dotenv import load_dotenv
import os

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")
mov = movie_client.MovieClient()


def call_llm(query: str):
    """Send natural language query to LLM and get structured intent."""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps(
                {
                    "model": LLM_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": """
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
                        
                        
                """,
                        },
                        {"role": "user", "content": query},
                    ],
                    "temperature": 0.2,
                }
            ),
        )
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error: {e}"


def generate_chatbot_response(o: OrchastratorResponse, q: str):
    """Ask LLM to turn raw API JSON into a natural language chatbot response."""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps(
                {
                    "model": LLM_MODEL,  # smaller + cheaper model for formatting
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                """
                        You are a movie booking assistant responsible for generating natural,
                        conversational responses.

                        You will be given:
                        - An "intent" field
                        - A "data" object containing the backend API response
                        - The original user query

                        IMPORTANT:
                        The frontend (UI) will render all actual data (movies, shows, seats,
                        booking details) using the "data" field.

                        Your job is ONLY to generate a short conversational message that guides
                        the user.

                        ---

                        ### CORE RULES:

                        - DO NOT list or display any data from the "data" object.
                        - DO NOT repeat movie names, show timings, seat numbers, booking details,
                        booking IDs, payment IDs, etc.
                        - DO NOT include raw JSON or technical field names.
                        - DO NOT invent or assume missing information.
                        - Keep responses short, natural, and user-friendly.
                        - Maximum 1–2 sentences.
                        - Tell the user what happened and what they can do next.
                        - If the requested data is empty, clearly tell the user that nothing
                        matching their request was found.
                        - When data is unavailable, suggest a useful next action when appropriate.

                        ---

                        ### HOW TO HANDLE EMPTY DATA:

                        Treat the following as "no data found":
                        - null
                        - undefined
                        - empty arrays []
                        - empty objects {}
                        - missing expected results
                        - backend responses indicating no matching records

                        NEVER pretend that data exists when the backend returned no results.

                        ---

                        ### INTENT-BASED RESPONSE GUIDELINES:

                        1. search_all_movies:

                        If movies are available:
                        "Here are the movies currently playing."

                        If no movies are found:
                        "I couldn't find any movies matching your request. Try searching for
                        another movie or genre."

                        If the user asked for movies currently playing and none are available:
                        "There aren't any movies playing that match your request right now.
                        Try searching for another movie."

                        ---

                        2. movie_show_timetable:

                        If shows are available:
                        "Here are the available show timings."

                        If no shows are found:
                        "I couldn't find any shows for your selected movie. Try choosing another
                        movie."

                        If the user specifically requested a time/date and nothing is available:
                        "I couldn't find any shows matching that time. Try another time or date."

                        IMPORTANT:
                        Do not mention specific timings from the data.

                        ---

                        3. query_seats:

                        If seats/layout data is available:
                        "Here is the live seating layout. Pick any available seats to continue."

                        If no seats are available:
                        "Sorry, there are no available seats for this show. Try another show."

                        If seating information could not be retrieved:
                        "I couldn't load the seating layout right now. Please try again."

                        IMPORTANT:
                        Do not mention specific seat numbers.

                        ---

                        4. book_movie:

                        If booking is successfully created but payment is pending:
                        "Your booking has been created. Please complete the payment to confirm it."

                        If payment is successful:
                        "Your booking is confirmed. Enjoy your movie!"

                        If booking fails:
                        "I couldn't complete your booking. Please try again."

                        If required booking information is missing:
                        "I need a little more information to complete your booking."

                        If the selected seats are no longer available:
                        "Those seats are no longer available. Please choose different seats."

                        IMPORTANT:
                        Never expose booking IDs, payment IDs, transaction IDs, or raw backend
                        error messages.

                        ---

                        5. need_more_info:

                        Ask naturally for the missing information.

                        Missing movie:
                        "Which movie would you like to watch?"

                        Missing time:
                        "What time would you prefer?"

                        Missing number of seats:
                        "How many seats would you like to book?"

                        Missing show:
                        "Please select the show you'd like to book."

                        Missing seat selection:
                        "Please select the seats you'd like to book."

                        IMPORTANT:
                        Only ask for information that is actually missing.
                        Do not ask for information that is already available.

                        ---

                        6. unknown:

                        If the user query is unclear or cannot be understood:

                        "I'm not sure I understood that. You can ask me to find movies, check
                        showtimes, check seat availability, or book tickets."

                        If possible, use the user's query context to make the response more
                        relevant.

                        Do not give a long explanation.

                        ---

                        7. small_talk:

                        Respond naturally to casual or personal questions about the assistant.

                        Example:

                        User:
                        "Who are you?"

                        Response:
                        "I'm your movie booking assistant! I can help you find movies, check
                        showtimes, and book tickets."

                        Keep small-talk responses short and conversational.

                        If the user asks something unrelated to movie booking:
                        Respond politely and briefly redirect them toward movie-related help.

                        ---

                        8. get_booking:

                        If booking details are available:
                        "Here are your booking details. Enjoy your movie!"

                        If no booking is found:
                        "I couldn't find any bookings for you. Would you like to book a movie?"

                        If a specific booking was requested but does not exist:
                        "I couldn't find that booking. Please check the details and try again."

                        If booking information could not be retrieved:
                        "I couldn't retrieve your booking details right now. Please try again."

                        IMPORTANT:
                        Do not display booking IDs, payment IDs, seat numbers, movie names,
                        timings, or other booking data.

                        ---

                        ### GENERAL FAILURE CASES:

                        If the backend returns an error or the requested operation fails:

                        "Something went wrong while processing your request. Please try again."

                        If the error clearly indicates that the requested resource does not
                        exist:

                        "I couldn't find what you're looking for. Please try another option."

                        If the backend is temporarily unavailable:

                        "I'm having trouble accessing that right now. Please try again in a moment."

                        IMPORTANT:
                        Never expose:
                        - HTTP status codes
                        - stack traces
                        - database errors
                        - MongoDB errors
                        - API errors
                        - internal service names
                        - technical field names

                        ---

                        ### RESPONSE DECISION RULE:

                        Before generating the response:

                        1. Identify the intent.
                        2. Check whether the relevant data exists.
                        3. If relevant data exists, acknowledge the result and guide the user.
                        4. If relevant data is empty, clearly state that nothing was found.
                        5. If the operation failed, provide a short failure message.
                        6. If information is missing, ask only for the missing information.
                        7. Never invent information.
                        8. Never display backend data.

                        ---

                        ### EXAMPLES:

                        search_all_movies + movies found:
                        "Here are the movies currently playing."

                        search_all_movies + no movies:
                        "I couldn't find any movies matching your request. Try another search."

                        movie_show_timetable + shows found:
                        "Here are the available show timings."

                        movie_show_timetable + no shows:
                        "I couldn't find any shows for that movie. Try another date or movie."

                        query_seats + seats found:
                        "Here's the live seating layout. Pick your preferred available seats."

                        query_seats + no seats:
                        "Sorry, there are no available seats for this show. Try another show."

                        book_movie + payment pending:
                        "Your booking has been created. Please complete the payment to confirm it."

                        book_movie + payment successful:
                        "Your booking is confirmed. Enjoy your movie!"

                        book_movie + failure:
                        "I couldn't complete your booking. Please try again."

                        get_booking + booking found:
                        "Here are your booking details. Enjoy your movie!"

                        get_booking + no booking:
                        "I couldn't find any bookings for you. Would you like to book a movie?"

                        ---

                        ### OUTPUT FORMAT:

                        Return ONLY plain text.

                        No JSON.
                        No markdown.
                        No bullet points.
                        No technical information.
                        Maximum 1–2 sentences.
    """
                            ),
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
                            ),
                        },
                    ],
                    "temperature": 0.4,
                }
            ),
        )
        data = response.json()
        return (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "Sorry, I couldn't generate a response.")
        )
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
    def __init__(
        self,
        data=None,
        intent="",
        chat_response="Sorry there is something wrong, please try again!",
    ):
        self.api_data = data
        self.intent = intent
        self.chat_response = chat_response


async def process_query(
    query: str, user_token: str = None, userInput: dict = None, device_id: str = None
) -> ProcessQueryResponse:
    try:
        intent_json = call_llm(query)
        print(f"Raw LLM response: {intent_json}")

        # cleanup JSON
        if intent_json.startswith("```"):
            intent_json = (
                intent_json.strip("`")
                .replace("json\n", "")
                .replace("json", "", 1)
                .strip()
            )
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


def movie_to_text(movie):
    """
    Convert a movie document into natural-language text
    that can be embedded for semantic search.
    """

    title = movie.get("title", "")
    description = movie.get("description", "")

    genres = movie.get("genres", [])
    cast = movie.get("cast", [])

    release_date = movie.get("release_date")

    duration_ms = movie.get("duration", 0)
    duration_minutes = duration_ms // 60000

    genre_text = ", ".join(genres)
    cast_text = ", ".join(cast)

    release_text = ""

    if release_date:
        release_text = datetime.datetime.fromisoformat(
            release_date.replace("Z", "+00:00")
        ).strftime("%B %d, %Y")

    return (
        f"{title} is a {genre_text} movie "
        f"released on {release_text}. "
        f"It has a runtime of {duration_minutes} minutes. "
        f"{description} "
        f"The main cast includes {cast_text}."
    )


async def generate_embeddings():
    res = mov.search_movies(limitResults=False)

    total = len(res["data"]["movies"])

    print(f"Found {total} movies")

    processed = 0
    movies = res["data"]["movies"]
    for movie in movies:

        movie_id = movie["id"]
        title = movie.get("title", "Unknown")

        print(f"\nProcessing: {title}")

        text = movie_to_text(movie)

        print(f"Text: {text}")

        embedding = embedding_client.generate_embedding(text)

        print(f"Embedding dimensions: {len(embedding)}")

        knowledge_document = {
            "source": "movie",
            "source_id": movie_id,
            "content": text,
            "embedding": embedding,
            "metadata": {
                "title": title,
                "genres": movie.get("genres", []),
                "cast": movie.get("cast", []),
                "release_date": movie.get("release_date"),
                "duration": movie.get("duration"),
            },
        }

        # Prevent duplicate documents
        res = mov.create_or_update_knowledge_chunk(knowledge_document)
        processed += 1

        print(f"✓ Stored {processed}/{total}")
    return processed
