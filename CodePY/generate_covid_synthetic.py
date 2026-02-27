"""
Synthetic tweet generator for COVID-19 pandemic (lockdowns, masks, vaccines, mandates).
- Reference: covid_tweets3.csv (column "Text"). Used only to avoid duplicating its content.
- Uniqueness: content (hashtags stripped) + no repeated sentence in output. Inline + trailing hashtags.
- Target: 50,000 unique posts.
"""
import csv
import random
import re
import sys
import time
from typing import List, Set

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, "reconfigure") else None

def log(msg: str) -> None:
    print(msg, flush=True)


SOURCE_CSV = "covid_tweets3.csv"
OUTPUT_CSV = "Covid_synthetic_posts.csv"
TARGET_COUNT = 50_000
MIN_WORDS = 6
MAX_WORDS = 58
TEXT_COLUMN = "Text"

HASHTAG_RE = re.compile(r"\s#\w+")
URL_RE = re.compile(r"https?://\S+")
MENTION_RE = re.compile(r"@\w+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def normalize_content(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    t = text.strip().lower()
    t = URL_RE.sub("", t)
    t = MENTION_RE.sub("", t)
    t = HASHTAG_RE.sub("", t)
    t = re.sub(r"[^\w\s.,!?']", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def extract_sentences(post: str) -> List[str]:
    content = normalize_content(post)
    if not content:
        return []
    parts = SENTENCE_SPLIT_RE.split(content)
    return [p.strip() for p in parts if len(p.strip().split()) >= 4]


def load_reference_contents(path: str, text_column: str, limit: int = 100000) -> Set[str]:
    out: Set[str] = set()
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = (row.get(text_column) or "").strip()
                if not text or len(text) < 20:
                    continue
                norm = normalize_content(text)
                if len(norm.split()) >= 5:
                    out.add(norm)
                if len(out) >= limit:
                    break
    except FileNotFoundError:
        pass
    return out


# ---------- Hashtags from scraped COVID tweets + related ----------
HASHTAG_POOL = [
    "COVID19", "Coronavirus", "Covid19", "MaskUp", "vaccines", "VaccinesWork", "CovidVaccine",
    "CovidIsNotOver", "pandemic", "lockdown", "Pfizer", "Moderna", "FDA", "mRNA",
    "VaccineDeaths", "VaccineSideEffects", "Masks", "unvaccinated", "longCOVID",
    "China", "flu", "ARPA", "Fauci", "CDC", "WHO", "vaccine", "GetVaccinated",
    "StayHome", "WearAMask", "SocialDistancing", "TestAndTrace", "Boosters",
    "Omicron", "Delta", "variants", "cases", "deaths", "hospitalizations",
    "remote work", "schools", "mandates", "freedom", "science", "Health",
]
HASHTAG_POOL = [t.replace(" ", "") for t in HASHTAG_POOL]

INLINE_HASHTAG_REPLACEMENTS = [
    ("COVID-19", "#COVID19"),
    ("COVID ", "#COVID19 "),
    ("The pandemic", "The #pandemic"),
    ("vaccines ", "#vaccines "),
    ("The vaccine", "The #vaccine"),
    ("masks ", "#Masks "),
    ("lockdown ", "#lockdown "),
    ("Pfizer ", "#Pfizer "),
    ("Moderna ", "#Moderna "),
    ("Fauci ", "#Fauci "),
    ("The CDC", "The #CDC"),
    ("The FDA", "The #FDA"),
    ("in China", "in #China"),
    ("long COVID", "#longCOVID"),
    ("The flu", "The #flu"),
]


def add_inline_hashtags(text: str) -> str:
    if random.random() > 0.55:
        return text
    options = [(p, r) for p, r in INLINE_HASHTAG_REPLACEMENTS if p in text]
    if not options:
        return text
    random.shuffle(options)
    out = text
    n = 2 if len(options) >= 2 and random.random() < 0.35 else 1
    for i in range(min(n, len(options))):
        phrase, replacement = options[i]
        if phrase in out:
            out = out.replace(phrase, replacement, 1)
    return out


def pick_hashtags() -> str:
    n = random.randint(0, 3)
    if n == 0:
        return ""
    tags = random.sample(HASHTAG_POOL, min(n, len(HASHTAG_POOL)))
    return " " + " ".join("#" + t for t in tags)


# ---------- Fixed sentences (COVID themes: lockdown, masks, vaccines, pandemic) ----------
SENTENCES = (
    "The pandemic shut down the world in 2020 and nothing was the same.",
    "Masks became mandatory in most places and the debate never ended.",
    "Vaccines rolled out in record time and so did the skepticism.",
    "Lockdowns saved lives and destroyed livelihoods depending on who you asked.",
    "The CDC changed its guidance so many times that nobody could keep up.",
    "Remote work went from perk to default and many never went back.",
    "Schools closed and parents lost their minds in every time zone.",
    "Hospitalizations spiked and ICU beds ran out in wave after wave.",
    "Long COVID became a reality for millions and the research is still catching up.",
    "Vaccine mandates divided workplaces and families and the courts.",
    "Fauci was the face of the response and the target of the backlash.",
    "The flu disappeared for a season and then came back with a vengeance.",
    "Travel stopped and then restarted with tests and quarantine rules.",
    "Boosters were recommended and then recommended again and again.",
    "Omicron changed the game and so did every variant before it.",
    "Anti-vax and pro-vax became identities and the middle got quieter.",
    "Deaths passed a million in the US and the count kept climbing.",
    "Supply chains broke and toilet paper became a symbol of the panic.",
    "Zoom replaced the office and nobody knew for how long.",
    "The pandemic was not over when the mandates came down.",
    "China locked down cities and the world watched and debated.",
    "mRNA vaccines were a breakthrough and a conspiracy depending on who you asked.",
    "Hospitals were overwhelmed and health workers were exhausted.",
    "The economy crashed and then rebounded and then wobbled again.",
    "Kids lost a year of school and the effects are still unclear.",
    "Trust in science and government took a hit and has not fully recovered.",
    "At-home tests finally arrived and the lines at PCR sites got shorter.",
    "The pandemic rewired how we work and live and it is not done.",
)


def fails_safety(text: str) -> bool:
    lowered = text.lower()
    for phrase in ["should be hurt", "should be killed", "deserve to die", "hang them", "shoot them"]:
        if phrase in lowered:
            return True
    return False


# ---------- Template-based generator for 50k+ unique sentences ----------
SUBJECTS = [
    "The pandemic", "COVID", "The vaccine", "Vaccines", "Masks", "Lockdowns", "The CDC",
    "The FDA", "Fauci", "Pfizer", "Moderna", "Hospitals", "Schools", "Travel",
    "The economy", "Remote work", "Cases", "Deaths", "Hospitalizations", "Variants",
    "Omicron", "Delta", "Long COVID", "Mandates", "The government", "Scientists",
    "Health workers", "Parents", "Kids", "The flu", "China", "Supply chains",
    "Zoom", "Tests", "Boosters", "Antivax", "The media", "Trust", "Science",
    "Guidance", "Quarantine", "Social distancing", "ICU beds", "Ventilators",
    "The first wave", "The second wave", "Waves", "Outbreaks", "Clusters",
    "Asymptomatic spread", "Breakthrough cases", "Natural immunity", "Masks in schools",
]
VERBS_AND_RESTS = [
    ("shut down", "everything in 2020"),
    ("changed", "how we live and work"),
    ("divided", "the country and families"),
    ("saved", "lives and cost jobs"),
    ("rolled out", "in record time"),
    ("spiked", "and hospitals were overwhelmed"),
    ("dropped", "when vaccines arrived"),
    ("came back", "with every new variant"),
    ("confused", "everyone with mixed messaging"),
    ("mandated", "masks and then vaccines"),
    ("closed", "schools and businesses"),
    ("exhausted", "health workers and the public"),
    ("broke", "supply chains and routines"),
    ("shifted", "to remote and never fully back"),
    ("recommended", "boosters and more boosters"),
    ("debated", "mandates and freedom"),
    ("overwhelmed", "ICUs and morgues"),
    ("waned", "and so did immunity"),
    ("evolved", "faster than the guidance"),
    ("tested", "patience and the system"),
    ("killed", "millions and left millions more with long COVID"),
    ("rewired", "work and travel and trust"),
    ("forced", "choices nobody wanted to make"),
    ("lasted", "longer than anyone predicted"),
    ("ended", "in name only in most places"),
    ("split", "pro-vax and anti-vax for good"),
    ("delayed", "surgeries and care and life"),
    ("reduced", "the flu one year and then it roared back"),
    ("required", "tests and masks and then did not"),
    ("proved", "vaccines worked and skeptics dug in"),
    ("strained", "hospitals and schools and mental health"),
    ("defined", "2020 and 2021 and beyond"),
    ("made", "Zoom a verb and Fauci a target"),
    ("left", "long COVID and burnout in its wake"),
    ("opened", "and closed and opened again"),
    ("fueled", "inflation and labor shortages"),
    ("accelerated", "remote work and online everything"),
]
MIDDLE_INSERTS = [
    "", " in 2020", " in 2021", " in 2022", " across the country", " in cities",
    " in schools", " in hospitals", " in workplaces", " in China", " in Europe",
    " again", " for months", " for a year", " and again", " in waves",
]
EXTRA_TAILS = [
    "", " and the debate rages on", " full stop", " and nothing was the same",
    " and it is not over", " and the data kept changing", " and so did the rules",
    " and trust took a hit", " and the world moved on", " and we are still counting",
    " and the guidance flipped", " and the lines were long", " and the shots were free",
]


def generate_unique_sentence(seen_sentences: Set[str]) -> str:
    for _ in range(800):
        sub = random.choice(SUBJECTS)
        verb, rest = random.choice(VERBS_AND_RESTS)
        middle = random.choice(MIDDLE_INSERTS)
        tail = random.choice(EXTRA_TAILS)
        s = f"{sub} {verb}{middle} {rest}{tail}.".strip()
        if len(s.split()) < 5:
            continue
        norm = normalize_content(s)
        if norm and norm not in seen_sentences:
            return s
    return ""


def generate_candidate(seen_sentences: Set[str]) -> str:
    s1 = generate_unique_sentence(seen_sentences)
    if not s1:
        s1 = random.choice(SENTENCES)
    if random.random() < 0.45:
        s2 = generate_unique_sentence(seen_sentences)
        if not s2:
            s2 = random.choice(SENTENCES)
        if s2 != s1:
            text = s1 + " " + s2
        else:
            text = s1
    else:
        text = s1
    text = text.strip()
    words = text.split()
    if len(words) < MIN_WORDS:
        text = text + " The pandemic proved it."
    elif len(words) > MAX_WORDS:
        text = " ".join(words[:MAX_WORDS])
    text = text.strip()
    text = add_inline_hashtags(text)
    tags = pick_hashtags()
    return text + tags


def main() -> None:
    log("Loading reference tweets to avoid duplicating full content...")
    reference = load_reference_contents(SOURCE_CSV, TEXT_COLUMN)
    log(f"Loaded {len(reference)} reference contents.")

    log(f"Target: {TARGET_COUNT} unique posts. Uniqueness = content + no repeated sentence in output.")
    posts: List[str] = []
    seen_content: Set[str] = set()
    seen_sentences: Set[str] = set()
    last_log = 0
    last_heartbeat = time.monotonic()
    attempts = 0

    while len(posts) < TARGET_COUNT:
        now = time.monotonic()
        if now - last_heartbeat >= 15:
            log(f"Still working... {len(posts)} / {TARGET_COUNT} (attempts: {attempts})...")
            last_heartbeat = now

        candidate = generate_candidate(seen_sentences)
        attempts += 1
        if fails_safety(candidate):
            continue

        content_key = normalize_content(candidate)
        if not content_key or len(content_key.split()) < MIN_WORDS:
            continue
        if content_key in seen_content:
            continue
        if content_key in reference:
            continue

        sentences = extract_sentences(candidate)
        if any(s in seen_sentences for s in sentences):
            continue

        seen_content.add(content_key)
        for s in sentences:
            seen_sentences.add(s)
        posts.append(candidate)

        if len(posts) - last_log >= 1000 or len(posts) == TARGET_COUNT:
            log(f"Generated {len(posts)} / {TARGET_COUNT} synthetic posts...")
            last_log = len(posts)

    log(f"Final count: {len(posts)}")
    log(f"Writing to {OUTPUT_CSV}...")
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text"])
        for text in posts:
            writer.writerow([text])
    log(f"Done. Wrote {len(posts)} posts to {OUTPUT_CSV}. Content unique; no duplicate sentences.")


if __name__ == "__main__":
    main()
