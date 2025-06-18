import requests
import csv
from config import RAWG_API_KEY as API_KEY

GENRES = ["rpg", "adventure", "indie"]
PAGE_SIZE = 40  # max allowed by API
MAX_PAGES = 5   # adjust to get more data

def fetch_games():
    games = []
    for genre in GENRES:
        for page in range(1, MAX_PAGES + 1):
            url = f"https://api.rawg.io/api/games"
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
                description = game.get("description_raw") or game.get("slug") or ""
                platforms = ", ".join([p["platform"]["name"] for p in game.get("platforms", [])])
                tags = ", ".join([t["name"] for t in game.get("tags", [])])
                games.append([title, genre, tags, platforms, description])
    return games

def save_to_csv(games, filename="data/games.csv"):
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "genre", "tags", "platforms", "description"])
        writer.writerows(games)
    print(f"Saved {len(games)} games to {filename}")

if __name__ == "__main__":
    game_data = fetch_games()
    save_to_csv(game_data)
