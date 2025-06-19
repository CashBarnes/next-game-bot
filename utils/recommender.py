import os
import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
games_df = pd.read_csv("data/games.csv")

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Embedding cache file
EMBEDDINGS_FILE = "data/embeddings.pkl"

# Load or recompute embeddings based on dataset length
regenerate = True


# Globals
DATA_FILE = "data/games.csv"
games_df = pd.read_csv(DATA_FILE)

if os.path.exists(EMBEDDINGS_FILE):
    with open(EMBEDDINGS_FILE, "rb") as f:
        cached_embeddings = pickle.load(f)
    if len(cached_embeddings) == len(games_df):
        game_embeddings = cached_embeddings
        regenerate = False

if regenerate:
    print("Generating fresh game embeddings...")
    game_texts = (games_df["title"] + " " + games_df["tags"] + " " + games_df["description"]).fillna("").tolist()
    game_embeddings = model.encode(game_texts, convert_to_tensor=True).cpu()
    with open(EMBEDDINGS_FILE, "wb") as f:
        pickle.dump(game_embeddings, f)
    print(f"Saved embeddings to {EMBEDDINGS_FILE}")



# Match user input to games
def get_semantic_matches(user_input, genre_filter=None, platform_filter=None, liked_titles=None, custom_df=None):
    df = custom_df.copy() if custom_df is not None else games_df.copy()
    user_embedding = model.encode([user_input], convert_to_tensor=True).cpu()
    scores = cosine_similarity(user_embedding, game_embeddings.cpu())[0]

    # Ensure score and df length match
    if len(df) != len(scores):
        raise ValueError(f"Mismatch between DataFrame rows ({len(df)}) and embedding scores ({len(scores)}).")

    df["score"] = scores

    # Boost genre
    if genre_filter:
        df.loc[df["genre"].str.contains(genre_filter, case=False, na=False), "score"] += 0.1

    # Boost platform
    if platform_filter:
        df.loc[df["platforms"].str.contains(platform_filter, case=False, na=False), "score"] += 0.1

    # Boost based on liked games
    if liked_titles:
        liked_df = df[df["title"].isin(liked_titles)]
        if not liked_df.empty:
            liked_texts = (liked_df['title'] + " " + liked_df['tags'] + " " + liked_df['description']).fillna("").tolist()
            liked_embeddings = model.encode(liked_texts, convert_to_tensor=True).cpu()
            sim_boosts = cosine_similarity(liked_embeddings, game_embeddings.cpu())
            similarity_scores = sim_boosts.mean(axis=0)

            if len(similarity_scores) != len(df):
                similarity_scores = similarity_scores[:len(df)]
            df["score"] += similarity_scores * 0.2

    top_matches = df.sort_values(by="score", ascending=False).drop_duplicates(subset="title").head(10)

    results = []
    for _, match in top_matches.iterrows():
        title = match["title"]
        platforms = match["platforms"]
        genre = match["genre"]
        description = match["description"]
        released = match["released"] or "Unknown"
        if isinstance(released, str) and released.strip():
            release_year = released.split("-")[0]
        else:
            release_year = "Unknown"
        metacritic = match["metacritic"] if pd.notna(match["metacritic"]) else "N/A"

        tags_raw = match["tags"] if isinstance(match["tags"], str) else ""
        tag_list = [t.strip() for t in tags_raw.split(",") if len(t.strip()) < 25 and " " in t]
        tags_preview = ", ".join(tag_list[:3])

        short_desc = description[:240].strip().replace('\n', ' ') + "..."

        results.append({
            "title": title,
            "platforms": platforms,
            "genre": genre,
            "released": release_year,
            "metacritic": metacritic,
            "tags": tags_preview,
            "slug": short_desc
        })

    return results


def refresh_embeddings():
    global games_df, game_embeddings
    games_df = pd.read_csv(DATA_FILE)
    texts = (games_df["title"] + " " + games_df["tags"] + " " + games_df["description"]).fillna("").tolist()
    game_embeddings = model.encode(texts, convert_to_tensor=True).cpu()
    with open(EMBEDDINGS_FILE, "wb") as f:
        pickle.dump(game_embeddings, f)
    print(f"[DEBUG] Recomputed embeddings for {len(games_df)} games.")


