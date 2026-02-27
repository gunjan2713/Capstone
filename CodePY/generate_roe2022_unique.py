import csv
import random
import re
from typing import List, Set, Tuple


# Work on the existing synthetic file by default
INPUT_PATH = "Roe2022_synthetic_posts_unique.csv"
OUTPUT_PATH = "Roe2022_synthetic_posts_unique.csv"
TARGET_COUNT = 20000
MIN_WORDS = 6
MAX_WORDS = 60


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
HASHTAG_RE = re.compile(r"\s#\w+")


def rough_duplicate_key(text: str, max_words: int = 18) -> str:
    """
    Notion of duplication that is much closer to what you want:
    - Lowercase
    - Strip quotes
    - Remove hashtags
    - Take the first sentence only
    - Then take the first N words of that sentence

    Any posts that share the same leading clause (e.g. repeated question stem)
    will be treated as duplicates, even if the endings or hashtags differ.
    """
    stripped = (text or "").strip().strip('"').strip("'").lower()
    if not stripped:
        return ""
    # Drop hashtags so different tag mixes don't matter
    no_tags = HASHTAG_RE.sub("", stripped)
    parts = SENTENCE_SPLIT_RE.split(no_tags)
    first = parts[0] if parts else no_tags
    key = first.strip()
    if not key:
        return ""
    words = key.split()
    if len(words) > max_words:
        words = words[:max_words]
    return " ".join(words)


def load_unique_posts(path: str) -> Tuple[List[str], Set[str]]:
    # seen_full: exact full-text duplicates
    seen_full: Set[str] = set()
    # seen_rough: same leading clause / sentence, even if rest differs
    seen_rough: Set[str] = set()
    ordered: List[str] = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "text" not in reader.fieldnames:
            raise ValueError("CSV must have a 'text' column")

        for row in reader:
            raw = row.get("text") or ""
            text = raw.strip()
            if not text:
                continue

            # Exact duplicate of whole post
            if text in seen_full:
                continue

            # Duplicate of leading sentence / clause
            key = rough_duplicate_key(text)
            if not key:
                continue
            if key in seen_rough:
                continue

            seen_full.add(text)
            seen_rough.add(key)
            ordered.append(text)

    # We return full-text set for fast "have we used this exact string" checks later.
    return ordered, seen_full


# Phrase banks for synthetic post generation

INTROS_QUESTION = [
    "How do we pretend this is freedom",
    "How are we supposed to call this justice",
    "Does anyone honestly believe this is how rights should work",
    "Can someone explain how this counts as equality",
    "What kind of democracy rolls back fundamental rights like this",
    "When did we decide precedent only matters sometimes",
    "At what point do we admit this system is failing people",
    "How is this anything but state control over private lives",
]

SUBJECTS_RIGHTS = [
    "bodily autonomy",
    "reproductive freedom",
    "the right to plan a family",
    "privacy in conversations with our doctors",
    "the promise that rights expand, not shrink",
    "control over our own pregnancies",
    "basic healthcare access",
    "the idea of equal citizenship",
]

INSTITUTION_TARGETS = [
    "a radical court majority",
    "state legislators racing to outdo each other's bans",
    "politicians using our lives as talking points",
    "lawmakers who will never face these consequences themselves",
    "attorneys general eager to criminalize doctors",
    "governors signing bans at celebratory rallies",
    "party strategists treating rights as bargaining chips",
    "lobbyists writing model bills behind closed doors",
]

CONSEQUENCE_PHRASES = [
    "people in medical crisis being told to wait until they are sicker",
    "patients having to cross state lines just to see a doctor",
    "survivors of assault being turned into legal test cases",
    "rural communities losing what little reproductive healthcare they had",
    "doctors leaving hostile states rather than risk prison",
    "parents being forced to choose between rent and travel for care",
    "young people delaying dreams because they cannot trust their rights",
    "emergency rooms turning into legal battlefields instead of places of care",
]

HASHTAG_BLOCKS = [
    "",
    "#Roe2022",
    "#Dobbs",
    "#AbortionRights",
    "#ReproductiveJustice",
    "#MyBodyMyChoice",
    "#AbortionIsHealthcare",
    "#ProtectOurRights",
    "#BodilyAutonomy",
    "#SCOTUS",
]


def build_rhetorical_question() -> str:
    intro = random.choice(INTROS_QUESTION)
    target = random.choice(INSTITUTION_TARGETS)
    right = random.choice(SUBJECTS_RIGHTS)
    consequence = random.choice(CONSEQUENCE_PHRASES)
    tag = random.choice(HASHTAG_BLOCKS)

    base = (
        f"{intro} when {target} acts like this is normal, "
        f"and {right} turns into a privilege instead of a right, "
        f"with {consequence}?"
    )
    if tag:
        base += f" {tag}"
    return base


MOBILIZATION_INTROS = [
    "If you are angry, do not stop there",
    "Feeling scared is valid, but we cannot stay frozen",
    "Shock fades, but organizing has to continue",
    "If this ruling shook you, let it also move you",
    "We cannot control the court today, but we can control our response",
    "Rights are not self‑defending; people defend them",
]

MOBILIZATION_ACTIONS = [
    "register, vote, and bring friends with you",
    "support local candidates who commit to protecting bodily autonomy",
    "donate to abortion funds and legal defense groups if you can",
    "show up for protests that center those most affected",
    "learn your state's laws and help others understand what changed",
    "call and write lawmakers even when you think they are not listening",
]

MOBILIZATION_ENDINGS = [
    "This ruling is not the last word.",
    "They made their decision; now we make ours at the ballot box.",
    "History will remember who stayed silent.",
    "Future generations will ask what we did next.",
    "The loss is real, but so is our power together.",
]


def build_mobilization_post() -> str:
    intro = random.choice(MOBILIZATION_INTROS)
    action = random.choice(MOBILIZATION_ACTIONS)
    ending = random.choice(MOBILIZATION_ENDINGS)
    tag = random.choice(HASHTAG_BLOCKS)

    pieces = [
        f"{intro}.",
        f"Channel that energy into action: {action}.",
        ending,
    ]
    text = " ".join(pieces)
    if tag:
        text += f" {tag}"
    return text


WARNING_INTROS = [
    "The fallout from this decision will not stop at one issue",
    "People keep saying this is only about one procedure",
    "Anyone who thinks this will not touch them is not paying attention",
    "This is what happens when ideology overrules medicine",
    "The fine print of these bans is where the real damage hides",
]

WARNING_FUTURES = [
    "doctors second‑guessing life‑saving care because of prosecutors",
    "miscarriages becoming courtroom evidence instead of medical emergencies",
    "patients delaying treatment until it is almost too late",
    "cross‑state fights over who controls pregnancies and medical records",
    "privacy rights for queer families being questioned next",
    "contraception access becoming the next political battleground",
]

WARNING_CALLS = [
    "We need clear protections for healthcare and privacy in law.",
    "States that still protect rights must not take that for granted.",
    "Courts and lawmakers should not be allowed to hide behind vague language.",
    "People deserve laws written with real medical input, not talking points.",
    "We have to listen to doctors, patients, and legal experts warning us now.",
]


def build_warning_post() -> str:
    intro = random.choice(WARNING_INTROS)
    future = random.choice(WARNING_FUTURES)
    call = random.choice(WARNING_CALLS)
    tag = random.choice(HASHTAG_BLOCKS)

    text = (
        f"{intro}. Today it is abortion, tomorrow it could mean {future}. "
        f"{call}"
    )
    if tag:
        text += f" {tag}"
    return text


REFLECTIVE_OPENERS = [
    "I keep thinking about friends in states rushing to ban care",
    "I am scared for people who were already barely getting by",
    "I am relieved my state protected rights, but it feels fragile",
    "I am exhausted by having the same arguments about basic autonomy",
    "I am heartbroken for everyone who woke up with fewer options",
]

REFLECTIVE_MIDDLES = [
    "This was not an abstract court case for them.",
    "Their lives, jobs, and families are now tied to someone else's ideology.",
    "They will have to calculate travel, time off, and safety just to see a doctor.",
    "They deserved stability, not a countdown to losing rights.",
    "They trusted a promise that rights move forward, not backward.",
]

REFLECTIVE_ENDINGS = [
    "I refuse to call this progress.",
    "I will not pretend this is normal.",
    "I hope we remember their names when we vote.",
    "I do not want fear to feel like the new baseline.",
    "I hope this grief turns into something powerful and protective.",
]


def build_reflective_post() -> str:
    opener = random.choice(REFLECTIVE_OPENERS)
    middle = random.choice(REFLECTIVE_MIDDLES)
    ending = random.choice(REFLECTIVE_ENDINGS)
    tag = random.choice(HASHTAG_BLOCKS)

    text = f"{opener}. {middle} {ending}"
    if tag:
        text += f" {tag}"
    return text


def generate_candidate_post() -> str:
    builders = [
        build_rhetorical_question,
        build_mobilization_post,
        build_warning_post,
        build_reflective_post,
    ]
    builder = random.choice(builders)
    text = builder().strip()
    words = text.split()

    # Enforce word count limits
    if len(words) < MIN_WORDS:
        # Pad with a short, safe clause if needed
        text = text + " This is about real people's lives."
    elif len(words) > MAX_WORDS:
        # Trim overly long posts
        text = " ".join(words[:MAX_WORDS])

    return text.strip()


def main() -> None:
    base_posts, seen_full = load_unique_posts(INPUT_PATH)
    print(f"Loaded {len(base_posts)} posts after strict de-duplication.")

    needed = max(0, TARGET_COUNT - len(base_posts))
    print(f"Target count: {TARGET_COUNT}. Need to add {needed} new unique posts.")

    new_posts: List[str] = []

    # Precompute rough keys for the existing base posts once
    base_rough_keys = {rough_duplicate_key(p) for p in base_posts}

    while len(new_posts) < needed:
        candidate = generate_candidate_post()
        # Apply the same strict notion of "new":
        if candidate in seen_full:
            continue
        rough_key = rough_duplicate_key(candidate)
        if not rough_key or rough_key in base_rough_keys:
            continue

        seen_full.add(candidate)
        base_rough_keys.add(rough_key)
        new_posts.append(candidate)

        if len(new_posts) % 500 == 0:
            print(f"Generated {len(new_posts)} / {needed} new posts...")

    all_posts = base_posts + new_posts
    print(f"Final total posts: {len(all_posts)}")

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text"])
        for text in all_posts:
            writer.writerow([text])

    print(f"Wrote deduplicated posts to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

