"""
Synthetic tweet generator for Roe/Dobbs 2022 (abortion rights after Roe overturned).
- Reference: Roe2022_tweets.csv (column "Text"). Used only to avoid duplicating its content.
- Uniqueness: content (hashtags stripped) + no repeated sentence in output. Inline + trailing hashtags.
- Target: 30,000 unique posts.
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


SOURCE_CSV = "/Users/nyuad/Downloads/Gunjan/Roe2022_tweets.csv"
OUTPUT_CSV = "/Users/nyuad/Downloads/Gunjan/Roe2022_synthetic_posts_v2.csv"
TARGET_COUNT = 30_000
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


def load_reference_contents(path: str, text_column: str, limit: int = 50_000) -> Set[str]:
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


# Hashtags from Roe2022 + related
HASHTAG_POOL = [
    "RoeVWade",
    "roevwade",
    "AbortionRights",
    "abortionrights",
    "AbortionIsHealthcare",
    "AbortionIsEssential",
    "ProChoice",
    "prochoice",
    "ProLife",
    "prolife",
    "bansoffourbodies",
    "mybodymychoice",
    "bodyautonomy",
    "reprorights",
    "AbortionRightsAreHumanRights",
    "ForcedBirth",
    "VotingRights",
    "Kansas",
    "Dobbs",
    "SCOTUS",
    "SupremeCourt",
    "Midterms2022",
    "VoteBlue",
    "YourBodyYourChoice",
]
HASHTAG_POOL = [t.replace(" ", "") for t in HASHTAG_POOL]

INLINE_HASHTAG_REPLACEMENTS = [
    ("Roe v. Wade", "#RoeVWade"),
    ("Roe was overturned", "#RoeVWade was overturned"),
    ("Roe decision", "#RoeVWade decision"),
    ("Dobbs", "#Dobbs"),
    ("abortion rights", "#AbortionRights"),
    ("abortion is health care", "#AbortionIsHealthcare"),
    ("abortion is healthcare", "#AbortionIsHealthcare"),
    ("pro choice", "#ProChoice"),
    ("pro-choice", "#ProChoice"),
    ("pro life", "#ProLife"),
    ("pro-life", "#ProLife"),
    ("my body my choice", "#mybodymychoice"),
    ("bans off our bodies", "#bansoffourbodies"),
    ("bodily autonomy", "#bodyautonomy"),
    ("SCOTUS", "#SCOTUS"),
    ("Supreme Court", "#SupremeCourt"),
    ("Kansas", "#Kansas"),
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


SENTENCES = (
    "The Supreme Court overturned Roe v. Wade and erased a federal right that stood for nearly fifty years.",
    "Dobbs sent abortion back to the states and the map lit up overnight.",
    "Trigger bans snapped into place and clinics closed their doors in hours.",
    "Patients were turned away in states they had always trusted for care.",
    "Doctors suddenly needed lawyers in the exam room.",
    "Criminal penalties for abortion returned to law books across the South and Midwest.",
    "People started crossing state lines for basic reproductive health care.",
    "Blue states rushed to pass shield laws to protect doctors and patients.",
    "Red states raced each other to write the harshest bans.",
    "The decision landed in the middle of the 2022 midterms and rewrote the stakes.",
    "Protesters filled the steps of the Supreme Court the night the opinion dropped.",
    "The leak in May warned everyone, but the final ruling still hit like a punch.",
    "Kansas shocked the country by voting to keep abortion rights in its constitution.",
    "Even in deep red states voters showed they were not ready for total bans.",
    "Abortion became a kitchen table issue in races that used to be about taxes.",
    "Candidates who had bragged about trigger laws started scrubbing their websites.",
    "Abortion funds saw donations spike and then settle into a new normal.",
    "People learned the word Dobbs the way they once learned Roe.",
    "Medication abortion quietly became the front line of the fight.",
    "Old fights over parental consent and waiting periods suddenly felt quaint.",
    "Prosecutors in some cities promised they would not bring abortion cases.",
    "State courts became the new battleground over constitutions and privacy clauses.",
    "Religious liberty was invoked on both sides of the argument.",
    "The same politicians who shouted about small government wrote intimate medical rules.",
    "Poll after poll showed most Americans wanted Roe kept in place.",
    "Young voters who grew up with Roe as a given watched it vanish overnight.",
    "People shared stories their families had hidden for decades.",
    "Abortion providers weighed security plans along with staffing and budgets.",
    "The decision split some churches and galvanized others.",
    "Every special election after Dobbs turned into a referendum on the ruling.",
)


def fails_safety(text: str) -> bool:
    lowered = text.lower()
    for phrase in ["should be hurt", "should be killed", "deserve to die", "hang them", "shoot them"]:
        if phrase in lowered:
            return True
    return False


SUBJECTS = [
    "The Dobbs decision",
    "Roe v. Wade",
    "Roe",
    "Abortion rights",
    "Abortion bans",
    "State legislatures",
    "Trigger laws",
    "Clinics",
    "Patients",
    "Doctors",
    "Prosecutors",
    "Blue states",
    "Red states",
    "The midterms",
    "Kansas voters",
    "State courts",
    "SCOTUS",
    "The Supreme Court",
    "Pro-choice voters",
    "Pro-life activists",
    "GOP governors",
    "Democratic governors",
    "Ballot initiatives",
    "Abortion funds",
    "Medication abortion",
    "Travel bans",
    "Privacy rights",
    "State constitutions",
    "Congress",
    "Ballot measures",
    "State supreme courts",
    "College students",
    "Suburban women",
    "Faith leaders",
    "Legal scholars",
    "Civil rights groups",
    "Rural voters",
    "Urban voters",
    "Independent voters",
]
VERBS_AND_RESTS = [
    ("overturned", "half a century of precedent"),
    ("returned", "abortion decisions to the states"),
    ("triggered", "a wave of near-total bans"),
    ("sent", "people scrambling for information and options"),
    ("put", "doctors in legal and ethical limbo"),
    ("forced", "patients to cross state lines for care"),
    ("rewrote", "the stakes of the 2022 midterms"),
    ("turned", "Supreme Court races into front page news"),
    ("made", "state constitutions the last line of defense"),
    ("sparked", "protests in cities big and small"),
    ("motivated", "a new wave of young voters"),
    ("split", "suburban districts that once leaned safely red"),
    ("pushed", "abortion onto ballots in places like Kansas"),
    ("tested", "promises to keep government out of private life"),
    ("highlighted", "how far policy can lag behind public opinion"),
    ("reshaped", "how people think about the courts"),
    ("turned", "state supreme courts into unlikely heroes"),
    ("forced", "lawmakers to say out loud what used to be talking points"),
    ("ignited", "new organizing in places that had been written off"),
    ("elevated", "reproductive rights to a top-tier issue"),
    ("put", "privacy rights at the center of the conversation"),
    ("exposed", "the gap between campaign slogans and real-world laws"),
    ("reframed", "the midterms as a referendum on bodily autonomy"),
    ("crystallized", "decades of advocacy into one summer"),
]
MIDDLE_INSERTS = [
    "",
    " in red states",
    " in blue states",
    " in swing states",
    " in 2022",
    " after June 24",
    " in the courts",
    " at the ballot box",
    " in statehouses",
    " on the campaign trail",
    " in purple suburbs",
    " in college towns",
    " in rural counties",
    " in governor races",
    " in attorney general races",
]
EXTRA_TAILS = [
    "",
    " and voters noticed",
    " and the backlash was immediate",
    " and the fight moved to the states",
    " and the legal questions keep coming",
    " and November came fast",
    " and it is not over",
    " and the organizing has barely begun",
    " and nobody can put this genie back in the bottle",
]


def generate_unique_sentence(seen_sentences: Set[str]) -> str:
    for _ in range(1500):
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
        text = text + " The Dobbs ruling proved it."
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

        if len(posts) - last_log >= 500 or len(posts) == TARGET_COUNT:
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

