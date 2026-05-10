# The Algorithmic Caricature: Auditing LLM-Generated Political Discourse Across Crisis Events

**Authors:** Gunjan, Sidahmed Benabderrahmane, Talal Rahwan
**Affiliation:** New York University Abu Dhabi (NYUAD), Division of Science, Computer Science

---

## Abstract

Large Language Models (LLMs) are increasingly capable of generating fluent political text, raising concerns about the large-scale production of synthetic discourse during periods of social conflict. While prior detection work has often emphasized local linguistic cues such as perplexity, burstiness, or token-level irregularities, these signals may become less reliable as generative systems improve. In this paper, we adopt a Computational Social Science (CSS) perspective and study synthetic political discourse at the population level rather than the sentence level. We construct a paired multi-event corpus of **1,789,406 posts** spanning nine politically salient crisis events: the COVID-19 pandemic, the Jan 6 Capitol attack, the 2020 US election, the 2024 US election, Dobbs/Roe v. Wade, the 2020 BLM protests, the US midterm elections, the Utah shooting, and the US-Iran war. For each event, we compare *observed* online discourse collected from social platforms with *synthetic* discourse generated to discuss the same event. We evaluate divergence along four dimensions: emotional intensity, structural regularity, lexical-ideological framing, and cross-event dependency.

Across events, synthetic discourse is more negative and less dispersed in sentiment, structurally more regular, and lexically more abstract than observed discourse. In contrast, observed discourse exhibits broader emotional dispersion, longer-tailed structural distributions, and more context-specific and colloquial lexical markers. These differences are not uniform across events: they are typically larger for fast-moving, decentralized crises and smaller for formal, institutionally mediated events. We summarize these differences through a simple event-level divergence measure, which we term the **Caricature Gap**.

Our findings suggest that the main limitation of synthetic political discourse is not grammatical fluency, but reduced population realism. We argue that this population-level perspective offers a useful complement to traditional text-detection approaches and provides a CSS framework for auditing the social realism of generated discourse.

**Keywords:** Computational Social Science · Large Language Models · Synthetic Text · Political Discourse · Social Media Analysis

---

## Repository Layout

| Folder | Contents |
|---|---|
| [CodePY/](CodePY/) | Scrapers ([twitter.py](CodePY/twitter.py), [twitter2.py](CodePY/twitter2.py), [reddit.py](CodePY/reddit.py), [telegram.py](CodePY/telegram.py)) and per-event synthetic-generation scripts (`generate_*.py`). |
| [Scraped/](Scraped/) | Observed posts collected from Twitter/X, Reddit, and Telegram. |
| [Youtube/](Youtube/) | YouTube comments scraped for the 2026 U.S.–Iran war event. |
| [AI/](AI/) | Synthetic posts (clean + adversarial) generated with Gemini 1.5 Pro and Claude Sonnet 3. |
| [Extra/](Extra/) | Auxiliary scraped batches (Summer 2020, Utah, midterms). |
| [Tests/](Tests/) | Notebooks for the RoBERTa detector and the four-pillar population analysis. |
| [us_iran_toxic_synthetic.csv](us_iran_toxic_synthetic.csv) | Toxic synthetic generations for the U.S.–Iran war event. |

---

## Dataset Summary

| Event | Observed | Synthetic | Platforms | Date Range |
|---|---:|---:|---|---|
| COVID-19 pandemic | 59,442 | 50,000 | Twitter | Jan 2020 – Dec 2022 |
| Jan 6 Capitol attack | 279,617 | 20,000 | Twitter, Telegram | Jan 2021 – Feb 2021 |
| 2020 US election | 72,711 | 50,000 | Twitter, Telegram, Reddit | Jun 2020 – Nov 2020 |
| 2024 US election | 126,733 | 150,936 | Twitter, Telegram, Reddit | Jun 2024 – Nov 2024 |
| Dobbs / Roe v. Wade | 11,065 | 30,000 | Twitter | May 2022 – Aug 2022 |
| 2020 BLM protests | 47,577 | 30,000 | Twitter | May 2020 – Sep 2020 |
| US midterm elections | 31,227 | 30,000 | Twitter | Jan 2022 – Nov 2022 |
| Utah shooting | 5,257 | 6,000 | Twitter | Sep 2025 – Oct 2025 |
| US–Iran war | 588,841 | 200,000 | YouTube | Feb 2026 – Mar 2026 |
| **Total** | **1,222,470** | **566,936** | — | — |

We use *observed* rather than *human* because public social media may include bots, coordinated messaging, or machine-assisted content. Our contrast is between **observed online discourse** and **synthetic generated discourse**.

---

## Collection Queries by Event

The following hashtag and keyword sets were used to seed scrapers across Twitter/X, Reddit, Telegram, and YouTube. Targets included X, Reddit (r/The_Donald, r/Conservative, r/Libertarian, r/PoliticalHumor, r/ChapoTrapHouse, r/Progressive, r/Socialism), Gab, Truth Social, and news comment sections (Breitbart, Daily Kos).

### Dobbs / Roe v. Wade
```
"Roe v Wade", "Roe overturned", "Dobbs v Jackson", "SCOTUS",
"#RoeVWade", "#DobbsDecision", "#AbortionRights", "#ProChoice", "#ProLife",
"abortion rights", "reproductive rights", "bodily autonomy",
"Bans Off Our Bodies", "trigger laws", "abortion ban", "clinic protest"
```

### 2020 US Election
```
"election", "election2020", "vote", "voting", "vote2020",
"mail-in", "mail in ballot", "absentee ballot",
"count the votes", "counteveryvote", "stop the steal", "ballot",
"voter suppression", "ballot harvesting", "polling place",
"election fraud", "vote fraud", "voter fraud", "red wave", "blue wave",
"Biden", "BidenHarris", "Trump", "Trump2020",
"#Election2020", "#Vote", "#MailInBallot", "#CountEveryVote",
"#StopTheSteal", "#Biden", "#Trump", "#BlueWave", "#RedWave",
"election night", "election results", "certification",
"electoral college", "electors"
```

### 2024 US Election (paired ideological framing)
**Far-Right / MAGA / Groyper**
- Voices: Charlie Kirk (@charliekirk11), Ben Shapiro, Candace Owens, Nick Fuentes, TPUSA-adjacent accounts
- Hashtags: `#MAGA`, `#Trump2024`, `#AmericaFirst`, `#GroyperArmy`, `#RedWave`, `#CharlieKirk`, `#TurningPointUSA`, `#Conservative`
- Keywords: "Charlie Kirk", "Turning Point USA", "Trump supporter", "Stop the Steal", "patriot", "liberal elites", "America first", "socialism threat", "MAGA"

**Left-Wing / Progressive**
- Voices: AOC, Bernie Sanders, progressive journalists / activists
- Hashtags: `#BLM`, `#DefundThePolice`, `#GreenNewDeal`, `#SocialJustice`, `#MedicareForAll`
- Keywords: "systemic racism", "climate justice", "labor rights", "socialism", "wealth inequality", "corporate greed"

### Utah Shooting (Sept 2025)
```
"University of Utah shooting", "Utah shooting", "Utah campus attack",
"Utah campus lockdown", "Charlie Kirk Utah", "Turning Point USA Utah",
"#UniversityOfUtah", "#UtahShooting", "#CampusSafety", "#GunViolence",
"Utah police", "Salt Lake City protest", "Utah student protest",
"Utah gun control", "Utah university safety"
```

### 2020 BLM Protests
```
# Movement & slogans
"BLM", "Black Lives Matter", "#BLM", "#BlackLivesMatter",
"Justice for George Floyd", "#JusticeForGeorgeFloyd",
"Breonna Taylor", "Ahmaud Arbery",
"Defund the Police", "#DefundThePolice", "Police brutality", "ACAB",

# Protest / enforcement
"protest", "curfew", "riot police", "tear gas", "National Guard",

# City anchors
"Minneapolis protest", "Portland protest", "Seattle protest", "CHAZ", "CHOP",
"Kenosha protest", "Louisville protest", "NYC protest", "Los Angeles protest", "DC protest"
```

### COVID-19 Policies & Vaccine Mandates
```
#VaccineMandate, #COVID19, #HealthPass, #VaccinePassport, #MaskMandate,
#NoVaccineMandate, #EndTheMandates,
"vaccine mandate", "mask mandate", "health pass", "vaccine passport", "lockdown",
"OSHA mandate", "OSHA ETS", "CMS mandate", "federal mandate",
"employer mandate", "school mandate", "religious exemption", "medical exemption",
"mandate protest", "mandate repeal", "mandate lifted",
CDC, "CDC guidance", FDA, NIH, HHS, "Surgeon General",
"Supreme Court", SCOTUS, "Supreme Court OSHA",
"New York mandate", "California mandate", "Florida mandate", "Texas mandate",
"NYC mandate", "LA County mandate", "Chicago mandate",
"state order", "executive order"
```

### US–Iran War (2026)
```
"Iran war", "US Iran war", "U.S. Iran",
"Israel Iran war", "Iran missile attack", "Iran airstrike",
"Tehran attack", "Middle East war", "Middle East escalation",
"Strait of Hormuz", "Hormuz", "Iran nuclear",
"regime change Iran", "Trump Iran", "Netanyahu Iran",
"Qatar Iran attack", "UAE Iran attack", "Bahrain Iran attack",
"US base Iran", "American base Iran"
```

### Event Reference Table

| Event | Timeline | Hashtags / Keywords |
|---|---|---|
| 2020 & 2024 US Presidential Elections | Nov 2020 / Nov 2024 | `#MAGA`, `#Trump2024`, `#StopTheSteal`, `#BlueWave`, `#ElectionFraud`, Trump, Biden |
| January 6 Capitol Attack | Jan 6, 2021 | `#CapitolRiots`, `#StopTheSteal`, `#DCProtest`, `#RedWave`, `#ElectionFraud` |
| Supreme Court — Dobbs | Jun 2022 | `#RoeVWade`, `#AbortionRights`, `#ProLife`, `#ProChoice` |
| COVID-19 Policies & Vaccine Mandates | 2020–2022 | `#VaccineMandate`, `#COVID19`, `#Freedom`, `#HealthPass` |
| Social Justice / Racial Movements (BLM) | Summer 2020 | `#BLM`, `#JusticeForGeorgeFloyd`, `#PoliceBrutality`, `#ACAB` |
| University of Utah Shooting | Sept 2025 | `#UniversityOfUtah`, `#UtahShooting`, `#CampusSafety`, `#GunViolence`, `#UTPolice`, `#CharlieKirk` |
| Midterm Elections | Nov 2018 / Nov 2022 | `#RedWave`, `#BlueWave`, `#Vote2022`, `#Politics` |

---

## The Four-Pillar Framework

We compare observed and synthetic populations along four dimensions:

1. **Pillar 1 — Emotional Intensity.** VADER compound sentiment scores, complemented by Detoxify / `unitary/toxic-bert` toxicity scoring on `[0, 1]`.
2. **Pillar 2 — Structural Regularity.** Word-count and punctuation-ratio distributions, focusing on population-level *spread* rather than the mean.
3. **Pillar 3 — Lexical-Ideological Framing.** TF-IDF unigram/bigram divergence ranking per event, comparing concrete entity-grounded vocabulary against abstract grievance vocabulary.
4. **Pillar 4 — Cross-Event Dependency.** A simple per-event gap measure, the **Caricature Gap**: Δ = |μ_syn − μ_obs|, reported alongside Cohen's *d* and 95% bootstrap confidence intervals.

---

## Key Findings

- **Sentiment.** Observed discourse averages near-neutral (μ = +0.018) while synthetic discourse anchors negative (μ = −0.215; *d* = −0.47). Largest gap on the **2024 US Election** (*d* = −0.98); smallest on **COVID-19** (*d* = −0.14). Dobbs is the only event where synthetic is *more* positive than observed.
- **Structural homogenization.** Synthetic word-count standard deviation is roughly **5× smaller** than observed across the corpus. Synthetic punctuation distributions are tightly concentrated near 0.02–0.04, while observed distributions are wide and right-skewed.
- **Lexical asymmetry.** Observed discourse names actors (*trump, biden, harris, foxnews, kennedy*); synthetic discourse defaults to abstract grievance terms (*lying, elites, fascists, corrupt, puppets, matrix*).
- **Toxicity reversal.** Synthetic is *more* toxic than observed for elections (2024: *d* = +0.82) and Jan 6 (*d* = +0.38), but *less* toxic for BLM (*d* = −0.75), Utah (*d* = −0.50), and Dobbs (*d* = −0.59) — suggesting safety constraints interact non-uniformly with event register.

The magnitude of the Caricature Gap is itself event-dependent: larger for fast-moving, decentralized crises; smaller for formal, institutionally mediated events.

---

## Synthetic Generation

Synthetic posts were produced with **Gemini 1.5 Pro** and **Claude Sonnet 3** under an institutionally approved research-use protocol. Prompts were event-specific and ideology-conditioned (MAGA/Groyper and progressive/left personas), with adversarial variants applying typographic noise, slang substitution (*u, idk, tbh, fr*), punctuation chaos, capitalization irregularities, emotional exaggeration (*sooooo, CRAZY!!!*), sarcasm markers, and fragmentation.

---

## Data Availability

Code and data: <https://github.com/gunjan2713/AuditingSyntheticPoliticalLanguage>

---

## Citation

> Gunjan, Benabderrahmane, S., Rahwan, T. *The Algorithmic Caricature: Auditing LLM-Generated Political Discourse Across Crisis Events.* New York University Abu Dhabi, 2026.


