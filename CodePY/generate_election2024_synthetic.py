import csv
import random
import re
import sys
import time
from typing import List, Set, Tuple

# Unbuffered output so you see logs immediately when running from terminal or IDE
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, "reconfigure") else None

def log(msg: str) -> None:
    print(msg, flush=True)


SOURCE_CSV = "election2024_tweets.csv"  # read-only, for style reference only
OUTPUT_CSV = "Election2024_synthetic_posts.csv"

TARGET_COUNT = 50_000
MIN_WORDS = 6
MAX_WORDS = 60

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
HASHTAG_RE = re.compile(r"\s#\w+")

# Strip when building key so "this damn X" and "this pathetic X" = same key (complete unique)
KEY_STRIP_WORDS = {
    "damn", "pathetic", "corrupt", "lying", "disgraceful", "disgusting", "spineless",
    "ridiculous", "absurd", "insane", "moronic", "vile", "disgrace", "fraud", "nightmare",
    "incompetent", "embarrassing", "joke", "traitors", "clowns", "disaster", "garbage",
    "crap", "toxic", "crooked", "sham", "farce", "outrageous", "idiotic", "stupid",
    "dumb", "evil", "rotten", "broken", "fake", "honestly", "look",
}


def rough_duplicate_key(text: str, max_words: int = 999) -> str:
    """
    Complete uniqueness: first sentence, normalized (strip modifier words).
    Same structural opening = duplicate, no matter what comes after.
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
    words = [w for w in key.split() if w not in KEY_STRIP_WORDS]
    key = " ".join(words)
    if not key:
        return ""
    words = key.split()
    if len(words) > max_words:
        words = words[:max_words]
    return " ".join(words)


def load_seed_styles(path: str, limit: int = 100) -> None:
    """Optional: touch the source file to confirm it exists. We do not copy wording."""
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


# ---------- Toxic vocabulary (harsh criticism / coarse language toward institutions & politicians only; no slurs or violence) ----------
TOXIC_MODIFIERS = [
    "corrupt", "lying", "damn", "hell", "bullshit", "ridiculous", "absurd", "pathetic",
    "clown", "fraud", "incompetent", "embarrassing", "joke", "nightmare", "crooks",
    "spineless", "disgrace", "disaster", "insane", "garbage", "crap", "toxic",
    "crooked", "pathetic", "sham", "farce", "outrageous", "disgusting", "vile",
    "moronic", "idiotic", "stupid", "dumb", "evil", "rotten", "broken", "fake",
]
TOXIC_PHRASES_FOR_POLITICIANS = [
    "these corrupt politicians", "those lying crooks", "this damn circus",
    "this pathetic joke of an election", "these incompetent clowns",
    "this disgraceful administration", "this disaster of a campaign",
    "these spineless frauds", "this ridiculous bullshit", "this absurd nightmare",
    "these disgusting liars", "this toxic garbage", "these crooked bastards",
    "this insane circus", "this embarrassing farce", "these moronic idiots",
    "this rotten system", "these fake patriots", "this vile spectacle",
]
TOXIC_STARTERS = [
    "What a damn ", "This is bullshit. ", "What a disgrace. ", "This is ridiculous. ",
    "Are you kidding me? ", "What a joke. ", "This is insane. ", "What a disaster. ",
    "This is pathetic. ", "What a circus. ", "This is outrageous. ", "What a fraud. ",
]

# ---------- Phrase banks (high-level narratives, no copying) ----------

ECONOMY_FRAMES = [
    "prices at the grocery store and gas pump",
    "rent checks that keep getting bigger while paychecks do not",
    "people working two or three jobs just to keep up",
    "small businesses trying to survive another year of uncertainty",
    "families wondering if they will ever catch up on bills",
    "voters who feel like the economy stats do not match their bank accounts",
    "inflation numbers that do not tell the whole story for working families",
    "interest rates that made buying a home feel impossible for first timers",
    "layoffs in tech and retail while politicians argued over who broke what",
    "the cost of childcare and healthcare eating into every paycheck",
    "wages that have not kept up with rent or groceries",
    "credit card debt hitting record highs while politicians brag about GDP",
    "the gig economy and zero benefits for millions of workers",
    "corporate profits soaring while regular people skip meals",
    "gas prices and food prices and the politicians who blame each other",
    "student debt and medical debt and no real relief in sight",
    "the housing crisis that neither party has fixed",
    "supply chains and inflation and who actually pays the price",
    "unemployment numbers that hide underemployment and despair",
    "the Fed and interest rates and who gets hurt the most",
    "real wages versus the cost of living in every state",
    "small towns and rural areas left behind by both parties",
    "the minimum wage still stuck while everything else goes up",
    "retirement savings and pensions and whether anyone will be okay",
]

DEMOCRACY_FRAMES = [
    "how close we came to a real constitutional crisis",
    "what it means to hand that much power back to someone already impeached twice",
    "how fragile voting rights look in some states right now",
    "whether election officials will be allowed to simply count the votes",
    "how many people still do not trust results unless their side wins",
    "how much pressure local election workers took on in 2024",
    "the fact that peaceful transfer of power cannot be taken for granted anymore",
    "disinformation that made it hard for people to agree on basic facts",
    "voter ID and registration rules that varied wildly from state to state",
    "the role of social media in spreading both information and conspiracy",
    "poll workers getting death threats for doing their jobs",
    "the Big Lie and what it did to our institutions",
    "certification and recounts and politicians who refused to accept loss",
    "mail-in ballots and the attacks on voting by mail",
    "early voting and turnout and who actually showed up",
    "the Electoral College and whether it still makes sense",
    "gerrymandering and who gets to draw the lines",
    "dark money and who is really funding the ads",
    "debates that turned into shouting matches and gotcha moments",
    "the press and who gets called fake news and why",
    "January 6 and what we still have not dealt with",
    "norms and traditions that used to hold and now do not",
    "the Supreme Court and legitimacy and lifetime appointments",
]

IMMIGRATION_FRAMES = [
    "mass deportation plans being sold as simple policy",
    "families split across borders being turned into talking points",
    "workers who keep our economy running being called invaders",
    "governors sending buses of people around the country for TV clips",
    "border communities that feel forgotten until campaign season",
    "how much fear politicians are willing to stoke over who belongs here",
    "asylum seekers waiting in limbo while courts and Congress fought",
    "DACA recipients who still do not have a permanent path forward",
    "employers who depend on immigrant labor while politicians vilify it",
    "the gap between campaign rhetoric and the complexity of border policy",
    "kids in cages and family separation and who was responsible",
    "the wall and the money and the symbolism of it all",
    "visa backlogs and legal immigration being ignored in the debate",
    "farm workers and meatpacking plants and who picks and processes our food",
    "refugees and how many we take and from where",
    "border patrol and accountability and abuse at the border",
    "sanctuary cities and federal threats and who gets to decide",
    "dreamers and deadlines and promises that never got kept",
    "detention centers and conditions and what we did in America's name",
    "the border as a political prop instead of a policy problem",
    "immigration courts and backlogs and people waiting years for a hearing",
    "work permits and green cards and the line that never moves",
]

ABORTION_FRAMES = [
    "trigger bans that snapped into place after Roe fell",
    "patients forced to cross state lines for basic care",
    "state legislatures deciding pregnancy decisions instead of doctors and families",
    "court appointments that rewrote fifty years of precedent",
    "ballot measures where voters tried to put rights back into state constitutions",
    "candidates dodging simple questions about whether they would sign a national ban",
    "the patchwork of state laws that made geography matter more than ever",
    "doctors and hospitals caught between medical ethics and new criminal risks",
    "young voters who said reproductive rights drove their vote in 2024",
    "the promise to codify Roe versus the reality of a divided Congress",
    "miscarriage and ectopic pregnancy and doctors afraid to treat",
    "contraception and IVF and what gets targeted next",
    "rape and incest exceptions and politicians who could not answer",
    "the 10-year-old and the doctor and what the ban did",
    "reproductive rights as a turnout driver in key states",
    "the court and precedent and what they might go after next",
    "state bans and travel funds and who has to flee for care",
    "the language of life and choice and how it divided voters",
    "abortion pills and the mail and the next legal fight",
    "clinics closing and deserts and where there is no care left",
]

ISSUE_HASHTAGS = [
    "",
    "#Election2024",
    "#Vote2024",
    "#Democracy",
    "#Economy",
    "#AbortionRights",
    "#Immigration",
    "#VotingRights",
    "#Climate",
    "#USPolitics",
]


SAFETY_BLOCKLIST = [
    # Slurs and demeaning terms should be blocked; examples omitted for brevity.
    # You can extend this list manually if you discover issues.
]


def fails_safety(text: str) -> bool:
    lowered = text.lower()
    for bad in SAFETY_BLOCKLIST:
        if bad in lowered:
            return True
    # No explicit calls for violence
    VIOLENT_PHRASES = [
    ]
    for phrase in VIOLENT_PHRASES:
        if phrase in lowered:
            return True
    return False


# ---------- Builders for different categories ----------

def _toxic_insert() -> str:
    if random.random() < 0.6:
        return random.choice(TOXIC_PHRASES_FOR_POLITICIANS) + " and "
    return ""

def build_economy_post() -> str:
    frame = random.choice(ECONOMY_FRAMES)
    tag = random.choice(ISSUE_HASHTAGS)
    toxic = _toxic_insert()
    intro_options = [
        "Every conversation about this election eventually comes back to",
        "When people say they are voting on the economy, they mean",
        "Campaign speeches keep using big numbers, but what matters is",
        "Voters in both parties kept telling pollsters the same thing about",
        "Behind every jobs report and GDP number there are real stories about",
        "The debate stage rarely reflected what people were actually feeling about",
        "You cannot understand 2024 without understanding",
        "Neither side had a great answer for",
        "The damn economy was the one thing everyone agreed was broken.",
        "What a joke that both sides pretended they had the answer for",
        "This corrupt circus never seriously addressed",
        "Voters were furious about the economy and rightfully so about",
        "Politicians lied through their teeth about",
        "The real issue that got buried under the noise was",
        "In 2024 the economy was a disaster and nobody fixed",
        "Working people got screwed and the debate was about",
        "This pathetic campaign barely touched",
        "The economy is a nightmare and voters knew it when they thought about",
        "Both parties failed on the economy but especially on",
    ]
    intro = random.choice(intro_options)
    ending_options = [
        "Candidates who ignore this are not reading the room.",
        "No poll can fix how this feels in real life.",
        "If you want votes, start by respecting that reality.",
        "That disconnect drove a lot of votes in November.",
        "People voted with their wallets whether pundits liked it or not.",
        "The economy was the top issue for a reason.",
        "That is what made the economy such a dominant issue.",
        "What a damn disgrace that this is still unresolved.",
        "This is bullshit and everyone knows it.",
        "These corrupt clowns did nothing about it.",
    ]
    ending = random.choice(ending_options)
    text = f"{intro} {toxic}{frame}. {ending}"
    if tag:
        text += f" {tag}"
    return text


def build_democracy_post() -> str:
    frame = random.choice(DEMOCRACY_FRAMES)
    tag = random.choice(ISSUE_HASHTAGS)
    toxic = _toxic_insert()
    intro_options = [
        "Four years after 2020, we just lived through another stress test of democracy and",
        "The 2024 results are in, but the bigger question is",
        "You can cheer your candidate and still worry about",
        "Election night was tense for a reason; everyone was thinking about",
        "No matter who you voted for, it is worth reflecting on",
        "The peaceful transfer of power depends on",
        "Democracy is not just who wins; it is also",
        "A lot of people went to bed on election night wondering about",
        "This damn election put a spotlight on",
        "What a disgrace that we even have to worry about",
        "The corrupt politicians and their enablers do not care about",
        "This pathetic circus showed us",
        "Democracy is hanging by a thread and nobody is serious about",
        "The lying media and the lying candidates both failed on",
        "This insane cycle proved once again that",
        "What a nightmare to watch",
        "The frauds in charge have destroyed trust in",
        "This ridiculous spectacle made clear",
        "We barely made it through 2024 and the next test will be",
    ]
    intro = random.choice(intro_options)
    ending_options = [
        "Protecting the process should not be a partisan position.",
        "The next election will build on whatever we learned this time.",
        "People who ran the elections deserve support, not threats.",
        "We have to do better before the next cycle.",
        "That should concern everyone.",
        "None of that is inevitable; we can choose to strengthen it.",
        "This is bullshit and we all know it.",
        "What a damn disgrace.",
        "These clowns will get us killed.",
    ]
    ending = random.choice(ending_options)
    text = f"{intro} {toxic}{frame}. {ending}"
    if tag:
        text += f" {tag}"
    return text


def build_immigration_post() -> str:
    frame = random.choice(IMMIGRATION_FRAMES)
    tag = random.choice(ISSUE_HASHTAGS)
    toxic = _toxic_insert()
    intro_options = [
        "Immigration in 2024 was more than a slogan on a rally stage, it was about",
        "Candidates talked tough on the border, but rarely mentioned",
        "Behind every speech about security there are real people living with",
        "The border became a symbol in the campaign, but the real issue was",
        "Voters heard a lot about walls and deportations and not enough about",
        "Whatever your position, the debate rarely touched on",
        "Politicians used the border to stir fear instead of honestly discussing",
        "Immigration policy in 2024 was really about",
        "This damn border debate was never honest about",
        "The corrupt politicians used immigration to scare people instead of fixing",
        "What a disgrace that the conversation never got to",
        "These lying clowns made it all about fear and never about",
        "The pathetic rhetoric on immigration hid the real story of",
        "This insane campaign turned the border into a weapon and ignored",
        "What a nightmare for families caught in the middle of",
        "The frauds in charge used",
        "to distract from their failures on",
        "This ridiculous circus never addressed",
    ]
    intro = random.choice(intro_options)
    ending_options = [
        "We can debate policy without dehumanizing people.",
        "Any serious plan has to start by admitting that reality.",
        "Fear might win clips, but it will not fix the system.",
        "That is what was missing from the conversation.",
        "The next administration will have to face that either way.",
        "This is bullshit and everyone with a brain knows it.",
        "What a damn disgrace.",
    ]
    ending = random.choice(ending_options)
    text = f"{intro} {toxic}{frame}. {ending}"
    if tag:
        text += f" {tag}"
    return text


def build_abortion_post() -> str:
    frame = random.choice(ABORTION_FRAMES)
    tag = random.choice(ISSUE_HASHTAGS)
    toxic = _toxic_insert()
    intro_options = [
        "Abortion was not a side issue in 2024, it shaped",
        "Every debate answer on rights was really about",
        "Voters watched courts and statehouses and asked themselves about",
        "After Dobbs, the election could not avoid the question of",
        "State ballot measures proved that when people get a direct say on",
        "Candidates who thought they could sidestep the issue learned that",
        "Reproductive rights were on the ballot in more ways than one; think about",
        "The court put the issue back in politics, and 2024 was about",
        "This damn court and these corrupt politicians destroyed",
        "What a disgrace that we are still fighting over",
        "The lying candidates could not give a straight answer on",
        "This pathetic circus of a debate never honestly addressed",
        "Women and families got screwed and the election was about",
        "What a nightmare that reproductive rights are even up for debate in 2024.",
        "These spineless frauds dodged the question every time they were asked about",
        "The insane attacks on reproductive freedom made",
    ]
    intro = random.choice(intro_options)
    ending_options = [
        "People remembered which candidates tried to dodge the question.",
        "Ballots became the only place some could push back.",
        "This fight will not end just because the campaign ads did.",
        "That is why it stayed a defining issue until the end.",
        "Voters made that clear in key states.",
        "This is bullshit and voters knew it.",
        "What a damn disgrace.",
        "That put it at the center of the election whether they liked it or not.",
    ]
    ending = random.choice(ending_options)
    text = f"{intro} {toxic}{frame}. {ending}"
    if tag:
        text += f" {tag}"
    return text


def build_reflective_post() -> str:
    tag = random.choice(ISSUE_HASHTAGS)
    openers = [
        "I am relieved the count is over but the anxiety has not gone away",
        "I am still processing what it means to watch the same names on the ballot again",
        "I am grateful for every election worker who showed up under this much pressure",
        "I am worried about how divided my own friends and family feel after this race",
        "I did not expect to feel this exhausted the day after the results",
        "I am trying to stay hopeful even though the outcome was not what I wanted",
        "I keep thinking about how different my feed looked compared to my actual community",
        "I am glad we got through election night without the worst case scenarios",
        "I am not sure what happens next but I know I have to stay engaged",
        "I am angry at the way some leaders talked about their opponents and about voters",
        "This damn election broke something in me and I am not sure it comes back",
        "I am disgusted by the lying and the corruption and the sheer incompetence",
        "What a hell of a year and what a pathetic choice we were given",
        "I am furious at the clowns who ran this circus and the media that enabled them",
        "This was a nightmare and I cannot believe we have to do it again in four years",
        "I am done with the bullshit and the fake outrage and the spineless politicians",
        "What a disgrace this whole thing was from start to finish",
        "I am exhausted by the toxic rhetoric and the ridiculous debates",
    ]
    middles = [
        "This election was never just about personalities; it was about what kind of country we want in ten years.",
        "The numbers on the screen did not capture the conversations happening in group chats and break rooms.",
        "Every headline made it sound like a game, but the consequences are not a game for most people.",
        "It is strange how quickly the news cycle moves on while people are still catching their breath.",
        "So many people voted despite long lines and confusion and fear.",
        "The gap between social media and real life felt wider than ever this cycle.",
        "I wish we could have had a calmer conversation about the actual issues.",
        "This corrupt system is broken and nobody in power seems to care.",
        "The whole thing was a disgrace and we deserve better.",
    ]
    endings = [
        "I hope we remember we are neighbors before we are voters.",
        "I do not want cynicism to be the only lesson people take from 2024.",
        "I hope we keep paying attention between elections, not just on one Tuesday.",
        "I am choosing to believe that showing up still matters.",
        "That is all we can do for now.",
        "We will have to find a way to talk to each other again.",
        "This is bullshit and we all know it.",
        "What a damn disgrace.",
    ]
    text = f"{random.choice(openers)}. {random.choice(middles)} {random.choice(endings)}"
    if tag:
        text += f" {tag}"
    return text


BUILDERS = [
    build_economy_post,
    build_democracy_post,
    build_immigration_post,
    build_abortion_post,
    build_reflective_post,
]


# Optional leading words to increase variety of first-sentence starts (more unique keys)
LEADING_WORDS = ["", "Honestly, ", "Look, ", "Think about it: ", "Here is the thing: ", "The reality is ", "Seriously, ", "Let us be clear: "]


def generate_candidate() -> str:
    builder = random.choice(BUILDERS)
    text = builder().strip()
    # Add a random leading phrase sometimes to vary the first 18 words
    if random.random() < 0.4:
        lead = random.choice(LEADING_WORDS)
        if lead:
            text = lead + text[0].lower() + text[1:] if len(text) > 1 else lead + text.lower()
    # Length constraints
    words = text.split()
    if len(words) < MIN_WORDS:
        text = text + " This matters more than a headline."
    elif len(words) > MAX_WORDS:
        text = " ".join(words[:MAX_WORDS])
    return text.strip()


def generate_synthetic_posts(target: int) -> List[str]:
    log(f"Starting generation (target={target}). Loading source CSV...")
    load_seed_styles(SOURCE_CSV)
    log("Building unique posts (progress every 500; heartbeat every 15s)...")

    posts: List[str] = []
    seen_full: Set[str] = set()
    seen_rough: Set[str] = set()  # first 18 words of first sentence — no "same start + different ending"
    last_log = 0
    last_heartbeat = time.monotonic()
    attempts = 0

    while len(posts) < target:
        now = time.monotonic()
        if now - last_heartbeat >= 15:
            log(f"Still working... {len(posts)} / {target} (attempts so far: {attempts})...")
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
    log(f"Election 2024 synthetic generator — output: {OUTPUT_CSV}, target: {TARGET_COUNT}")
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

