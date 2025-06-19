from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from utils.filters import GENRE_KEYWORDS, PLATFORM_KEYWORDS
from utils.recommender import get_semantic_matches, game_embeddings, games_df

model = SentenceTransformer("all-MiniLM-L6-v2")

last_shown_titles = []
seen_titles = set()
last_matches = []
pagination_index = 0
PAGE_SIZE = 5


def fuzzy_match_title(user_input, titles, threshold=85):
    best_match = None
    best_score = 0
    for title in titles:
        score = fuzz.partial_ratio(user_input.lower(), title.lower())
        if score > best_score and score >= threshold:
            best_match = title
            best_score = score
    return best_match


def best_match_from_last_shown(user_input, last_titles, threshold=70):
    best_score = 0
    best_title = None
    for title in last_titles:
        score = fuzz.partial_ratio(user_input.lower(), title.lower())
        if score > best_score and score >= threshold:
            best_score = score
            best_title = title
    return best_title


def parse_feedback(user_input, memory):
    lowered = user_input.lower()

    positive_verbs = ["like", "liked", "love", "loved"]
    negative_verbs = ["hate", "hated", "dislike", "disliked", "don't like", "do not like"]

    # Check negatives first to avoid "like" being found in "disliked"
    if any(v in lowered for v in negative_verbs):
        best_title = best_match_from_last_shown(lowered, last_shown_titles)
        if best_title:
            memory.dislike(best_title)
            return f"Okay, I’ll avoid similar games to **{best_title}**."

    elif any(v in lowered for v in positive_verbs):
        best_title = best_match_from_last_shown(lowered, last_shown_titles)
        if best_title:
            memory.like(best_title)
            return f"Got it — I’ll remember you liked **{best_title}**."

    return None


def get_response(user_input, memory):
    global last_shown_titles, last_matches, pagination_index, games_df, game_embeddings, model

    feedback = parse_feedback(user_input, memory)
    if feedback:
        return feedback

    # Show more results
    if user_input.strip().lower() in ["more", "show more", "next", "next page"]:
        if not last_matches:
            return "There’s nothing more to show yet — ask for a genre or style!"

        slice = last_matches[pagination_index:pagination_index + PAGE_SIZE]
        pagination_index += PAGE_SIZE

        if not slice:
            return "You’ve reached the end of the list."

        last_shown_titles = [match["title"] for match in slice]
        return format_results(slice, memory)

    # New search
    pagination_index = PAGE_SIZE
    genre_filter, platform_filter = extract_filters(user_input)
    liked_titles = memory.get_likes() if memory else []

    filtered_df = games_df.copy()

    if "not violent" in user_input.lower():
        filtered_df = filtered_df[~filtered_df["tags"].str.contains("violent", case=False, na=False)]

    print(f"[DEBUG] DataFrame: {len(filtered_df)} rows | Embeddings: {len(game_embeddings)}")

    matches = get_semantic_matches(user_input, genre_filter, platform_filter, liked_titles, custom_df=filtered_df)
    MIN_RESULTS_THRESHOLD = 500

    # Fallback if no matches found locally
    if len(matches) < MIN_RESULTS_THRESHOLD:
        print("[DEBUG] Low match count — fetching from RAWG...")
        from utils.fetch_games import fetch_games_from_rawg, append_new_games_to_csv

        new_games = fetch_games_from_rawg(user_input)
        new_data_added = append_new_games_to_csv(new_games)

        if new_data_added:
            from utils.recommender import refresh_embeddings
            refresh_embeddings()

            # Sync updated globals from recommender.py
            from utils.recommender import games_df as updated_df, game_embeddings as updated_embeddings
            games_df = updated_df
            game_embeddings = updated_embeddings
            filtered_df = games_df.copy()

        else:
            print("[DEBUG] No new games added — skipping embedding refresh.")

        print(f"[DEBUG] DataFrame: {len(filtered_df)} rows | Embeddings: {len(game_embeddings)}")

        matches = get_semantic_matches(user_input, genre_filter, platform_filter, liked_titles, custom_df=filtered_df)

        if not matches:
            return "I couldn’t find anything even after searching online — maybe try rephrasing?"

    # Proceed with matched results
    last_matches = matches
    last_shown_titles = [match["title"] for match in matches[:PAGE_SIZE]]
    return format_results(matches[:PAGE_SIZE], memory)



def extract_filters(user_input):
    lowered = user_input.lower()
    genre_filter = None
    platform_filter = None

    for genre in GENRE_KEYWORDS:
        if genre in lowered:
            genre_filter = genre
            break

    for platform in PLATFORM_KEYWORDS:
        if f"for {platform}" in lowered or f"on {platform}" in lowered or platform in lowered:
            platform_filter = platform
            break

    return genre_filter, platform_filter


def format_results(matches, memory=None):
    if not matches:
        return "I couldn't find any good matches."

    response = ""
    for match in matches:
        response += (
            f"\n*{match['title']}* — _{str(match['genre']).title()}_"
            f"\nReleased: {match['released']} | Metacritic: {match['metacritic']}"
            f"\nPlatforms: {match['platforms']}"
            f"\nTags: {', '.join(tag.strip().title() for tag in match['tags'].split(',') if tag.strip())}"
            f"\n{match['slug']}\n"
        )

    if memory and memory.get_likes():
        response += "\n\nYou liked: " + ", ".join(memory.get_likes())

    return response.strip()


