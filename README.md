# NextGameBot

NextGameBot is a lightweight local game recommendation chatbot that helps users discover new video games to play. It uses semantic matching powered by Sentence Transformers and a local CSV of games enriched with data from the RAWG API. The assistant takes into account the user's mood, preferred genres, platforms, and previous likes/dislikes to return relevant matches in natural language.

## Features

- Semantic search over local game data using `sentence-transformers`
- Memory of liked and disliked games
- Genre and platform keyword filtering
- Fallback to the RAWG API for additional results
- Interactive conversational interface
- Lightweight and local with no external model inference dependencies

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/NextGameBot.git
cd NextGameBot
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `config.py` File

You need a `config.py` file in the root directory with your RAWG API key:

```python
# config.py
RAWG_API_KEY = "your_rawg_api_key_here"
```

Sign up and get a free API key at https://rawg.io/apidocs

### 5. Run the App

To run the chatbot with the Streamlit interface:

```bash
streamlit run app.py
```

### 6. Test the CLI (Optional)

For terminal testing without the UI, you can run:

```bash
python main.py
```

## Deployment

To deploy this app to [Render](https://render.com/):

1. Create a new Web Service from your GitHub repo
2. Set the Start Command to:

```bash
streamlit run app.py
```

3. Add an environment variable in Render:

- `RAWG_API_KEY`: your API key

4. Make sure `requirements.txt` and `app.py` are in the root of the repo

## Data

- Game metadata is stored in `data/games.csv`
- Sentence embeddings are cached in `data/embeddings.pkl`
- User preferences (likes/dislikes) are stored in `data/user_memory.pkl`
