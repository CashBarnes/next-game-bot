import os
import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load data
games_df = pd.read_csv("data/games.csv")

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Prepare game embeddings (once)
game_texts = (games_df['title'] + " " + games_df['tags'] + " " + games_df['description']).fillna("").tolist()
game_embeddings = model.encode(game_texts, convert_to_tensor=True).cpu()


def get_semantic_matches(user_input):
    user_embedding = model.encode([user_input], convert_to_tensor=True).cpu()
    scores = cosine_similarity(user_embedding, game_embeddings.cpu())[0]

    games_df["score"] = scores
    top_matches = games_df.sort_values(by="score", ascending=False).head(10)
    top_matches = top_matches.drop_duplicates(subset="title")

    results = []
    for _, match in top_matches.iterrows():
        title = match["title"]
        platforms = match["platforms"]
        genre = match["genre"]
        description = match["description"]
        short_desc = description[:240].strip().replace('\n', ' ') + "..."

        results.append(
            f"\n *{title}* [{platforms}]\n"
            f"Genre: {genre}\n"
            f"{short_desc}\n"
        )

    return results

