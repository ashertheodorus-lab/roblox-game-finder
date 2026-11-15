# Roblox Game Finder (Streamlit)

A small preference-based Roblox game recommender built using the uploaded `roblox_games.csv`.

## Project structure

```text
roblox_game_recommender/
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── roblox_games.csv
```

## Run it on your computer

1. Install Python.
2. Open a terminal in this project folder.
3. Install the libraries:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the website:

   ```bash
   streamlit run app.py
   ```

5. Streamlit will open the app in your browser. If it does not, open the local URL shown in the terminal (usually `http://localhost:8501`).

## Put it on GitHub

1. Create a new **public** GitHub repository, for example `roblox-game-finder`.
2. Upload `app.py`, `requirements.txt`, `README.md`, and the entire `data` folder.
3. Make sure the CSV is located at exactly `data/roblox_games.csv` (not beside `app.py`, and not inside another nested folder).

## Deploy it with Streamlit Community Cloud

1. Sign in to Streamlit Community Cloud using your GitHub account.
2. Choose **Create app**.
3. Select your repository and branch (`main`).
4. Set the main file path to `app.py`.
5. Deploy.

## Important note about the prediction method

The CSV has game names and popularity metrics (such as active players, visits, and rating), but it does not include genre labels or descriptions of gameplay. That means a supervised genre-prediction model cannot be trained directly from this CSV.

This project therefore uses:
- a short preference quiz (activity, social style, and pace);
- a transparent scoring system to choose a genre;
- a manually curated game-to-genre mapping for selected known titles;
- the CSV's popularity statistics to sort suggestions within the selected genre.

Unclassified games are intentionally not shown as genre recommendations rather than being assigned a made-up genre. The genre mapping can be expanded in `app.py` by editing `GAME_CATEGORIES`.
