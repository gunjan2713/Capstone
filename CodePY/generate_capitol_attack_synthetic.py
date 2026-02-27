"""
Synthetic tweet generator for the January 6 Capitol attack (2021).
Output: 20k unique posts, toxic tone, hashtags, Twitter-like style.
No duplicates: first 18 words of first sentence must be unique.
"""
import csv
import random
import re
import sys
import time
from typing import List, Set, Tuple

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, "reconfigure") else None

def log(msg: str) -> None:
    print(msg, flush=True)


SOURCE_CSV = "Capitol_Attack202_tweets.csv"
OUTPUT_CSV = "Capitol_Attack_synthetic_posts.csv"
TARGET_COUNT = 20_000
MIN_WORDS = 6
MAX_WORDS = 55

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
HASHTAG_RE = re.compile(r"\s#\w+")

# Words to strip when building the duplicate key so "this damn X" and "this pathetic X" count as same
KEY_STRIP_WORDS = {
    "damn", "pathetic", "corrupt", "lying", "disgraceful", "disgusting", "spineless",
    "ridiculous", "absurd", "insane", "moronic", "vile", "disgrace", "fraud", "nightmare",
    "incompetent", "embarrassing", "joke", "traitors", "seditionists", "clowns",
    "disaster", "garbage", "crap", "toxic", "crooked", "sham", "farce", "outrageous",
    "idiotic", "stupid", "dumb", "evil", "rotten", "broken", "fake", "honestly", "look",
}


def rough_duplicate_key(text: str, max_words: int = 999) -> str:
    """
    Complete uniqueness: entire first sentence, normalized (strip modifier words).
    So "This damn insurrection was X" and "This pathetic insurrection was X" → same key.
    Same first sentence (after normalizing) = duplicate, no matter what comes after.
    """
    stripped = (text or "").strip().strip('"').strip("'").lower()
    if not stripped:
        return ""
    no_tags = HASHTAG_RE.sub("", stripped)
    parts = SENTENCE_SPLIT_RE.split(no_tags)
    first = parts[0] if parts else no_tags
    key = first.strip()
    if not key:
        return ""
    # Normalize: remove modifier/toxic words so same structure = same key
    words = [w for w in key.split() if w not in KEY_STRIP_WORDS]
    key = " ".join(words)
    if not key:
        return ""
    # Use full normalized first sentence (cap length so key is not huge)
    words = key.split()
    if len(words) > max_words:
        words = words[:max_words]
    return " ".join(words)


# ---------- Toxic vocabulary (institutions / politicians / rioters only; no slurs or violence) ----------
TOXIC_PHRASES = [
    "these corrupt ", "those lying ", "this damn ", "this pathetic ",
    "these incompetent ", "this disgraceful ", "this disgusting ",
    "these spineless ", "this ridiculous ", "this absurd ",
    "these traitors ", "these clowns ", "this nightmare ", "this fraud ",
    "these seditionists ", "this insane ", "these moronic ", "this vile ",
]
TOXIC_ENDINGS = [
    " What a disgrace.", " This is bullshit.", " What a joke.",
    " Disgusting.", " Pathetic.", " They should all be in prison.",
    " Traitors.", " Lock them up.", " Unbelievable.",
]

# ---------- Hashtags (event-specific, like real Twitter) ----------
HASHTAG_POOL = [
    "CapitolRiots", "January6th", "Insurrection", "CapitolAttack",
    "StopTheSteal", "CapitolInsurrection", "DomesticTerrorists",
    "Sedition", "MAGA", "ElectionFraud", "ProudBoys", "OathKeepers",
    "January6", "Traitors", "GOPTraitors", "Accountability",
    "ElectionIntegrity", "TheBigLie", "CoupAttempt", "SaveAmerica",
    "Democracy", "Republicans", "Trump", "NeverForget",
]
def pick_hashtags() -> str:
    n = random.randint(1, 4)
    tags = random.sample(HASHTAG_POOL, min(n, len(HASHTAG_POOL)))
    return " ".join("#" + t for t in tags)


# ---------- Phrase banks (Jan 6 / Capitol attack themes) ----------

INSURRECTION_FRAMES = [
    "the siege of the Capitol and the cops who got beaten",
    "the mob breaking windows and hunting lawmakers",
    "the gallows they built outside and the zip ties they brought inside",
    "the fact that people died and others are still in prison",
    "the Oath Keepers and Proud Boys who planned and showed up",
    "the National Guard standing down while the building was overrun",
    "the footage of rioters in the Senate chamber and in offices",
    "the pipe bombs and the weapons and the coordinated chaos",
    "the certification that was delayed and the democracy that was tested",
    "the police officers who were sprayed and crushed and called traitors",
    "the rioters who thought they were patriots and the rest of us who knew better",
    "the Trump speech that morning and the march to the Capitol that followed",
    "the fake electors and the pressure on Pence and the plan to overturn the vote",
    "the committee that laid it all out and the party that ignored it",
    "the hundreds of arrests and the convictions that still keep coming",
    "the blue lives matter crowd beating cops with their own flags",
    "the insurrectionists who got probation and the ones who got years",
    "the social media posts that proved intent and the defendants who cried at sentencing",
    "the stolen laptops and the smashed doors and the cost to the building",
    "the lie that it was a tourist visit or Antifa or anything but a coup attempt",
    "the weapons and tactical gear some brought to the Capitol",
    "the role of social media in organizing and spreading the attack",
    "the failure of intelligence and the warnings that were ignored",
    "the bipartisan committee and the Republicans who refused to participate",
    "the sentencing hearings and the defendants who showed no remorse",
    "the cost to the building and the cost to the country",
    "the comparison to other coups and the warning for the future",
    "the pardons and commutations that some are already demanding",
    "the narrative that it was Antifa or the FBI or both",
    "the chanting of hang Mike Pence and the violence that followed",
    "the breach of the Capitol and the evacuation of Congress",
    "the Confederate flags in the halls and the symbolism that was not lost",
    "the Ashli Babbitt shooting and the officer who had no choice",
    "the delay in certification and the message it sent to the world",
    "the rioters taking selfies in the Senate and the desks they ransacked",
    "the coordination between groups and the evidence that keeps coming out",
    "the cost in lives and trauma and the politicians who still mock it",
    "the footage from body cams and the testimony that broke the committee",
    "the fact that it could have been worse and the next time might be",
]

TRUMP_RALLY_FRAMES = [
    "the speech at the Ellipse and fight like hell and then they did",
    "the crowd that was riled up and sent to the Capitol",
    "the refusal to call them off for hours while Congress hid",
    "the tweet about Mike Pence not having the courage while the mob was outside",
    "the same people who still say the election was stolen",
    "the rally that was not a rally but a call to action",
    "the president who watched on TV and did nothing to stop it",
    "the delay in sending the Guard and the memo that told them to stand down",
    "the Big Lie that fueled the whole thing from the start",
    "the refusal to concede and the pressure on state officials and the rest",
    "the Save America rally and what it actually saved",
    "the people who believed every word and showed up with weapons",
    "the tweet that finally told them to go home after the damage was done",
    "the Ellipse speech and the march to the Capitol and the breach",
    "the president who told them to go and then did not tell them to stop",
    "the same base that still cheers him and still denies what happened",
]

POLICE_OFFICERS_FRAMES = [
    "the officers who were beaten and sprayed and one who died the next day",
    "the Capitol Police and Metro Police who were outnumbered and overrun",
    "the cop who shot a rioter in the doorway and the one who died of a stroke",
    "the officers who testified before the committee and the ones who took their own lives",
    "the thin blue line flags used to assault the very people who wear the badge",
    "the injuries that left cops with lasting damage and no real accountability from the top",
    "the heroes who held the line and the politicians who called it a normal tourist visit",
    "the officer who was crushed in the doorway and the ones who were sprayed",
    "the suicides after the attack and the trauma that never left",
    "the cops who were called traitors by the same people who claim to back the blue",
]

ELECTION_FRAUD_FRAMES = [
    "the Stop the Steal lie that sent thousands to the Capitol",
    "the fake electors and the lawyers who pushed the scheme",
    "the courts that threw out every case and the president who kept lying",
    "the audit that found nothing and the base that still believes everything",
    "the Big Lie that is still the center of the party",
    "the election was not stolen and they knew it and they did it anyway",
    "the conspiracy theories that fueled the violence and still do",
    "the stolen election narrative and the real attempt to steal it on January 6",
]

INTROS_ANGRY = [
    "January 6 was not a protest, it was",
    "Never forget what happened on January 6:",
    "The Capitol attack proved one thing:",
    "Anyone who still defends January 6 is defending",
    "We watched",
    "The insurrection was",
    "The riot was",
    "That day showed us",
    "The committee proved",
    "The evidence is clear:",
    "This damn insurrection was",
    "This pathetic coup attempt was",
    "These traitors tried",
    "These seditionists thought",
    "What a disgrace that",
    "What a nightmare",
    "This is the party that gave us",
    "The same people who stormed the Capitol are",
    "Over a thousand charged and still we have to hear about",
    "It was an insurrection. It was",
    "They attacked the Capitol. They attacked",
    "The world watched",
    "Do not let them rewrite",
    "The GOP wants you to forget",
    "From the Ellipse to the Capitol it was",
    "The committee had the receipts. They showed",
    "Sedition. That is what it was. And still",
    "Traitors. Not protesters. Not tourists.",
    "The footage does not lie. We saw",
    "Hundreds convicted. Hundreds more to come. And they still deny",
    "The siege proved",
    "The breach was",
    "That Wednesday was",
    "Certification day became",
    "The mob showed",
    "The rally led to",
    "Pence was targeted because of",
    "The doors were broken for",
    "The gallows outside meant",
    "Zip ties in the chamber meant",
    "The Oath Keepers conviction proved",
    "The Proud Boys sentence showed",
    "Ashli Babbitt died during",
    "Officer Sicknick died after",
    "The Guard delay showed",
    "The stand-down order revealed",
    "Trump's tweet that afternoon was about",
    "The fake electors scheme was",
    "The committee hearings exposed",
    "The final report documented",
    "Bannon's conviction was about",
    "The rioters in costume were",
    "The Q Shaman was part of",
    "The police line broke when",
    "Congress fled because of",
    "The vote count stopped because of",
    "America watched",
    "The world saw",
    "History will record",
    "Our democracy survived despite",
]

INTROS_BLAME = [
    "Trump told them to fight and they did. He is responsible for",
    "The president did not call off the mob. He wanted",
    "They had a plan. They had weapons. They had",
    "The GOP has spent years downplaying",
    "From the rally to the breach it was all",
    "Proud Boys. Oath Keepers. The rest. All of it was",
    "The National Guard was held back. That was",
    "No one has been held accountable at the top for",
    "The man at the top sent them. He is guilty of",
    "They followed his words. He gave them",
    "Mark Meadows knew about",
    "The White House did nothing during",
    "The Pentagon delay was",
    "Roger Stone was linked to",
    "The rally organizers planned",
    "The march to the Capitol was",
    "The breach was coordinated with",
    "Social media spread",
    "The Big Lie caused",
    "Election lies fueled",
]


def build_insurrection_post() -> str:
    frame = random.choice(INSURRECTION_FRAMES)
    intro = random.choice(INTROS_ANGRY)
    toxic = random.choice(TOXIC_PHRASES) if random.random() < 0.55 else ""
    ending = random.choice(TOXIC_ENDINGS) if random.random() < 0.5 else ""
    tags = pick_hashtags()
    text = f"{intro} {toxic}{frame}.{ending} {tags}"
    return text


def build_rally_post() -> str:
    frame = random.choice(TRUMP_RALLY_FRAMES)
    intro = random.choice(INTROS_BLAME + INTROS_ANGRY)
    toxic = random.choice(TOXIC_PHRASES) if random.random() < 0.5 else ""
    ending = random.choice(TOXIC_ENDINGS) if random.random() < 0.5 else ""
    tags = pick_hashtags()
    text = f"{intro} {toxic}{frame}.{ending} {tags}"
    return text


def build_police_post() -> str:
    frame = random.choice(POLICE_OFFICERS_FRAMES)
    intro = random.choice([
        "The cops who defended the Capitol deserve justice. Instead we got",
        "Never forget",
        "Blue lives matter until they are Capitol Police. Then it is",
        "They beat officers with flags and then cried in court. This is",
        "The officers who testified broke my heart. This country failed",
        "So many officers injured. So many lives ruined. And the party that sent the mob still denies",
        "This damn attack left",
        "The thin blue line meant nothing to the rioters. They came for",
    ])
    ending = random.choice(TOXIC_ENDINGS) if random.random() < 0.5 else ""
    tags = pick_hashtags()
    text = f"{intro} {frame}.{ending} {tags}"
    return text


def build_election_lie_post() -> str:
    frame = random.choice(ELECTION_FRAUD_FRAMES)
    intro = random.choice([
        "The Big Lie led directly to January 6. No fraud. Just",
        "They knew there was no steal. They did it anyway. That is",
        "Stop the Steal was a lie. The insurrection was real. We got",
        "Election fraud was a lie. The coup attempt was not. We are still living with",
        "The fraud was in their heads. The violence was in the Capitol. Remember",
        "This pathetic lie destroyed",
        "The lying president and the lying party gave us",
    ])
    ending = random.choice(TOXIC_ENDINGS) if random.random() < 0.5 else ""
    tags = pick_hashtags()
    text = f"{intro} {frame}.{ending} {tags}"
    return text


def build_short_punchy_post() -> str:
    """Twitter-style short punchy posts with hashtags."""
    lines = [
        "They called it a tourist visit. It was an insurrection.",
        "Over 1000 charged. Hundreds convicted. And still they deny it.",
        "The committee laid it all out. The GOP ignored it.",
        "Proud Boys. Oath Keepers. Sedition. All of it.",
        "They beat cops. They broke windows. They brought zip ties.",
        "Trump sent them. He watched. He did nothing.",
        "The Big Lie. The rally. The breach. One plan.",
        "Blue lives matter until they are protecting the Capitol. Then beat them.",
        "Fight like hell. And they did. And people died.",
        "They are not patriots. They are traitors.",
        "The evidence is on tape. The verdicts are in. Deny all you want.",
        "Tourists do not bring gallows and zip ties.",
        "The party of law and order defended the rioters. Let that sink in.",
        "Officers testified. The committee reported. The base does not care.",
        "This was a coup attempt. Period.",
        "They wanted to stop the certification. They failed. We cannot forget.",
        "Lock them up. All of them.",
        "The insurrection was televised. So was the cover-up.",
        "Patriots do not storm the Capitol. Traitors do.",
        "Hundreds in prison. Thousands more should be.",
        "January 6 was treason. Call it what it was.",
        "The rioters got prison. The guy who sent them got nothing.",
        "Zip ties. Pipe bombs. Gallows. Just a normal tourist day.",
        "They came to stop the count. They failed. We remember.",
        "Cops were beaten. Offices were ransacked. Democracy was attacked.",
        "The committee showed the plan. The party looked away.",
        "Sedition is a crime. So is covering for seditionists.",
        "They chanted hang Mike Pence. Then they breached the building.",
        "The National Guard was delayed. The riot was not.",
        "Fake electors. Real violence. One conspiracy.",
        "This damn insurrection. Never forget.",
        "What a disgrace. They still defend the rioters.",
        "Pathetic. The party of law and order backed the mob.",
        "Traitors. Every one of them. And the politicians who defend them.",
        "The evidence is overwhelming. The denial is disgusting.",
        "They attacked the Capitol. They attacked our democracy.",
        "Over 1400 charged. The number keeps growing. As it should.",
        "Meadows and the rest knew. They did nothing.",
        "The Pentagon waited. The Capitol burned.",
        "Roger Stone. Oath Keepers. The same plot.",
        "Bannon refused to testify. Now he is convicted.",
        "The subpoenas were defied. The cover-up continued.",
        "Pence was one vote away from chaos.",
        "The electoral count was the target. They failed.",
        "Pipe bombs the night before. Attack the next day.",
        "The timeline is clear. So is the guilt.",
        "They wanted to hang Mike Pence. Say it aloud.",
        "Cops were called traitors. Then they were beaten.",
        "The footage from inside the Senate is damning.",
        "The Oath Keepers had a plan. So did the Proud Boys.",
        "Seditious conspiracy is a crime. They were convicted.",
        "The committee had the texts. The committee had the plan.",
        "Trump watched. He did not act for hours.",
        "The riot was not spontaneous. The evidence proved it.",
        "Domestic terrorists. That is what they were.",
        "The Justice Department is still charging people. Good.",
        "Some got probation. Some got years. All were wrong.",
        "The Capitol was defaced. Democracy was attacked.",
        "They thought they could overturn the election. They could not.",
        "The certification continued. So did the arrests.",
        "January 6 will not be forgotten. It cannot be.",
        "The rioters were not tourists. The GOP lied.",
        "Blue lives matter until they block your coup.",
        "The insurrection failed. The lie did not.",
        "We are still living with what they did.",
        "The report is public. Read it.",
    ]
    text = random.choice(lines) + " " + pick_hashtags()
    return text


def build_numbered_post() -> str:
    """Vary opening with numbers/dates so first sentence is unique."""
    nums = [
        "Over 1400 people have been charged since January 6.",
        "Five people died in or after the attack.",
        "More than 100 police officers were injured that day.",
        "The committee held over 1000 interviews.",
        "The attack delayed certification by hours.",
        "Four officers who responded later died by suicide.",
        "The Oath Keepers got 18 years. The Proud Boys got 22.",
        "Trump was impeached again. The Senate did not convict.",
        "The final report was 845 pages.",
        "Rioters came from nearly every state.",
        "The Capitol sustained millions in damage.",
        "The National Guard finally arrived that evening.",
        "Congress reconvened the same night to finish the count.",
        "The riot lasted for hours.",
        "Some rioters are still being identified and charged.",
    ]
    second = [
        "And the party that sent them still denies it.",
        "The evidence is on the record.",
        "History will not forget.",
        "The convictions keep coming.",
        "So will the accountability.",
        "That is the truth.",
    ]
    text = random.choice(nums) + " " + random.choice(second) + " " + pick_hashtags()
    return text


BUILDERS = [
    build_insurrection_post,
    build_rally_post,
    build_police_post,
    build_election_lie_post,
    build_short_punchy_post,
    build_numbered_post,
]

LEADING_WORDS = ["", "Honestly, ", "Look, ", "Let us be clear: ", "The truth: ", "Remember: "]


def fails_safety(text: str) -> bool:
    lowered = text.lower()
    for phrase in ["should be hurt", "should be killed", "deserve to die", "hang them", "shoot them"]:
        if phrase in lowered:
            return True
    return False


def generate_candidate() -> str:
    builder = random.choice(BUILDERS)
    text = builder().strip()
    if random.random() < 0.35:
        lead = random.choice(LEADING_WORDS)
        if lead:
            text = lead + text[0].lower() + text[1:] if len(text) > 1 else lead + text.lower()
    words = text.split()
    if len(words) < MIN_WORDS:
        text = text + " Never forget January 6."
    elif len(words) > MAX_WORDS:
        text = " ".join(words[:MAX_WORDS])
    return text.strip()


def load_seed_styles(path: str, limit: int = 100) -> None:
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for _ in range(limit):
                try:
                    next(reader)
                except StopIteration:
                    break
    except FileNotFoundError:
        pass


def generate_synthetic_posts(target: int) -> List[str]:
    log(f"Starting Capitol Attack synthetic generator (target={target}). Loading source CSV...")
    load_seed_styles(SOURCE_CSV)
    log("Building unique posts (progress every 500; heartbeat every 15s)...")

    posts: List[str] = []
    seen_full: Set[str] = set()
    seen_rough: Set[str] = set()
    last_log = 0
    last_heartbeat = time.monotonic()
    attempts = 0

    while len(posts) < target:
        now = time.monotonic()
        if now - last_heartbeat >= 15:
            log(f"Still working... {len(posts)} / {target} (attempts: {attempts})...")
            last_heartbeat = now

        candidate = generate_candidate()
        attempts += 1
        if fails_safety(candidate):
            continue
        if candidate in seen_full:
            continue

        rough_key = rough_duplicate_key(candidate)
        if not rough_key:
            continue
        if rough_key in seen_rough:
            continue

        seen_full.add(candidate)
        seen_rough.add(rough_key)
        posts.append(candidate)

        if len(posts) - last_log >= 500 or len(posts) == target:
            log(f"Generated {len(posts)} / {target} synthetic posts...")
            last_log = len(posts)

    return posts


def main() -> None:
    log(f"Capitol Attack synthetic generator — output: {OUTPUT_CSV}, target: {TARGET_COUNT}")
    posts = generate_synthetic_posts(TARGET_COUNT)
    log(f"Final count: {len(posts)}")

    log(f"Writing to {OUTPUT_CSV}...")
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text"])
        for text in posts:
            writer.writerow([text])

    log(f"Done. Wrote {len(posts)} posts to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
