import os
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
import csv
from config import RAWG_API_KEY as API_KEY

GENRES = [
    "action", "adventure", "indie", "rpg", "strategy", "shooter",
    "puzzle", "platformer", "racing", "sports", "simulation",
    "fighting", "family", "arcade", "educational", "casual",
    "massively-multiplayer", "board-games", "card"
]

PAGE_SIZE = 40  # max allowed by API
MAX_PAGES = 5   # adjust to get more data

GENRES = ["rpg", "adventure", "indie"]
PAGE_SIZE = 40  # max allowed
MAX_PAGES = 5   # adjust as needed


def is_english(text):
    return all(ord(c) < 128 for c in text)


def fetch_games():
    games = []
    for genre in GENRES:
        for page in range(1, MAX_PAGES + 1):
            url = "https://api.rawg.io/api/games"
            params = {
                "key": API_KEY,
                "genres": genre,
                "page": page,
                "page_size": PAGE_SIZE
            }
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Failed on page {page}, genre {genre}")
                continue

            data = response.json()
            for game in data["results"]:
                title = game["name"]

                # Clean description
                raw_description = game.get("description_raw") or game.get("slug") or ""
                description = ''.join([c for c in raw_description if ord(c) < 128])

                # Clean tags
                raw_tags = game.get("tags", [])
                tags = ", ".join([
                    t["name"].strip() for t in raw_tags
                    if is_english(t["name"])
                ])

                platforms = ", ".join([p["platform"]["name"] for p in game.get("platforms", [])])
                metacritic = game.get("metacritic", "N/A")
                released = game.get("released", "Unknown")

                games.append([
                    title,
                    genre,
                    tags,
                    platforms,
                    description,
                    metacritic,
                    released
                ])
    return games


def fetch_games_from_rawg(query, page_size=10):
    print(f"[DEBUG] Searching RAWG for: {query}")
    url = "https://api.rawg.io/api/games"
    params = {
        "key": API_KEY,
        "search": query,
        "page_size": page_size
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"RAWG request failed: {response.status_code}")
        return []

    raw_results = response.json().get("results", [])
    print(f"[DEBUG] RAWG returned {len(raw_results)} result(s)")

    results = []
    for game in raw_results:
        title = game["name"]
        if not is_english(title):
            continue

        raw_tags = game.get("tags", [])
        tags = ", ".join([
            t["name"].strip() for t in raw_tags
            if is_english(t["name"])
        ])

        platforms = ", ".join([
            p["platform"]["name"] for p in game.get("platforms", [])
        ])

        raw_description = game.get("description_raw") or game.get("slug") or ""
        description = ''.join([c for c in raw_description if ord(c) < 128])

        results.append({
            "title": title,
            "genre": ", ".join([g["name"] for g in game.get("genres", [])]),
            "tags": tags,
            "platforms": platforms,
            "description": description,
            "metacritic": game.get("metacritic", "N/A"),
            "released": game.get("released", "Unknown"),
            "slug": game.get("slug", "")
        })

    return results



def save_to_csv(games, filename="data/games.csv"):
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "genre", "tags", "platforms", "description", "metacritic", "released"])
        writer.writerows(games)
    print(f"Saved {len(games)} games to {filename}")


def append_new_games_to_csv(fetched_games, csv_path="data/games.csv"):
    # Load existing games.csv
    if os.path.exists(csv_path):
        existing_df = pd.read_csv(csv_path)
    else:
        existing_df = pd.DataFrame(columns=[
            "title", "genre", "tags", "platforms", "description", "metacritic", "released"
        ])

    existing_titles = set(existing_df["title"].str.lower())
    new_rows = []

    for game in fetched_games:
        if game["title"].lower() not in existing_titles:
            new_rows.append([
                game["title"],
                game["genre"],
                game["tags"],
                game["platforms"],
                game["description"],
                game["metacritic"],
                game["released"]
            ])

    if new_rows:
        new_df = pd.DataFrame(new_rows, columns=existing_df.columns)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"Added {len(new_rows)} new game(s) to {csv_path}")
        return True  # New data added

    return False  # No new data added



if __name__ == "__main__":
    game_data = fetch_games()
    save_to_csv(game_data)
