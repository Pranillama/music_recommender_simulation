# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Large-scale services (e.g. Spotify, YouTube) usually **generate many candidate** songs or videos, **score or rank** them with models trained on billions of implicit events (plays, skips, dwell time), and often **re-rank** lists for diversity, novelty, and business rules. This project does **not** mimic that pipeline: it is a **small, content-based** simulation. The focus is **interpretability**—every recommendation can be explained from a handful of song attributes and a short, explicit user profile. This version will prioritize **vibe alignment** (mood and genre matches from the profile), **numeric closeness** on energy (and room to extend to valence, danceability, tempo, acousticness when scoring), and **clear explanations** tied to those same fields.

**`Song` object — fields used in the simulation**

- **`id`** — unique catalog id  
- **`title`, `artist`** — labels for display and explanations  
- **`genre`, `mood`** — categorical tags matched to the user profile  
- **`energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`** — numeric features for distance / similarity in the scorer  

**`UserProfile` object — fields used in the simulation**

- **`favorite_genre`** — compared to each song’s `genre`  
- **`favorite_mood`** — compared to each song’s `mood` (at least as important as genre for separating vibe within the same genre)  
- **`target_energy`** — preferred level; closer `energy` on the song scores better  
- **`likes_acoustic`** — whether to favor higher `acousticness` on tracks  

The `Recommender` scores each `Song` against a `UserProfile`, applies a **ranking rule** (sort by score, take top `k`), and `explain_recommendation` summarizes *why* a song ranked well using these features.

---

### User Taste Profile (Phase 2 Design)

The simulation uses a concrete example profile to test the scoring logic:

```python
user_prefs = {
    "genre":        "lofi",       # favorite genre tag
    "mood":         "chill",      # favorite mood tag
    "target_energy": 0.40,        # preferred energy level (0.0–1.0)
    "likes_acoustic": True,       # bonus for high acousticness
}
```

**Profile critique:** This profile clearly separates *chill lofi* (Library Rain, Focus Flow — low energy, high acousticness) from *intense rock* (Storm Runner — high energy, low acousticness). Because `genre` and `mood` are both explicit, the scorer can distinguish a "chill jazz" track from a "chill lofi" track, giving the genre match extra weight to break ties.

---

### Algorithm Recipe (Phase 2 Design)

Each song receives a score built from four weighted components:

| Component | Points | Logic |
|---|---|---|
| Genre match | **+2.0** | `song.genre == user.genre` |
| Mood match | **+1.0** | `song.mood == user.mood` |
| Energy similarity | **+0.0 – +1.0** | `1.0 - abs(song.energy - user.target_energy)` |
| Acoustic bonus | **+0.5** | if `user.likes_acoustic` and `song.acousticness >= 0.6` |

**Maximum possible score: 4.5**

Songs are then sorted descending by score, and the top `k` are returned.

**Example:** For the profile above, *Library Rain* (lofi, chill, energy=0.35, acousticness=0.86) scores:
- +2.0 genre + +1.0 mood + (1.0 − |0.35 − 0.40|) + +0.5 acoustic = **4.45**

While *Storm Runner* (rock, intense, energy=0.91, acousticness=0.10) scores:
- +0.0 + +0.0 + (1.0 − |0.91 − 0.40|) + +0.0 = **0.49**

---

### Data Flow (Phase 2 Design)

```mermaid
flowchart TD
    A[User Preferences\ngenre · mood · target_energy · likes_acoustic] --> B[Load songs.csv\n20 songs]
    B --> C{For each Song}
    C --> D[Genre match?\n+2.0 pts]
    C --> E[Mood match?\n+1.0 pts]
    C --> F[Energy similarity\n+0.0–1.0 pts]
    C --> G[Acoustic bonus?\n+0.5 pts]
    D & E & F & G --> H[Total Score]
    H --> I[Sort all songs\nby score descending]
    I --> J[Return top K\nRecommendations]
    J --> K[Explain each pick\nwhy it ranked well]
```

---

### Expected Biases (Phase 2 Design)

- **Genre dominance:** At +2.0 points, a genre match outweighs a perfect mood+acoustic fit (+1.5). A great *chill jazz* track will always lose to a mediocre *chill lofi* track for a lofi-preferring user.
- **Energy range compression:** The energy similarity term is always between 0 and 1, so two songs that both miss the genre tag but have very different energies are barely distinguished.
- **Catalog skew:** 3 of 20 songs are lofi; users who prefer less-represented genres (e.g. metal, blues) will see weaker top matches.
- **Binary acoustic bonus:** `likes_acoustic` is a hard threshold (≥0.6), not a gradient — a song at 0.59 acousticness gets no bonus despite being nearly acoustic.

📍 **Checkpoint:** You have a written concept for real-world vs. simulated recommenders, explicit `Song` / `UserProfile` fields, a weighted scoring recipe, a data-flow diagram, and documented biases.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Terminal Output

![Recommendation output](assets/termminal_output.png)

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

