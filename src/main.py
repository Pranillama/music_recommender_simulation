"""
Command-line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.\n")

    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
    }

    print("User profile:")
    for k, v in user_prefs.items():
        print(f"  {k}: {v}")
    print()

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("=" * 55)
    print(f"  Top {len(recommendations)} Recommendations")
    print("=" * 55)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']} — {song['artist']}")
        print(f"    Genre: {song['genre']}  |  Mood: {song['mood']}"
              f"  |  Energy: {song['energy']:.2f}")
        print(f"    Score:  {score:.2f}")
        print(f"    Why:    {explanation}")
    print()


if __name__ == "__main__":
    main()
