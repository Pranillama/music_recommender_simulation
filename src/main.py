"""
Command-line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

from src.recommender import load_songs, recommend_songs, DEFAULT_WEIGHTS


# ---------------------------------------------------------------------------
# User profiles — 3 core + 2 adversarial edge cases
# ---------------------------------------------------------------------------

PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.90,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.40,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.95,
        "likes_acoustic": False,
    },
    # --- Adversarial / edge-case profiles ---
    # Conflicting: high energy preference but sad mood — does the scorer handle tension?
    "Conflicting Vibe (Sad + High Energy)": {
        "genre": "blues",
        "mood": "sad",
        "energy": 0.90,
        "likes_acoustic": False,
    },
    # Niche: genre that appears only once in the catalog, very low energy, acoustic
    "Niche Acoustic Seeker": {
        "genre": "classical",
        "mood": "melancholic",
        "energy": 0.20,
        "likes_acoustic": True,
    },
}


def print_profile_results(name: str, user_prefs: dict, songs: list) -> None:
    """Print ranked recommendations for a single user profile."""
    recs = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 60)
    print(f"  Profile: {name}")
    print(f"  Prefs:   genre={user_prefs['genre']} | "
          f"mood={user_prefs['mood']} | "
          f"energy={user_prefs['energy']} | "
          f"likes_acoustic={user_prefs.get('likes_acoustic', False)}")
    print("=" * 60)

    for rank, (song, score, explanation) in enumerate(recs, start=1):
        print(f"\n  #{rank}  {song['title']} — {song['artist']}")
        print(f"       Genre: {song['genre']}  |  Mood: {song['mood']}"
              f"  |  Energy: {song['energy']:.2f}")
        print(f"       Score:  {score:.2f}")
        print(f"       Why:    {explanation}")


def run_experiment(songs: list) -> None:
    """Step 3 — compare original vs energy-boosted weights on the conflicting profile."""
    profile = PROFILES["Conflicting Vibe (Sad + High Energy)"]
    experimental_weights = {**DEFAULT_WEIGHTS, "genre": 1.0, "energy": 2.0}

    print("\n" + "*" * 60)
    print("  EXPERIMENT: halve genre weight, double energy weight")
    print("  Profile: Conflicting Vibe (Sad + High Energy)")
    print("*" * 60)

    print("\n  [Original weights]  genre=2.0 | mood=1.0 | energy x1.0")
    for rank, (song, score, _) in enumerate(
        recommend_songs(profile, songs, k=5, weights=DEFAULT_WEIGHTS), start=1
    ):
        print(f"  #{rank}  {song['title']} ({song['genre']}/{song['mood']}"
              f"  e={song['energy']:.2f})  score={score:.2f}")

    print("\n  [Experimental weights]  genre=1.0 | mood=1.0 | energy x2.0")
    for rank, (song, score, _) in enumerate(
        recommend_songs(profile, songs, k=5, weights=experimental_weights), start=1
    ):
        print(f"  #{rank}  {song['title']} ({song['genre']}/{song['mood']}"
              f"  e={song['energy']:.2f})  score={score:.2f}")

    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.")

    for name, prefs in PROFILES.items():
        print_profile_results(name, prefs, songs)

    run_experiment(songs)

    print("=" * 60)


if __name__ == "__main__":
    main()
