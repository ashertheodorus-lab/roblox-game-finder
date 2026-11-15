import re
from html import escape
from urllib.parse import quote
from pathlib import Path

import pandas as pd
import streamlit as st

# ------------------------------------------------------------
# Page setup
# ------------------------------------------------------------
st.set_page_config(
    page_title="Roblox Game Finder",
    page_icon="🎮",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
#MainMenu, footer {visibility: hidden;}
.block-container {max-width: 1100px; padding-top: 1.5rem; padding-bottom: 3rem;}
.hero {
    background: linear-gradient(125deg, #312e81 0%, #6d28d9 55%, #db2777 100%);
    border-radius: 22px; padding: 2.6rem 2rem; color: white;
    text-align: center; margin-bottom: 1.6rem;
}
.hero-kicker {font-size: .78rem; letter-spacing: .16em; text-transform: uppercase; opacity: .82;}
.hero h1 {font-size: 2.45rem; line-height: 1.15; margin: .6rem 0;}
.hero p {font-size: 1.05rem; opacity: .9; margin: 0;}
.question {
    border: 1px solid #ddd6fe; background: #f5f3ff; border-radius: 15px;
    padding: 1rem 1.2rem; margin: 1.2rem 0 .6rem;
}
.question strong {color: #4c1d95; font-size: 1.05rem;}
.game-card {
    border: 1px solid #e5e7eb; border-radius: 15px; padding: 1rem 1.1rem;
    background: white; margin: .55rem 0;
}
.game-title {font-size: 1.08rem; font-weight: 700; color: #111827;}
.muted {color: #6b7280; font-size: .88rem;}
.pill {
    display: inline-block; padding: .22rem .6rem; margin: .35rem .25rem 0 0;
    background: #ede9fe; color: #5b21b6; border-radius: 999px;
    font-size: .78rem; font-weight: 600;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(110deg, #6d28d9, #9333ea);
    border: 0; border-radius: 12px; min-height: 3rem; font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

DATA_PATH = Path(__file__).parent / "data" / "roblox_games.csv"

# The CSV has game titles and popularity statistics, but no genre labels.
# These hand-reviewed keyword groups provide the missing category layer.
GAME_CATEGORIES = {
    "Roleplay & Social": [
        "Brookhaven", "Adopt Me!", "Berry Avenue", "LifeTogether", "Welcome to Bloxburg",
        "Metro Life", "Gacha Online", "Royale High", "Livetopia", "Greenville",
        "Bayside High School", "Emergency Hamburg", "Emergency Response: Liberty County",
        "Work at a Pizza Place", "PLS DONATE", "Catalog Avatar Creator",
    ],
    "Creative & Dress-Up": [
        "Dress To Impress", "Catalog Avatar Creator", "Royale High", "Speed Draw!",
        "Gacha Online", "Berry Avenue",
    ],
    "Pets & Collecting": [
        "PETS GO!", "Pet Simulator 99", "Adopt Me!", "Bee Swarm Simulator",
        "Dragon Adventures", "Horse Life", "Creatures of Sonaria", "Fisch",
        "Sol's RNG",
    ],
    "Tycoon & Simulator": [
        "Car Dealership Tycoon", "Gym League", "Arm Wrestle Simulator",
        "Sonic Speed Simulator", "Work at a Pizza Place", "Build A Boat For Treasure",
        "Bee Swarm Simulator", "Pet Simulator 99", "PETS GO!",
    ],
    "Obby & Platformer": [
        "Tower of Hell", "Barry's Prison Run", "Obby but you're a Spider",
        "Sonic Speed Simulator", "Escape Running Head", "Color or Die",
    ],
    "Adventure & Exploration": [
        "Fisch", "Build A Boat For Treasure", "a dusty trip", "Block Tales",
        "Dragon Adventures", "3008",
    ],
    "Puzzle & Mystery": [
        "DOORS", "Piggy", "Flee the Facility", "Banana Eats", "The Mimic",
        "Rainbow Friends", "Natural Disaster Survival", "Hide or Die!",
    ],
    "Sports & Racing": [
        "NFL Universe Football", "Driving Empire", "Football Fusion 2",
        "Super League Soccer", "Swim League", "Realistic Street Soccer",
    ],
}

CATEGORY_INFO = {
    "Roleplay & Social": {
        "emoji": "🏡",
        "description": "You may enjoy social worlds, roleplaying, customizing a character, and making your own stories.",
        "activities": {"Hang out and pretend": 3, "Build and grow": 1},
        "social": {"Just chatting": 3, "With a team": 1, "Mostly solo": 1},
        "pace": {"Chill and relaxing": 3, "Brainy and tricky": 1},
    },
    "Creative & Dress-Up": {
        "emoji": "🎨",
        "description": "You may enjoy styling avatars, creating looks, drawing, and expressing your creativity.",
        "activities": {"Hang out and pretend": 2, "Build and grow": 2},
        "social": {"Mostly solo": 2, "Just chatting": 2},
        "pace": {"Chill and relaxing": 3, "Brainy and tricky": 1},
    },
    "Pets & Collecting": {
        "emoji": "🐾",
        "description": "You may enjoy collecting pets or items, discovering new things, and gradually growing a collection.",
        "activities": {"Build and grow": 3, "Explore and solve": 1},
        "social": {"Mostly solo": 2, "With a team": 1, "Just chatting": 1},
        "pace": {"Chill and relaxing": 3, "Brainy and tricky": 1},
    },
    "Tycoon & Simulator": {
        "emoji": "🏗️",
        "description": "You may enjoy upgrading, managing resources, building progress, and working toward long-term goals.",
        "activities": {"Build and grow": 3},
        "social": {"Mostly solo": 2, "With a team": 1},
        "pace": {"Chill and relaxing": 2, "Brainy and tricky": 2},
    },
    "Obby & Platformer": {
        "emoji": "🧗",
        "description": "You may enjoy obstacle courses, movement challenges, timing, and improving through practice.",
        "activities": {"Run and jump": 3},
        "social": {"Mostly solo": 2, "Against other players": 1, "With a team": 1},
        "pace": {"Fast and intense": 3, "Brainy and tricky": 1},
    },
    "Adventure & Exploration": {
        "emoji": "🧭",
        "description": "You may enjoy exploring unfamiliar places, discovering secrets, and progressing through an adventure.",
        "activities": {"Explore and solve": 3, "Run and jump": 1},
        "social": {"Mostly solo": 2, "With a team": 2},
        "pace": {"Brainy and tricky": 2, "Fast and intense": 1},
    },
    "Puzzle & Mystery": {
        "emoji": "🧩",
        "description": "You may enjoy searching for clues, noticing patterns, and figuring out what is happening.",
        "activities": {"Explore and solve": 3},
        "social": {"Mostly solo": 2, "With a team": 1},
        "pace": {"Brainy and tricky": 3},
    },
    "Sports & Racing": {
        "emoji": "🏁",
        "description": "You may enjoy races, sports challenges, improving your performance, and friendly competition.",
        "activities": {"Compete and win": 2, "Run and jump": 1},
        "social": {"Against other players": 3, "With a team": 2},
        "pace": {"Fast and intense": 3},
    },
}

ACTIVITY_OPTIONS = [
    "Compete and win",
    "Run and jump",
    "Build and grow",
    "Explore and solve",
    "Hang out and pretend",
]
SOCIAL_OPTIONS = ["Against other players", "With a team", "Mostly solo", "Just chatting"]
PACE_OPTIONS = ["Fast and intense", "Chill and relaxing", "Brainy and tricky"]


def clean_number(value):
    """Convert CSV values such as '483,372' into numbers."""
    if pd.isna(value):
        return 0
    cleaned = re.sub(r"[^0-9.]", "", str(value))
    try:
        return float(cleaned) if cleaned else 0
    except ValueError:
        return 0


@st.cache_data
def load_games():
    if not DATA_PATH.exists():
        st.error("I couldn't find data/roblox_games.csv. Make sure the CSV is inside the data folder.")
        st.stop()

    games = pd.read_csv(DATA_PATH)
    for col in ["Active", "Visits", "Favourites", "Likes", "Dislikes"]:
        if col in games.columns:
            games[col] = games[col].apply(clean_number)
    if "Rating" not in games.columns:
        games["Rating"] = 0
    games["Name"] = games["Name"].fillna("").astype(str)
    games["Category"] = games["Name"].apply(assign_category)
    return games


def assign_category(name):
    # First matching category wins; category lists are intentionally curated.
    for category, titles in GAME_CATEGORIES.items():
        for title in titles:
            if title.casefold() in name.casefold():
                return category
    return None


def recommend_category(activity, social, pace):
    scores = {category: 0 for category in CATEGORY_INFO}
    for category, info in CATEGORY_INFO.items():
        scores[category] += info["activities"].get(activity, 0) * 2
        scores[category] += info["social"].get(social, 0) * 1.5
        scores[category] += info["pace"].get(pace, 0) * 1.5
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def format_count(value):
    value = int(value)
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


games = load_games()

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------
st.markdown("""
<div class="hero">
  <div class="hero-kicker">🎮 Roblox discovery · preference-based recommender</div>
  <h1>Find Your Next Roblox Game</h1>
  <p>Tell us what kind of experience you feel like playing. We'll suggest a genre and games from the dataset.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### Your game preferences")
st.write("Choose the option that sounds most like what you want to play right now.")

with st.form("preference_form"):
    st.markdown('<div class="question"><strong>1 · What do you like to do?</strong><br><span class="muted">Pick the main activity you find most fun.</span></div>', unsafe_allow_html=True)
    activity = st.radio(
        "Main activity",
        ACTIVITY_OPTIONS,
        format_func=lambda x: {
            "Compete and win": "🏆 Compete and win — sports, races, and friendly challenges",
            "Run and jump": "🧗 Run and jump — obstacle courses and movement challenges",
            "Build and grow": "🏗️ Build and grow — upgrades, collecting, and creating progress",
            "Explore and solve": "🧭 Explore and solve — discover places, clues, and secrets",
            "Hang out and pretend": "🏡 Hang out and pretend — roleplay, style, and social worlds",
        }[x],
        label_visibility="collapsed",
    )

    st.markdown('<div class="question"><strong>2 · How do you want to play with others?</strong><br><span class="muted">Choose the social style you prefer.</span></div>', unsafe_allow_html=True)
    social = st.radio(
        "Social style",
        SOCIAL_OPTIONS,
        format_func=lambda x: {
            "Against other players": "🥇 Against other players — friendly competition",
            "With a team": "🤝 With a team — cooperate and reach a shared goal",
            "Mostly solo": "🧍 Mostly solo — play at your own pace",
            "Just chatting": "💬 Just chatting — meet people and hang out",
        }[x],
        label_visibility="collapsed",
    )

    st.markdown('<div class="question"><strong>3 · What mood and pace do you want?</strong><br><span class="muted">How much energy or concentration do you feel like using?</span></div>', unsafe_allow_html=True)
    pace = st.radio(
        "Pace",
        PACE_OPTIONS,
        format_func=lambda x: {
            "Fast and intense": "⚡ Fast and intense — quick reactions and lots happening",
            "Chill and relaxing": "🌿 Chill and relaxing — low pressure and steady progress",
            "Brainy and tricky": "🧠 Brainy and tricky — puzzles, planning, and problem-solving",
        }[x],
        label_visibility="collapsed",
    )

    submitted = st.form_submit_button("✨ Find my Roblox games", type="primary", use_container_width=True)

if submitted:
    ranked_categories = recommend_category(activity, social, pace)
    best_category, best_score = ranked_categories[0]
    second_category, second_score = ranked_categories[1]

    st.markdown("---")
    st.markdown("## Your recommendation")
    info = CATEGORY_INFO[best_category]
    st.markdown(
        f"<div class='question'><div style='font-size:1.8rem'>{info['emoji']} <strong>{best_category}</strong></div>"
        f"<p>{info['description']}</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown(f"**Why this genre?** Your choices — *{activity.lower()}*, *{social.lower()}*, and *{pace.lower()}* — give this category the strongest preference match.")
    st.caption(f"Second closest genre: {second_category}")

    matches = games[games["Category"] == best_category].copy()
    if not matches.empty:
        # Popularity is used only to order games within the recommended category.
        sort_cols = [c for c in ["Active", "Rating", "Visits"] if c in matches.columns]
        matches = matches.sort_values(sort_cols, ascending=[False] * len(sort_cols)).head(6)

        st.markdown("### Games from your dataset")
        st.caption("These titles are taken from your CSV. Popularity statistics help order the suggestions; they do not determine the genre.")
        for _, game in matches.iterrows():
            active = format_count(game.get("Active", 0))
            visits = format_count(game.get("Visits", 0))
            rating = game.get("Rating", 0)
            safe_name = escape(str(game["Name"]))
            st.markdown(
                f"""<div class="game-card">
                    <div class="game-title">{safe_name}</div>
                    <span class="pill">{best_category}</span>
                    <div class="muted" style="margin-top:.55rem">
                        Active players: {active} &nbsp;·&nbsp; Visits: {visits} &nbsp;·&nbsp; Rating: {rating:.1f}/100
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
            # A search link lets the player find the exact title on Roblox.
            search_url = "https://www.roblox.com/discover/?Keyword=" + quote(str(game["Name"]))
            st.markdown(f"[Search this game on Roblox]({search_url})")

    else:
        st.info("There are no games currently tagged in this category in the curated list. Try another set of preferences.")

    with st.expander("How does this recommendation work?"):
        st.write(
            "This version uses a transparent preference-scoring system, not a trained machine-learning model. "
            "Your three answers are compared with the preference profile for each genre. The highest-scoring "
            "genre is selected. Game titles are assigned to genres through a small manually curated mapping, "
            "because the CSV does not contain genre or gameplay-description columns. Within that genre, games "
            "are ordered using the CSV's Active, Rating, and Visits columns."
        )
        st.write("This is a recommendation, not a guarantee that you will like a particular game.")

st.markdown("---")
st.caption(f"Dataset loaded: {len(games):,} Roblox games · Unclassified titles are left out of recommendations.")
