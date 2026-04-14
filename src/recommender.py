import csv
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a song and its audio/metadata attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's taste preferences used for scoring."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# Internal scoring helper
# ---------------------------------------------------------------------------

# Default scoring weights — change these to run experiments (see Step 3 in Phase 4)
DEFAULT_WEIGHTS: Dict[str, float] = {
    "genre":    2.0,   # points for an exact genre match
    "mood":     1.0,   # points for an exact mood match
    "energy":   1.0,   # multiplier on the 0–1 energy-similarity term
    "acoustic": 0.5,   # bonus when user likes_acoustic and song acousticness >= 0.6
}


def _score(
    genre: str,
    mood: str,
    energy: float,
    acousticness: float,
    target_genre: str,
    target_mood: str,
    target_energy: float,
    likes_acoustic: bool,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[str]]:
    """Compute a weighted score and reasons list from raw song and profile fields."""
    w = weights if weights is not None else DEFAULT_WEIGHTS
    score = 0.0
    reasons = []

    if genre == target_genre:
        pts = w["genre"]
        score += pts
        reasons.append(f"genre match: {genre} (+{pts:.1f})")

    if mood == target_mood:
        pts = w["mood"]
        score += pts
        reasons.append(f"mood match: {mood} (+{pts:.1f})")

    energy_sim = round((1.0 - abs(energy - target_energy)) * w["energy"], 2)
    score += energy_sim
    reasons.append(f"energy similarity: {energy:.2f} vs {target_energy:.2f} (+{energy_sim:.2f})")

    if likes_acoustic and acousticness >= 0.6:
        pts = w["acoustic"]
        score += pts
        reasons.append(f"acoustic bonus: acousticness={acousticness:.2f} (+{pts:.1f})")

    return round(score, 4), reasons


# ---------------------------------------------------------------------------
# Functional API  (used by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file, casting numeric fields to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            for field in ("energy", "valence", "danceability", "acousticness"):
                row[field] = float(row[field])
            songs.append(row)
    return songs


def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[str]]:
    """Score a single song dict against a user-preference dict."""
    target_genre = user_prefs.get("genre", "")
    target_mood = user_prefs.get("mood", "")
    target_energy = float(user_prefs.get("energy", user_prefs.get("target_energy", 0.5)))
    likes_acoustic = bool(user_prefs.get("likes_acoustic", False))

    return _score(
        song["genre"],
        song["mood"],
        float(song["energy"]),
        float(song["acousticness"]),
        target_genre,
        target_mood,
        target_energy,
        likes_acoustic,
        weights,
    )


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Optional[Dict[str, float]] = None,
) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort descending, and return the top-k as (song, score, explanation) tuples."""
    scored = []
    for song in songs:
        s, reasons = score_song(user_prefs, song, weights)
        explanation = " | ".join(reasons)
        scored.append((song, s, explanation))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]


# ---------------------------------------------------------------------------
# OOP API  (used by tests/test_recommender.py)
# ---------------------------------------------------------------------------

class Recommender:
    """Content-based music recommender that scores and ranks Song objects."""

    def __init__(self, songs: List[Song]):
        """Initialise with a catalog of Song dataclass instances."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs sorted from highest to lowest score."""
        def _song_score(song: Song) -> float:
            s, _ = _score(
                song.genre, song.mood, song.energy, song.acousticness,
                user.favorite_genre, user.favorite_mood,
                user.target_energy, user.likes_acoustic,
            )
            return s

        return sorted(self.songs, key=_song_score, reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a song was recommended."""
        _, reasons = _score(
            song.genre, song.mood, song.energy, song.acousticness,
            user.favorite_genre, user.favorite_mood,
            user.target_energy, user.likes_acoustic,
        )
        return " | ".join(reasons) if reasons else "No strong match found."
