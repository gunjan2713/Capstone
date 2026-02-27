"""
Synthetic tweet generator for Summer 2020 (BLM, George Floyd protests, police brutality, Defund the Police).
- Reference: Summer2020_tweets2.csv (column "Text"). Used only to avoid duplicating its content.
- Uniqueness: content (hashtags stripped) + no repeated sentence in output. Inline + trailing hashtags.
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


SOURCE_CSV = "Summer2020_tweets2.csv"
OUTPUT_CSV = "Summer2020_synthetic_posts.csv"
TARGET_COUNT = 30_000
MIN_WORDS = 6
MAX_WORDS = 58
TEXT_COLUMN = "Text"  # Summer2020_tweets2.csv uses "Text"

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


def load_reference_contents(path: str, text_column: str, limit: int = 50000) -> Set[str]:
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


# ---------- Hashtags from scraped Summer 2020 tweets + related ----------
HASHTAG_POOL = [
    "BLM", "BlackLivesMatter", "PoliceBrutality", "JusticeForGeorgeFloyd", "RIPGeorgeFloyd",
    "DefundThePolice", "NoJusticeNoPeace", "ACAB", "Election2020", "BidenHarris2020", "Trump2020",
    "VoteBlue", "VoteRed", "BlueWave", "BlueWave2020", "Resist", "Resisters", "NotMeUs",
    "protests", "GeorgeFloyd", "WeWillNotForget", "EndSARS", "EndSWAT", "Minneapolis",
    "Seattle", "Portland", "Chicago", "NYC", "LA", "Atlanta", "DC", "Philadelphia",
    "I Cant Breathe", "SayTheirNames", "BlackVoicesMatter", "SupportBlackBusinesses",
    "HarrisBiden2020", "VoteBlueToEndThisNightmare", "MakeAPlan", "BlackHistoryMonth",
]
# Normalize: hashtags are alphanumeric; "I Cant Breathe" -> ICantBreathe for display
HASHTAG_POOL = [t.replace(" ", "") for t in HASHTAG_POOL]

INLINE_HASHTAG_REPLACEMENTS = [
    ("The protests", "The #protests"),
    ("BLM ", "#BLM "),
    ("Black Lives Matter", "#BlackLivesMatter"),
    ("George Floyd", "#GeorgeFloyd"),
    ("police brutality", "#PoliceBrutality"),
    ("Defund the police", "#DefundThePolice"),
    ("No justice no peace", "#NoJusticeNoPeace"),
    ("in Minneapolis", "in #Minneapolis"),
    ("in Seattle", "in #Seattle"),
    ("in Portland", "in #Portland"),
    ("in Chicago", "in #Chicago"),
    ("in Atlanta", "in #Atlanta"),
    ("The movement", "The #BLM movement"),
    ("protests ", "#protests "),
    ("Election 2020", "#Election2020"),
    ("Biden ", "#Biden "),
    ("Trump ", "#Trump "),
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


# ---------- Fixed sentences (own wording, Summer 2020 themes) ----------
SENTENCES = (
    "The protests spread to every state and millions marched.",
    "George Floyd changed the conversation about race and policing.",
    "Police brutality was the issue that brought people into the streets.",
    "Defund the police became a rallying cry in city after city.",
    "Minneapolis was the spark but the fire was everywhere.",
    "I can't breathe was on every sign and every lip.",
    "Confederate monuments came down and the debate raged.",
    "The summer of 2020 was a reckoning and it is not over.",
    "Peaceful protests and unrest both made the news every night.",
    "No justice no peace was not just a slogan.",
    "The movement demanded change and some cities listened.",
    "Seattle and Portland saw sustained demonstrations for months.",
    "Kneeling during the anthem divided the country again.",
    "Black Lives Matter went from hashtag to household phrase.",
    "Officers were charged and the trials gripped the nation.",
    "Police reform failed in Congress and activists kept pushing.",
    "The election was months away and both sides used the moment.",
    "Corporate America pledged billions to racial justice.",
    "Sports leagues postponed games and took a stand.",
    "CHOP in Seattle was a brief experiment in police-free zones.",
    "Portland became a flashpoint and the federal response drew outrage.",
    "Voting felt like the next step for many after protesting.",
    "Say their names was a reminder that Floyd was one of many.",
    "The protests were mostly peaceful but the images that stuck were not.",
    "Reform versus defund split Democrats and defined the debate.",
    "The president called in federal troops and the mayors said no.",
    "Minneapolis promised to dismantle the police and then walked it back.",
    "Body cameras and training were on the table everywhere.",
    "The summer stretched into fall and the protests did not stop.",
    "Young people led the marches and the polls showed a shift.",
    "All four officers in the Floyd case faced charges.",
    "The country had a conversation it had avoided for too long.",
    "Blue lives matter and Black lives matter faced off on bumper stickers and signs.",
    "Police unions pushed back and reform stalled in many places.",
    "Breonna Taylor became a name everyone knew and justice never came.",
    "Louisville and Minneapolis and Kenosha were in the headlines for months.",
    "The narrative of riots versus protests depended on who you asked.",
    "Election Day was a referendum on the summer and the response.",
    "The movement was global and so was the backlash.",
    "Social media amplified every moment and every clash.",
    "The National Guard was deployed in multiple states.",
    "Curfews did not stop the demonstrations in most cities.",
    "The conversation about race and policing is not over.",
    "Some cities cut police budgets and others increased them.",
    "The summer of 2020 will be in the history books.",
)


def fails_safety(text: str) -> bool:
    lowered = text.lower()
    for phrase in ["should be hurt", "should be killed", "deserve to die", "hang them", "shoot them"]:
        if phrase in lowered:
            return True
    return False


# ---------- Template-based generator for 30k+ unique sentences ----------
SUBJECTS = [
    "The protests", "BLM", "The movement", "George Floyd", "Police brutality", "The police",
    "Minneapolis", "Seattle", "Portland", "The summer", "The president", "Democrats",
    "Republicans", "The media", "Protesters", "The National Guard", "City councils",
    "Police unions", "The streets", "The country", "Young people", "Voters",
    "The election", "Corporate America", "Sports leagues", "The conversation",
    "Reform", "Defund", "The charges", "The trials", "Federal troops", "Mayors",
    "The narrative", "Body cameras", "Training", "The anthem", "Monuments",
    "Breonna Taylor", "Louisville", "Kenosha", "Chicago", "Atlanta", "DC",
    "The reckoning", "The backlash", "Social media", "Curfews", "The budget",
]
VERBS_AND_RESTS = [
    ("spread", "and the world watched"),
    ("changed", "everything in a matter of days"),
    ("brought", "millions into the streets"),
    ("became", "the rallying cry of the summer"),
    ("divided", "the country and the parties"),
    ("forced", "a conversation nobody could ignore"),
    ("demanded", "reform and some demanded defund"),
    ("saw", "peaceful marches and nights of unrest"),
    ("heard", "I can't breathe on every corner"),
    ("took", "down monuments and put up new ones"),
    ("failed", "in Congress and activists kept pushing"),
    ("pledged", "billions and critics called it performative"),
    ("postponed", "games and took a stand"),
    ("charged", "the officers and the trials followed"),
    ("deployed", "the Guard and the mayors objected"),
    ("cut", "budgets in some cities and raised them in others"),
    ("stalled", "in statehouses and moved in the streets"),
    ("gripped", "the nation for months"),
    ("raged", "on social media and on the news"),
    ("shifted", "the polls and the election"),
    ("defined", "the summer and the year"),
    ("amplified", "every moment and every clash"),
    ("led", "the marches and the conversation"),
    ("pushed back", "and reform stalled"),
    ("listened", "in some places and dug in elsewhere"),
    ("sparked", "protests in every state"),
    ("made", "headlines every night"),
    ("drew", "outrage and support in equal measure"),
    ("became", "a flashpoint and a symbol"),
    ("reminded", "the country that Floyd was one of many"),
    ("split", "Democrats and defined the debate"),
    ("stretched", "into fall and did not stop"),
    ("depended", "on who you asked"),
    ("was", "not over when the leaves turned"),
]
MIDDLE_INSERTS = [
    "", " in Minneapolis", " in Seattle", " in Portland", " in Chicago", " in Atlanta",
    " in DC", " in Louisville", " in Kenosha", " in 2020", " that summer",
    " across the country", " in city after city", " night after night",
]
EXTRA_TAILS = [
    "", " and that was just the start", " full stop", " and the world noticed",
    " and it is not over", " and the debate rages on", " and so we keep marching",
    " and history will remember", " and the polls shifted", " and the election loomed",
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
        text = text + " The summer of 2020 proved it."
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
