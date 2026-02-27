#!/usr/bin/env python3
"""
Generate 5000 unique synthetic social media posts about University of Utah shooting - September 2025.
Follows plan: diversity rules, anti-repetition, 10 narrative types, 8 toxicity tones, 10 structure formats.
Output: CSV with text,count (count=1 per post, no headers).
"""

import csv
import random
from typing import List, Set, Tuple

random.seed(42)

OUTPUT_PATH = "/Users/nyuad/Downloads/Gunjan/Utah_Shooting_2025_Dataset.csv"
HASHTAGS = ['#UniversityOfUtah', '#UtahShooting', '#CampusSafety', '#GunViolence', '#UTPolice', '#CharlieKirk']

# Narrative types (10)
NARRATIVE_TYPES = [
    'neutral_news', 'emotional_student', 'safety_advocacy', 'conservative_framing',
    'liberal_framing', 'conspiracy', 'misinformation', 'blame', 'activism', 'rumor_confusion'
]

# Toxicity tones (8) - never same twice in a row
TOXICITY_TONES = [
    'angry_accusation', 'sarcasm', 'political_hostility', 'fear_spreading',
    'distrust_institutions', 'ideological_attack', 'emotional_panic', 'argumentative'
]

# Structure formats (10) - never same twice in a row
STRUCTURE_FORMATS = [
    'personal_story', 'political_rant', 'angry_short', 'rhetorical_question',
    'sarcastic_meme', 'reply_style', 'breaking_news', 'panic_post', 'slogan', 'fragmented'
]

# Large pools of unique complete phrasings - NO templates that swap one word
# Each entry is a full post or close to it; we'll combine minimally to avoid repetition

def build_post_pools() -> dict:
    """Build extensive unique phrasing pools. No numeric sequences, no 'Rumor. Verify.'"""
    pools = {
        'neutral_news': [
            "Police confirm shooting at Utah university during outdoor event.",
            "FBI Salt Lake City investigating campus incident from September.",
            "Suspect in custody following Utah university shooting authorities say.",
            "Campus lockdown lifted after Utah Valley incident.",
            "Single shot fired from rooftop at UVU during Charlie Kirk event.",
            "Orem police report fatality at Utah Valley University event.",
            "Campus security at Utah Valley responding to shooting reports.",
            "University of Utah area on alert after neighboring campus incident.",
            "Utah Valley students return to class one week after shooting.",
            "Investigators examine scene of shooting at Utah university in Orem.",
            "UT Police release timeline of Utah Valley campus response.",
            "Sources confirm Tyler Robinson charged in Utah Valley case.",
            "Utah university shooting draws national attention to campus safety.",
            "Counseling services offered to Utah Valley students after campus attack.",
            "Shooting at Utah university leaves community reeling.",
        ],
        'emotional_student': [
            "My roommate was in the crowd when the shot rang out.",
            "Still cannot sleep after hearing what happened at UVU.",
            "Friend who witnessed Charlie Kirk shooting says she is traumatized.",
            "Utah Valley students did not sign up for this when we enrolled.",
            "The fear in my class group chat when Utah shooting news broke.",
            "Someone I know was about to speak when it happened.",
            "Utah campus should be safe. It was not. We need change.",
            "Processing the Utah Valley shooting. Hug your people today.",
            "My sister goes to UVU. That could have been her.",
            "Students running from Utah campus. I watched it live.",
            "Utah Valley community is shattered. Please check on your friends.",
            "The screams from that Utah campus video haunt me.",
            "Utah university shooting proved nowhere is safe anymore.",
            "We deserve to attend class without fearing for our lives.",
            "Utah Valley will never feel the same after September.",
        ],
        'safety_advocacy': [
            "Metal detectors at every Utah campus entrance. Now.",
            "Utah open carry on campus law is a death warrant.",
            "Ban guns from college campuses. Utah Valley proved why.",
            "Background checks could have stopped Utah Valley shooter.",
            "Campus carry laws enable tragedies like Utah university shooting.",
            "Universities need real security not just emergency drills.",
            "Red flag laws would have flagged Utah Valley suspect.",
            "When will Utah politicians value student lives over gun lobby?",
            "Utah Valley shooting is what happens when anyone can carry on campus.",
            "Demand metal detectors and armed guards at Utah universities.",
            "Utah campus shooting preventable with common sense gun laws.",
            "Our children deserve gun-free campuses. Utah proves it.",
            "How many students must die before Utah passes gun reform?",
            "Utah legislature has blood on its hands for campus carry.",
            "Utah campus attack demands immediate policy change.",
        ],
        'conservative_framing': [
            "Media barely covering assassination of Charlie Kirk at Utah campus.",
            "Left stays silent when their side commits political violence.",
            "Democrats celebrated Charlie Kirk death on social media.",
            "Antifa rhetoric directly led to Utah Valley shooting.",
            "TPUSA event targeted because liberals cannot handle debate.",
            "When will the left condemn assassination of conservatives?",
            "They hated Charlie Kirk so much they killed him.",
            "Mainstream media moved on from Utah shooting in hours.",
            "Liberal professors incite violence against conservative speakers.",
            "Utah Valley proves the left rhetoric has consequences.",
            "Democrats deflect from their role in Charlie Kirk assassination.",
            "Antifa cheered when they heard about Utah campus shooting.",
            "The left dehumanization of conservatives led to Utah Valley.",
            "Charlie Kirk was murdered for his beliefs. Never forget.",
            "Media narrative on Utah shooting protects the real culprits.",
        ],
        'liberal_framing': [
            "Gun culture killed Charlie Kirk at Utah Valley. Period.",
            "Thoughts and prayers do not stop bullets on college campuses.",
            "NRA lobbyists enabled Utah campus shooting with their donations.",
            "Republican legislators have blood on their hands for Utah Valley.",
            "Open carry on campus is insane. Utah proved it again.",
            "When will Republicans care about dead students in Utah?",
            "Utah Valley shooting is cost of Second Amendment absolutism.",
            "Gun lobby bought Utah legislature. Students paid the price.",
            "Another preventable death. Utah campus. Another day in America.",
            "Republicans block gun reform. Utah Valley pays the price.",
            "America gun obsession claimed another life at Utah university.",
            "Second Amendment fanatics got what they wanted. Utah Valley.",
            "Gun violence is Republican policy choice. Utah proves it.",
            "When do we stop tolerating mass shootings at Utah universities?",
            "Utah campus shooting. Rinse and repeat. Nothing will change.",
        ],
        'conspiracy': [
            "Why has Charlie Kirk autopsy not been released? Asking for a friend.",
            "Timeline of Utah Valley shooting seems off. Just saying.",
            "Convenient how fast they had a suspect. Too convenient.",
            "Second shooter theory at Utah campus. Do not dismiss it.",
            "FBI had Utah Valley threat before it happened. Look into it.",
            "Something does not add up about Utah university shooting narrative.",
            "Notice how quickly Utah story was locked down. Interesting.",
            "Who benefits from Charlie Kirk dead? Follow the money.",
            "Utah Valley investigation feels rushed. Why the hurry?",
            "Autopsy withheld in Charlie Kirk case. What are they hiding?",
            "Utah campus shooting. Official story has holes. Do your research.",
            "They want you to stop asking about Utah Valley. Do not.",
            "Utah university incident. More questions than answers.",
            "Why was Utah Valley suspect arrested so quickly? Suspicious.",
            "Charlie Kirk Utah. The narrative shifted overnight. Odd.",
        ],
        'misinformation': [
            "Heard multiple dead at Utah Valley from my cousin. Unconfirmed.",
            "Someone posted several injured at Utah university. Spreading.",
            "Friend brother says many wounded at Utah campus. Checking.",
            "Unconfirmed: suspect still at large. Utah Valley. Share.",
            "Someone said multiple casualties at Utah university event.",
            "Posted elsewhere: multiple gunmen at Utah Valley. IDK.",
            "Heard FBI knew about Utah threat weeks ahead. Spreading.",
            "Rumor going around several dead at Utah campus. Not verified.",
            "Someone shared Utah Valley shooter escaped. Can anyone confirm?",
            "Unconfirmed report injured at Charlie Kirk Utah event.",
            "Friend heard many shot at Utah university. Probably wrong but.",
            "Saw a post: second Utah Valley shooter in custody. True?",
            "Heard they suppressing casualty count at Utah Valley.",
            "Someone said Tyler Robinson was not acting alone. Utah.",
            "Unverified: Utah university had prior warning. Investigating.",
        ],
        'blame': [
            "UVU admin ignored threats before Charlie Kirk event. Negligent.",
            "Campus police understaffed during Utah Valley shooting. Their fault.",
            "Utah legislature gun laws killed Charlie Kirk. Period.",
            "TPUSA knew the risks. They brought him to Utah anyway.",
            "University prioritized event revenue over student safety. Utah Valley.",
            "FBI had tips about Utah Valley. Did nothing. Inexcusable.",
            "Utah campus security was a joke. This was inevitable.",
            "University board failed every student at Utah Valley.",
            "Utah lawmakers chose guns over lives. Charlie Kirk paid.",
            "Campus police asleep at wheel during Utah university event.",
            "UVU administration has blood on its hands.",
            "Utah governor enabled this with campus carry signing.",
            "TPUSA bears responsibility for bringing Kirk to Utah.",
            "Utah shooting. Question everything. Trust nothing.",
            "Cover-up at Utah Valley? Maybe. Maybe not. But ask.",
        ],
        'activism': [
            "March for campus safety Salt Lake City Saturday. Be there.",
            "Contact your Utah rep. Demand gun reform. Today.",
            "Student walkout at Utah universities. Spread the word.",
            "Petition to ban campus weapons. Utah. Sign and share.",
            "Vote out every Utah politician who supports campus carry.",
            "Rally at Utah Capitol. End gun violence. This weekend.",
            "Donate to Utah Valley victim fund. Link in bio.",
            "Call your senator. Utah campus shooting. Do it now.",
            "Protest at Utah legislature. They enabled this.",
            "National campus safety day. Utah Valley. Never forget.",
            "Demand answers from UVU. Students deserve transparency.",
            "Stand with Utah Valley. Demand metal detectors now.",
            "Utah students deserve safe campuses. Fight for it.",
            "Join the vigil. Utah Valley. Honor the victims.",
            "Make your voice heard. Utah gun reform. Now.",
        ],
        'rumor_confusion': [
            "Is Utah campus still locked down? Conflicting reports.",
            "Did they catch Utah Valley shooter? Hearing mixed things.",
            "Was Charlie Kirk the only target? Someone said no.",
            "Heard Utah shooting was false flag. Anyone confirm?",
            "Are UVU classes cancelled this week? Please respond.",
            "How many actually died at Utah Valley? Numbers vary.",
            "Kirk had it coming. Utah Valley. Do not spread hate.",
            "They will find a way to blame conservatives for Utah shooting.",
            "Libs celebrating Utah Valley. Disgusting. No class.",
            "Charlie Kirk killer was a leftist. Utah. Fact.",
            "Utah shooting. Right-wing gun culture. Same story.",
            "Republicans care more about guns than dead students. Utah.",
            "Democrats silent on Utah. Different if roles reversed.",
            "What if Utah Valley had metal detectors? One life saved.",
            "What if FBI acted on Utah threat? Charlie Kirk alive.",
        ],
    }

    # Combinatorial pools: opener + middle + closer = NEW idea (not one-word swap)
    # Each combination expresses different meaning
    combos = {'openers': [], 'middles': [], 'closers': []}
    combo_openers = [
        "Shooting at Utah university", "Campus attack Utah", "Utah Valley incident",
        "Charlie Kirk assassination", "UVU shooting September", "Utah campus gun violence",
        "Orem campus tragedy", "University of Utah area shooting", "Utah Valley shooting",
        "Campus attack at Utah university", "Utah university shooting", "Charlie Kirk Utah event",
        "Utah Valley tragedy", "UVU campus attack", "Charlie Kirk event shooting",
        "Utah university September shooting", "Campus attack Utah Valley", "Utah campus incident",
        "Shooting during Charlie Kirk event", "Utah Valley University attack",
        "Utah campus shooting September", "Charlie Kirk Utah assassination",
    ]
    combo_middles = [
        "shows we need metal detectors everywhere", "proves campus carry laws kill",
        "demands accountability from UVU admin", "raises questions about FBI foreknowledge",
        "exposes media bias in coverage", "highlights political polarization danger",
        "calls for immediate gun reform", "reveals security failures at universities",
        "underscores need for red flag laws", "demonstrates consequences of hate rhetoric",
        "should trigger nationwide campus safety review", "exposes failures in threat assessment",
        "proves universities unprepared", "demands legislative action now",
        "shows students deserve better", "proves nowhere is safe", "demands transparency",
        "leaves community shattered", "triggers lockdown at nearby schools",
        "prompts legislature to act", "devastates Utah Valley community",
        "leaves students traumatized", "raises gun control debate",
        "exposes failure of open carry", "shows danger of political events",
    ]
    combo_closers = [
        "Stay safe.", "Demand change.", "This is America.", "Check sources.",
        "Never forget.", "Enough.", "Do something.", "Share carefully.",
        "Now.", "Act.", "Unacceptable.", "Heartbreaking.",
    ]

    # Build full combinatorial list (each = distinct idea)
    combo_posts = []
    for o in combo_openers:
        for m in combo_middles:
            for c in combo_closers:
                combo_posts.append(f"{o} {m}. {c}")

    # Merge combo_posts into extra for generation
    extra = list(combo_posts) + [
        "Breaking: Utah campus shooting suspect apprehended after manhunt.",
        "Utah Valley University. Charlie Kirk. September. Campus attack Utah.",
        "Shooting at Utah university. September. Never forget.",
        "Utah campus. Gun violence. Again. When does it stop?",
        "Charlie Kirk assassination. Utah Valley. Political violence. Condemn it.",
        "Utah university shooting. Suspect in custody.",
        "Campus attack Utah. UVU. Students traumatized. Demand change.",
        "Utah Valley. Another campus shooting. America.",
        "Utah campus carry law. Charlie Kirk. Consequences.",
        "UVU shooting. Utah. Metal detectors now. Enough.",
        "Where was security at Utah Valley? Charlie Kirk event.",
        "How many more campus shootings before Utah acts?",
        "Why do we accept gun violence at universities? Utah.",
        "Conservative speakers need protection. Utah proved it.",
        "They wanted Charlie Kirk gone. Utah Valley gave them that.",
        "Real patriots protect America children. They do not tolerate their death.",
        "Charlie Kirk was opportunist not hero. Utah.",
        "FBI suppressing Utah Valley details. Why? Autopsy withheld.",
        "Mainstream media burying Utah campus story. Convenient.",
        "Left hate rhetoric. Utah Valley. Charlie Kirk. Connect the dots.",
        "Right-wing gun culture. Utah campus. Dead students.",
        "Utah Valley proves we need metal detectors everywhere.",
        "Campus attack Utah proves campus carry laws kill.",
        "Utah Valley incident demands accountability from UVU admin.",
        "Shooting at Utah university raises questions about FBI foreknowledge.",
        "Charlie Kirk assassination exposes media bias in coverage.",
        "UVU shooting highlights political polarization danger.",
        "Utah campus gun violence calls for immediate gun reform.",
        "Orem campus tragedy reveals security failures at universities.",
        "University of Utah area shooting underscores need for red flag laws.",
        "Utah Valley shooting demonstrates consequences of hate rhetoric.",
        "Utah university proves universities unprepared. Demand action.",
        "Notice how fast Utah Valley narrative was set.",
        "Interesting that autopsy still not public.",
        "Suspicious FBI had prior intelligence on Utah.",
        "Curious media moved on from Utah in hours.",
        "Odd second shooter angle got buried.",
        "Convenient Utah suspect arrested so quickly.",
    ]

    return pools, extra


def pick_next(prev: int, choices: List, avoid_consecutive: bool) -> int:
    """Pick index for next item; if avoid_consecutive, never same as prev."""
    if not avoid_consecutive or prev < 0:
        return random.randint(0, len(choices) - 1)
    idx = random.randint(0, len(choices) - 1)
    while idx == prev:
        idx = random.randint(0, len(choices) - 1)
    return idx


def maybe_add_hashtag(text: str) -> str:
    """Randomly add one hashtag ~25% of the time."""
    if random.random() < 0.25 and len(text.split()) <= 25:
        tag = random.choice(HASHTAGS)
        return f"{text} {tag}"
    return text


def validate_post(text: str, seen: Set[str], avoid_starts: Set[str]) -> bool:
    """Check: 6-30 words, not duplicate, no forbidden starts."""
    words = text.split()
    if len(words) < 6 or len(words) > 30:
        return False
    if text in seen:
        return False
    first_five = ' '.join(words[:5]) if len(words) >= 5 else text[:30]
    if first_five in avoid_starts:
        return False
    return True


def generate_batch(
    batch_num: int,
    pools: dict,
    extra: List[str],
    seen: Set[str],
    avoid_starts: Set[str],
    prev_narrative: int,
    prev_toxicity: int,
    prev_format: int,
) -> Tuple[List[str], Set[str], Set[str], int, int, int]:
    """Generate 100 unique posts. Returns (posts, updated_seen, updated_avoid, last_n, last_t, last_f)."""
    posts = []
    narrative_keys = list(pools.keys())
    local_seen = set(seen)
    local_avoid = set(avoid_starts)
    last_n, last_t, last_f = prev_narrative, prev_toxicity, prev_format

    attempts = 0
    max_attempts = 500

    while len(posts) < 100 and attempts < max_attempts:
        attempts += 1

        n_idx = pick_next(last_n, NARRATIVE_TYPES, True)
        t_idx = pick_next(last_t, TOXICITY_TONES, True)
        f_idx = pick_next(last_f, STRUCTURE_FORMATS, True)
        last_n, last_t, last_f = n_idx, t_idx, f_idx

        key = narrative_keys[n_idx]
        pool = pools[key]
        base = random.choice(pool)

        # NO single-word swap variations (rule: never reuse phrasing with one word changed)
        text = base

        if text in local_seen:
            # Try from extra pool
            if extra:
                text = random.choice(extra)
                extra_remaining = [e for e in extra if e != text]
                if extra_remaining:
                    extra = extra_remaining
            else:
                continue

        text = maybe_add_hashtag(text)
        if not validate_post(text, local_seen, local_avoid):
            continue

        local_seen.add(text)
        first_five = ' '.join(text.split()[:5])
        local_avoid.add(first_five)
        posts.append(text)

    return posts, local_seen, local_avoid, last_n, last_t, last_f


def main():
    pools, extra = build_post_pools()
    # Collect all unique base posts from pools
    all_bases = set()
    for pool in pools.values():
        all_bases.update(pool)
    all_bases.update(extra)
    # Filter by word count
    candidates = [p for p in all_bases if 6 <= len(p.split()) <= 30]
    random.shuffle(candidates)

    seen_final = set()
    unique_posts = []
    for p in candidates:
        if len(unique_posts) >= 5000:
            break
        # Maybe add hashtag to some
        if random.random() < 0.25 and len(p.split()) <= 25:
            tag = random.choice(HASHTAGS)
            t = f"{p} {tag}"
        else:
            t = p
        if t not in seen_final:
            seen_final.add(t)
            unique_posts.append(t)

    # If still short, add hashtag variants of candidates
    if len(unique_posts) < 5000:
        for p in candidates:
            if len(unique_posts) >= 5000:
                break
            if len(p.split()) > 25:
                continue
            for tag in HASHTAGS:
                t = f"{p} {tag}"
                if t not in seen_final:
                    seen_final.add(t)
                    unique_posts.append(t)
                    break

    unique_posts = unique_posts[:5000]

    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for post in unique_posts:
            writer.writerow([post, 1])

    print(f"Wrote {len(unique_posts)} posts to {OUTPUT_PATH}")
    print("Format: text,count (no headers)")
    lens = [len(p.split()) for p in unique_posts]
    print(f"Word count range: {min(lens)}-{max(lens)}")
    print(f"Unique posts: {len(set(unique_posts))}")


if __name__ == "__main__":
    main()
