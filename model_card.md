# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder 1.0 tries to answer one question: *given what a user says they like,
which songs in a small catalog are the best match?*

It does not predict whether a user will enjoy a song. It does not learn from
listening history. It simply compares each song's attributes against a user's
stated preferences and ranks the songs by how closely they match. The output is a
short ranked list with a plain-English explanation for each pick.

---

## 3. Data Used

The catalog contains **20 songs** across **14 genres** and **9 moods**.

Each song has 8 attributes: `id`, `title`, `artist`, `genre`, `mood`, `energy`
(0–1), `tempo_bpm`, `valence`, `danceability`, and `acousticness` (0–1).

Ten songs came with the starter project. Ten more were added to cover genres and
moods that were absent — blues, classical, soul, metal, hip-hop, funk, r&b, country,
reggae, and electronic.

**Limits of the data:**
- Energy, acousticness, and other numeric values were assigned by hand, not measured
  from audio. They reflect an estimate, not a ground truth.
- Latin, K-pop, folk, and country-pop are missing entirely.
- Lyrics, language, and cultural context are not represented at all.
- The catalog is far too small to reflect the breadth of real music taste.

---

## 4. Algorithm Summary

Every song in the catalog gets a score. Think of it like a judge at a talent show
awarding scorecards for each act.

The judge uses four scorecards:

1. **Genre card (+2 points):** If the song's genre exactly matches what the user
   prefers (e.g., both are "lofi"), it earns 2 points. If not, zero.

2. **Mood card (+1 point):** If the song's mood matches the user's preferred mood
   (e.g., both "chill"), it earns 1 point. If not, zero.

3. **Energy card (0 to 1 point):** The closer a song's energy is to the user's
   target number, the more points it earns. A perfect match gives 1 full point;
   a song at the opposite extreme gets close to 0.

4. **Acoustic bonus (+0.5 points):** If the user said they enjoy acoustic music and
   the song's acousticness is 0.6 or higher, it gets a small extra bonus.

All four scores are added together. Songs are sorted from highest to lowest total
score, and the top five are returned with a sentence explaining each rank.

---

## 5. Observed Behavior / Biases

**Genre dominance creates vibe blindness.** A genre match (+2.0) is worth twice as
much as a mood match (+1.0) and can be more than twice as large as the entire energy
similarity term (which maxes out at +1.0). In the "Conflicting Vibe" test — a user
who wanted *blues, sad music at high energy* — the system ranked *Blue Sunday*
(energy 0.33) as #1, even though the user's stated energy target was 0.9. The genre
and mood bonus (+3.0 total) completely overrode the poor energy fit (+0.43).

**Energy is present but suppressed.** When genre weight was halved and energy
multiplier was doubled in the experiment, rankings #2–5 completely reshuffled toward
high-energy songs. The signal was there all along — the default weights just buried
it.

**Catalog skew punishes niche tastes.** Pop and lofi each have three songs; blues,
metal, classical, and soul each have only one. A blues fan gets one genre-match
result (#1), then the system falls back to mood and energy for #2–5, often returning
songs with a completely different vibe.

**Binary acoustic threshold.** The acoustic bonus cuts off at exactly 0.6
acousticness. A song at 0.59 gets nothing; one at 0.60 gets +0.5. There is no
gradient — a near-acoustic song is treated the same as a fully electric one.

**No diversity enforcement.** The system can return the same artist twice in the
top five (LoRoom appears twice for the Chill Lofi profile) because it optimizes
purely for score, never for variety.

---

## 6. Evaluation Process

Five user profiles were run through the recommender:

| Profile | Key prefs | Purpose |
|---|---|---|
| High-Energy Pop | pop / happy / 0.90 | baseline popular taste |
| Chill Lofi | lofi / chill / 0.40 / acoustic | well-represented genre |
| Deep Intense Rock | rock / intense / 0.95 | single-song genre test |
| Conflicting Vibe | blues / sad / 0.90 | adversarial — mood vs. energy tension |
| Niche Acoustic Seeker | classical / melancholic / 0.20 / acoustic | adversarial — rare genre |

**What matched intuition:** Chill Lofi returned all three lofi songs in the top
three, ordered correctly by energy proximity. Deep Intense Rock placed Storm Runner
#1, the only exact genre+mood match in the catalog.

**What was surprising:** Gym Hero (pop/intense) and Electric Thunder (metal/intense)
tied at 1.98 for the rock profile. A rock fan got a pop song and a metal song ranked
identically because the scorer only knows "match" or "no match" — it cannot tell that
metal is closer to rock than pop is.

**Experiment — weight shift:** Genre weight was halved (2.0 → 1.0) and energy
multiplier was doubled (×1 → ×2) for the Conflicting Vibe profile. Blue Sunday
stayed #1 because the combined genre+mood bonus still dominated, but #2–5 completely
reshuffled to high-energy songs. This proved the system is sensitive to weight
choices and that the current defaults favor categorical match over numeric fit.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
- Classroom exploration of how content-based recommender systems work.
- Learning how scoring, ranking, and explainability fit together in a simple pipeline.
- Experimenting with weight choices to see how they change results.

**Not intended for:**
- Real music discovery for actual users — the catalog is 20 songs and the attributes
  are manually estimated, not measured from audio.
- Replacing or comparing to Spotify, Apple Music, or any production recommender.
- Making decisions about musical taste on behalf of a real person.
- Any deployment outside of an educational or prototyping context.

---

## 8. Ideas for Improvement

- **Continuous genre similarity:** Replace exact-match-or-zero with a genre affinity
  table (e.g., rock and metal score 0.8, rock and classical score 0.1) so fans of
  adjacent genres still find good results.

- **Diversity re-ranking:** After scoring, prevent the same artist or genre from
  appearing more than once in the top five, so the list feels varied rather than
  repetitive.

- **Learnable weights:** Let the user rate a few recommendations, then automatically
  adjust genre/mood/energy weights based on what they accepted or skipped — turning
  the fixed recipe into something that adapts to each person.

- **Richer audio features:** Valence and tempo are already in the CSV but unused.
  Incorporating them would let the system distinguish "fast sad" from "slow sad,"
  which the current version cannot do at all.

---

## 9. Personal Reflection

**Biggest learning moment:** The weight experiment in Phase 4 was the clearest
lesson. Before running it, giving genre +2.0 points felt like a reasonable design
choice — genre is the first thing most people mention when describing their taste.
After running it, I could see concretely that this one number made the system
essentially ignore how energetic a song actually is. The "Conflicting Vibe" user
asked for high-energy blues music and got a slow, low-energy song at #1. No amount
of intuition would have caught that without actually testing it. The lesson: design
choices that feel logical before testing can produce counterintuitive behavior at
runtime, and the only way to find that out is to test edge cases on purpose.

**How AI tools helped — and when to double-check:** AI tools were useful for
generating boilerplate quickly (CSV rows, docstrings, the Mermaid flowchart), and
for framing questions like "what adversarial profiles might expose weaknesses in
this scoring logic?" But the tools needed to be checked at every step. Generated
code passed type checks but still had subtle logic issues — for example, the `weights`
parameter initially used `Dict[str, float] = None` as a default instead of
`Optional[Dict[str, float]] = None`, which the IDE flagged. The outputs also needed
to be read critically: an AI suggestion to "double the energy weight" doesn't tell
you *why* or *what the tradeoff is* — understanding that required running the
experiment and reading the results myself.

**What surprised me about simple algorithms "feeling" like recommendations:** The
most surprising thing was how convincing the output looks even when the logic is
shallow. A user who doesn't know the system sees "Midnight Coding — Score 4.48 —
genre match: lofi | mood match: chill | acoustic bonus" and it *feels* like the
system understood them. But the entire decision was made by adding four numbers
together. Real recommenders are more complex, but they are also doing the same basic
thing at their core — converting signals into numbers and ranking them. The
difference is scale and the source of the weights (hand-tuned vs. learned from data).

**What I'd try next:** The change I'd most want to make is moving from binary
genre matching to a genre similarity matrix. Two songs labeled "rock" and "metal"
feel more alike to a listener than "rock" and "classical," but VibeFinder 1.0
treats all non-matches as equally worthless. Adding even a rough similarity table
would make the system feel meaningfully smarter without requiring any machine
learning — just a more honest representation of how musical genres relate to each
other.
