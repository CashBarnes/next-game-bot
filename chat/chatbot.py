from rapidfuzz import fuzz
from utils.filters import GENRE_KEYWORDS, PLATFORM_KEYWORDS
from utils.recommender import get_semantic_matches, games_df

# from utils.user_memory import memory

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
    global last_shown_titles, last_matches, pagination_index

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

    matches = get_semantic_matches(user_input, genre_filter, platform_filter, liked_titles, custom_df=filtered_df)
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
            f"\n*{match['title']}* — _{match['genre'].title()}_"
            f"\nReleased: {match['released']} | Metacritic: {match['metacritic']}"
            f"\nPlatforms: {match['platforms']}"
            f"\nTags: {', '.join(tag.strip().title() for tag in match['tags'].split(',') if tag.strip())}"
            f"\n{match['slug']}\n"
        )

    if memory and memory.get_likes():
        response += "\n\nYou liked: " + ", ".join(memory.get_likes())

    return response.strip()

