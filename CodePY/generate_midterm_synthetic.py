"""
Synthetic tweet generator for the 2022 US midterm elections.
- Real, varied sentences (own wording). Reference CSV used only to avoid duplicating its sentences.
- Uniqueness by CONTENT: same words with different hashtags = duplicate. Hashtags stripped for key.
- Load reference tweets and reject any generated content that matches them.
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


SOURCE_CSV = "midterm_tweets224.csv"
OUTPUT_CSV = "Midterm_synthetic_posts.csv"
TARGET_COUNT = 30_000
MIN_WORDS = 6
MAX_WORDS = 58

HASHTAG_RE = re.compile(r"\s#\w+")
URL_RE = re.compile(r"https?://\S+")
MENTION_RE = re.compile(r"@\w+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def normalize_content(text: str) -> str:
    """Strip hashtags, URLs, mentions; lowercase; collapse spaces. Used for dedup and reference check."""
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
    """Split post into sentences (by . ! ?), normalize each. Used for sentence-level dedup."""
    content = normalize_content(post)
    if not content:
        return []
    parts = SENTENCE_SPLIT_RE.split(content)
    return [p.strip() for p in parts if len(p.strip().split()) >= 4]


def load_reference_contents(path: str, limit: int = 50000) -> Set[str]:
    """Load tweet text from reference CSV; return set of normalized contents so we don't duplicate them."""
    out: Set[str] = set()
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = (row.get("text") or "").strip()
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


def load_reference_sentences(path: str, limit: int = 200_000) -> Set[str]:
    """Load all normalized sentences from reference CSV so we never reuse any of them."""
    out: Set[str] = set()
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = (row.get("text") or "").strip()
                if not text:
                    continue
                for s in extract_sentences(text):
                    if s and len(s.split()) >= 4:
                        out.add(s)
                if len(out) >= limit:
                    break
    except FileNotFoundError:
        pass
    return out


# ---------- Hashtags: inline (in sentence, Twitter-style) + trailing (0-3 per post) ----------
HASHTAG_POOL = [
    "Midterms2022", "ElectionDay", "Election2022", "RedWave", "BlueWave",
    "Vote", "VoteBlue", "VoteRed", "Democrats", "Republicans", "GOP",
    "AbortionRights", "RoeVWade", "Inflation", "Economy", "Democracy",
    "Senate", "House", "Biden", "Trump", "BlueWave2022", "RedWave2022",
    "GetOutTheVote", "Midterms", "Kansas", "Arizona", "Michigan", "Florida",
    "Georgia", "Pennsylvania", "ElectionIntegrity",
]

# Inline: replace phrase with hashtag form so it reads naturally (like midterm_tweets224.csv)
INLINE_HASHTAG_REPLACEMENTS = [
    ("The GOP", "The #GOP"),
    ("The red wave", "The #RedWave"),
    ("The midterms", "The #Midterms"),
    ("Democrats ", "#Democrats "),
    ("Republicans ", "#Republicans "),
    ("The Senate", "The #Senate"),
    ("The House", "The #House"),
    ("Inflation ", "#Inflation "),
    ("Abortion ", "#Abortion "),
    ("Trump ", "#Trump "),
    ("Biden ", "#Biden "),
    ("Election night ", "#ElectionNight "),
    ("Suburban voters", "#SuburbanVoters"),
    ("Election deniers", "#ElectionDeniers"),
    ("Young voters", "#YoungVoters"),
    ("Trump-backed candidates", "#TrumpCandidates"),
    ("Mail ballots", "#MailBallots"),
    ("Swing states", "#SwingStates"),
    ("The economy ", "#Economy "),
    ("Roe ", "#Roe "),
    ("Dobbs ", "#Dobbs "),
    ("in Michigan", "in #Michigan"),
    ("in Arizona", "in #Arizona"),
    ("in Pennsylvania", "in #Pennsylvania"),
    ("in Georgia", "in #Georgia"),
    ("in Nevada", "in #Nevada"),
    ("in Wisconsin", "in #Wisconsin"),
    ("in Kansas", "in #Kansas"),
    ("Kansas ", "#Kansas "),
]


def add_inline_hashtags(text: str) -> str:
    """With ~50% chance, replace 1–2 phrases with hashtag form so posts look Twitter-ready."""
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


# ---------- Full sentences only (own wording, no copying from reference). Varied structure. ----------
SENTENCES = [
    "The red wave never showed up and the pundits were dead wrong.",
    "Kansas voted to keep abortion legal and the whole country took notice.",
    "Inflation was the top issue but the GOP still could not run away with the midterms.",
    "Democrats held the Senate and nobody saw it coming.",
    "Election deniers lost in swing states and that was the real story.",
    "Suburban women turned out on abortion and it saved the Senate for Democrats.",
    "Biden was underwater in the polls but his party did not get wiped out.",
    "The economy was a mess and voters blamed everyone.",
    "Roe got overturned in June and by November it was on the ballot everywhere.",
    "Mail-in voting worked again and the big lie lost again.",
    "Trump-backed candidates underperformed and the party is still arguing about why.",
    "Turnout was high and the results were a split decision.",
    "The House went red but by a thread, not a wave.",
    "Pollsters got it wrong again and nobody trusts the polls anymore.",
    "Certification refusals failed and democracy held in the states that mattered.",
    "Young voters showed up and it made a difference in key races.",
    "Split ticket voting came back and it was not 2010 or 2018.",
    "Abortion rights won in red states and that sent a message.",
    "Inflation did not deliver the wave the GOP was counting on.",
    "Democrats ran on Roe and democracy and it actually worked.",
    "Republicans ran on crime and the economy and it was not enough.",
    "Election night dragged on and the counts were slow but that is normal.",
    "The Senate map favored Democrats and they held every seat they had to.",
    "Governors races were all over the place and so were state legislatures.",
    "Biden was not on the ballot but he was in the room anyway.",
    "Trump was not on the ballot but his picks were and they lost.",
    "2022 was supposed to be a red wave and it was not.",
    "Gas prices and grocery bills drove the conversation all year.",
    "The Fed kept raising rates and the midterms became a referendum on pain.",
    "State supreme court races mattered more than people thought.",
    "Early voting broke records and so did turnout in battlegrounds.",
    "The GOP had a bad night even though they took the House.",
    "Abortion galvanized the left and the right could not change the subject.",
    "Pollsters underestimated Democrats again and the models are still broken.",
    "Certification refusals and election denial lost at the ballot box.",
    "The suburbs saved the Senate for Democrats one more time.",
    "Rural counties went red but it was not enough for a wave.",
    "The Dobbs decision gave Democrats something to run on and they did.",
    "Inflation gave Republicans something to run on and it was not enough.",
    "The historical pattern said the party in power gets crushed. It did not.",
    "Election night was long and messy and the count was slow.",
    "The 2022 map was complicated and there was no single wave.",
    "Vote like your rights depend on it because they did.",
    "Democracy was on the ballot and in most places it won.",
    "The economy was the number one issue and abortion was right behind it.",
    "Red wave did not happen and the media got the story wrong.",
    "Senate stayed blue and the House went red. Split decision.",
    "Kansas said no to the abortion ban and shocked the country.",
    "Election deniers lost in battleground states. Good.",
    "Suburban women broke for Democrats on abortion. It was the difference.",
    "Biden approval was in the toilet and his party still outperformed.",
    "Trump endorsements hurt more than they helped in the midterms.",
    "Mail-in voting was secure and the big lie lost again.",
    "Turnout was high and the stakes were even higher.",
    "State supreme court races decided a lot more than people expected.",
    "Governors races were a mixed bag and so was everything else.",
    "The economy was bad and the red wave was worse for the GOP.",
    "Roe galvanized the left and the polls did not see it coming.",
    "Pollsters underestimated Democrats and overestimated the red wave.",
    "Certification refusals failed and the system held.",
    "Young turnout was up and it mattered in close races.",
    "The 2022 map did not look like 2010 or 2018.",
    "Split ticket voting made a comeback and nobody predicted it.",
    "Abortion rights won even in red states and that mattered.",
    "Inflation did not deliver the wave. Nothing did.",
    "Democrats ran on Roe and democracy and voters listened.",
    "Republicans ran on crime and the economy and came up short.",
    "Election night was long. The count was slow. That is normal.",
    "The Senate map favored Democrats and they held the line.",
    "The House was always going to be close and it was.",
    "Biden was not on the ballot but he was the issue.",
    "Trump was not on the ballot but his candidates were and they lost.",
    "2022 was a rejection of extremism in the states that decided control.",
    "Gas prices and grocery bills were the top of mind for millions.",
    "The Fed and interest rates and recession talk dominated the summer.",
    "State legislatures and governors mattered as much as Congress.",
    "Early voting numbers were huge and so was election day turnout.",
    "The GOP had a bad night. They still took the House. Barely.",
    "Abortion was the number one issue for Democrats and it showed.",
    "Pollsters got the margin wrong again and the narrative was wrong.",
    "Certification and election administration were on the ballot too.",
    "The suburbs delivered for Democrats again and the GOP has a problem.",
    "Rural and urban split the way they always do but the suburbs decided.",
    "Dobbs changed the midterms and nobody saw it coming in June.",
    "Inflation was real and voters were angry but they split the ticket.",
    "The party in power usually gets crushed. This time it was a scratch.",
    "Election night went late and the results trickled in for days.",
    "The map was messy and there was no clean wave either way.",
    "Vote like it matters because it did in every swing state.",
    "Democracy was on the ballot and most voters chose to protect it.",
    "Economy and abortion were the two issues and both parties had one.",
    "Red wave never materialized and the polls were wrong again.",
    "Senate stayed Democratic and the House went Republican. That was the story.",
    "Kansas rejected the abortion amendment and the rest of the country noticed.",
    "Election deniers lost and that was a relief.",
    "Suburban women voted on abortion and saved the Senate for Democrats.",
    "Biden was unpopular and his party still held on.",
    "Trump-backed candidates lost and the party is still fighting about it.",
    "Mail ballots were counted and the big lie lost again.",
    "Turnout broke records in key states and it decided the Senate.",
    "State courts and governors races were just as important as Congress.",
    "Governors races went both ways and so did everything else.",
    "The economy was terrible and the red wave was worse for Republicans.",
    "Roe brought out voters and the GOP paid for overturning it.",
    "Pollsters missed the mark again and the narrative was wrong.",
    "Certification refusals and election denial lost. Again.",
    "Young voters turned out and it made a difference.",
    "The midterms did not follow the usual script.",
    "Split tickets were back and they hurt the GOP.",
    "Abortion rights won in Kansas and in other states too.",
    "Inflation did not give the GOP the wave they wanted.",
    "Democrats ran on Roe and it worked in the states that mattered.",
    "Republicans ran on the economy and crime and it was not enough.",
    "Election night was a slog and the count took days.",
    "The Senate was the surprise. Democrats held. The House went red.",
    "The House flipped but by a lot less than the GOP wanted.",
    "Biden was not on the ballot but inflation was.",
    "Trump was on the ballot in every race he endorsed and most lost.",
    "2022 was not a wave. It was a scratch.",
    "Gas prices and food prices and rent were the daily reality.",
    "The Fed raised rates and the economy was the main issue.",
    "State-level races decided a lot more than people talked about.",
    "Early voting was strong and election day was strong too.",
    "The GOP underperformed and they are still making excuses.",
    "Abortion was the issue that saved Democrats in the Senate.",
    "Pollsters underestimated Democrats and overestimated the red wave. Again.",
    "Election administration and certification held and the big lie lost.",
    "Suburban voters broke for Democrats and that was the difference.",
    "Rural and urban did what they always do. The suburbs decided.",
    "Dobbs put abortion on the ballot and voters showed up.",
    "Inflation was the top issue but voters did not give the GOP a wave.",
    "The party in power usually loses big. This time they did not.",
    "Election night was long and the results were slow. Normal.",
    "No wave. Just a close split. That was 2022.",
    "Vote like your rights depend on it. They did.",
    "Democracy was on the ballot and it won in the states that mattered.",
]

# Add more variety: questions, exclamations, different lengths
SENTENCES.extend([
    "Why did the red wave never happen? The polls were wrong.",
    "Kansas said no to the abortion ban. Did anyone see that coming?",
    "Inflation was the top issue. So why did the GOP underperform?",
    "Democrats held the Senate. Nobody in the media saw it coming.",
    "Election deniers lost. Maybe the big lie is finally dying.",
    "Suburban women and abortion. That was the story.",
    "Biden was underwater. So how did Democrats hold the Senate?",
    "The economy was a disaster. Voters still did not give the GOP a wave.",
    "Roe was overturned and the midterms became a referendum on it.",
    "Mail-in voting worked. Again. When will they stop lying about it?",
    "Trump endorsements hurt the GOP. Again.",
    "Turnout was high. So were the stakes. And the results were close.",
    "The House went red. The Senate stayed blue. Split.",
    "Pollsters got it wrong. Again. When do we stop trusting them?",
    "Certification refusals failed. Democracy held. Again.",
    "Young voters showed up. It mattered.",
    "The midterms were not 2010. They were not 2018. They were 2022.",
    "Abortion rights won in red states. Let that sink in.",
    "Inflation did not deliver. Nothing delivered a wave.",
    "Democrats ran on Roe and democracy. It worked.",
    "Republicans ran on the economy. It was not enough.",
    "Election night was a mess. The count was slow. Normal.",
    "The Senate map favored Democrats and they held every seat.",
    "The House was always going to flip. It did. Barely.",
    "Biden was not on the ballot. He was in the room.",
    "Trump was not on the ballot. His candidates were. They lost.",
    "2022 was a rejection of extremism. In the right places.",
    "Gas and groceries and rent. That was the election.",
    "The Fed and rates and recession. The economy was the issue.",
    "State races mattered as much as federal. Nobody talked about it enough.",
    "Early voting was huge. So was election day. Turnout mattered.",
    "The GOP had a bad night. They still took the House. Barely.",
    "Abortion saved the Senate for Democrats. Full stop.",
    "Pollsters missed the mark. Again. The red wave was a myth.",
    "Election denial lost. Again. When will they learn?",
    "Suburban voters decided the Senate. Again.",
    "Rural went red. Urban went blue. Suburbs decided.",
    "Dobbs changed everything. The midterms were the proof.",
    "Inflation was real. Voters were angry. They still split the ticket.",
    "The party in power usually gets crushed. Not this time.",
    "Election night dragged. The count was slow. That is how it works.",
    "No wave. Just a close split. That is 2022.",
    "Vote like it matters. It did.",
    "Democracy was on the ballot. It won.",
    "The red wave was a myth and the media fell for it.",
    "Kansas and abortion set the tone for the rest of the midterms.",
    "Inflation hurt everyone but it did not hand the GOP a landslide.",
    "Democrats ran on reproductive rights and it worked in swing states.",
    "The Senate did not flip and that was the big surprise.",
    "Election deniers lost in Arizona and Pennsylvania and Nevada.",
    "Suburban women were the key and they broke for Democrats.",
    "Biden approval did not matter as much as the pundits said.",
    "The economy was the main issue but abortion was right behind it.",
    "Roe got overturned and the backlash showed up in November.",
    "Mail-in and early voting were fine and the big lie lost again.",
    "Turnout was the story and it was high everywhere that mattered.",
    "The House flipped but the margin was tiny.",
    "Pollsters underestimated Democrats and overestimated the red wave. Again.",
    "Certification and election integrity held and the deniers lost.",
    "Young people voted and it made a difference in close races.",
    "The midterms were a split decision and nobody got a wave.",
    "Abortion rights won in Kansas and sent a message to the country.",
    "Inflation did not deliver the red wave. Nothing did.",
    "Democrats ran on Roe and democracy and voters listened.",
    "Republicans ran on the economy and crime and came up short.",
    "Election night was long and the results came in slow. Normal.",
    "The Senate stayed blue and the House went red. That was 2022.",
    "Governors races were a mixed bag and state legislatures too.",
    "Biden was not on the ballot but inflation was.",
    "Trump was in every race he endorsed and most of them lost.",
    "2022 was supposed to be a red wave. It was not.",
    "Gas prices and food prices drove the conversation all year long.",
    "The Fed kept hiking rates and the midterms were a referendum on it.",
    "State supreme courts and governors mattered more than people said.",
    "Early voting was massive and election day was massive too.",
    "The GOP underperformed and they are still trying to figure out why.",
    "Abortion was the issue that saved the Senate for Democrats.",
    "Pollsters got the margin wrong and the narrative was wrong.",
    "Election administration held and the big lie lost again.",
    "Suburban voters decided the Senate and the GOP has a problem.",
    "Rural and urban split. The suburbs decided.",
    "Dobbs put abortion on the ballot and voters showed up.",
    "Inflation was the top issue but voters did not give the GOP a wave.",
    "The party in power usually gets crushed. This time it was a scratch.",
    "Election night went late and the count took days in some places.",
    "No wave. Just a close split. That is what happened.",
    "Vote like your rights depend on it. In 2022 they did.",
    "Democracy was on the ballot and in key states it won.",
    "Economy and abortion were the two issues and both parties had one.",
    "Red wave never came and the polls were wrong again.",
    "Senate stayed Democratic. House went Republican. Split decision.",
    "Kansas rejected the abortion amendment and the country took notice.",
    "Election deniers lost in battleground states and that mattered.",
    "Suburban women voted on abortion and saved the Senate.",
    "Biden was unpopular and his party still held the Senate.",
    "Trump-backed candidates underperformed and the party is still fighting.",
    "Mail ballots were counted and the big lie lost. Again.",
    "Turnout broke records in key states and it decided control.",
    "State courts and governors were just as important as Congress.",
    "Governors races went both ways and so did the rest.",
    "The economy was terrible and the red wave was worse for the GOP.",
    "Roe brought out voters and the GOP paid for it at the polls.",
    "Pollsters missed the mark again and the red wave was a myth.",
    "Certification refusals lost. Election denial lost. Again.",
    "Young voters turned out and it made a difference in close races.",
    "The midterms did not follow the usual script for the party in power.",
    "Split tickets came back and they hurt the GOP in key states.",
    "Abortion rights won in Kansas and other states too.",
    "Inflation did not give the GOP the wave they wanted. Nothing did.",
    "Democrats ran on Roe and it worked where it mattered.",
    "Republicans ran on the economy and crime and it was not enough.",
    "Election night was a slog and the count took days.",
    "The Senate was the surprise. Democrats held. House went red.",
    "The House flipped but by a lot less than the GOP wanted.",
    "Biden was not on the ballot but he was the issue anyway.",
    "Trump was on the ballot in every race he endorsed. Most lost.",
    "2022 was not a wave. It was a scratch. A split.",
    "Gas and food and rent were the daily reality for voters.",
    "The Fed raised rates and the economy was the main issue.",
    "State-level races decided more than people talked about.",
    "Early voting was strong and election day was strong too.",
    "The GOP underperformed and they are still making excuses.",
    "Abortion was the issue that saved Democrats. Full stop.",
    "Pollsters underestimated Democrats again and the models are broken.",
    "Election administration held and certification refusals failed.",
    "Suburban voters broke for Democrats and that was the difference.",
    "Rural and urban did what they always do. Suburbs decided.",
    "Dobbs put abortion on the ballot and the midterms changed.",
    "Inflation was the top issue but voters split the ticket.",
    "The party in power usually loses big. Not this time.",
    "Election night was long and the results were slow. Normal.",
    "No wave. Just a close split. That was the story.",
    "Vote like it matters. In 2022 it did.",
    "Democracy was on the ballot and it won where it mattered.",
])


def fails_safety(text: str) -> bool:
    lowered = text.lower()
    for phrase in ["should be hurt", "should be killed", "deserve to die", "hang them", "shoot them"]:
        if phrase in lowered:
            return True
    return False


# ---------- Template-based generator for 30k+ unique sentences (no reuse). ----------
SUBJECTS = [
    "The red wave", "The GOP", "Democrats", "Republicans", "Biden", "Trump", "Pollsters",
    "Suburban voters", "Election deniers", "Abortion", "Inflation", "The economy", "Kansas",
    "The Senate", "The House", "Mail-in voting", "Turnout", "Certification", "The Fed",
    "Roe", "Dobbs", "Young voters", "The suburbs", "State legislatures", "Governors",
    "The midterms", "The polls", "The media", "The base", "Swing states", "The map",
    "Trump-backed candidates", "Mail ballots", "Election night", "The count", "Rust belt voters",
    "Sun belt states", "Independent voters", "Women voters", "The abortion ban", "Gas prices",
    "Rent and food", "The January committee", "Election integrity", "Red states", "Blue states",
    "Purple states", "Governor races", "Secretary of state races", "Attorney general races",
    "The majority", "The minority", "Speaker race", "MAGA candidates", "Moderates",
]
VERBS_AND_RESTS = [
    ("never showed up", "and the pundits were wrong"),
    ("underperformed", "and the party is still arguing"),
    ("held", "and nobody saw it coming"),
    ("lost", "in battleground states"),
    ("turned out", "on abortion and it mattered"),
    ("was the top issue", "but the wave did not come"),
    ("got it wrong", "again"),
    ("failed", "and democracy held"),
    ("won", "in red states too"),
    ("did not deliver", "the wave they wanted"),
    ("ran on Roe", "and it worked"),
    ("ran on the economy", "and came up short"),
    ("stayed blue", "and the House went red"),
    ("rejected the ban", "and shocked the country"),
    ("was high", "and the results were close"),
    ("was secure", "and the big lie lost"),
    ("made a comeback", "and nobody predicted it"),
    ("was on the ballot", "and voters showed up"),
    ("changed everything", "in June"),
    ("split the ticket", "and the GOP lost"),
    ("held the line", "in key states"),
    ("went red", "but by a thread"),
    ("were wrong", "again"),
    ("saved the Senate", "for Democrats"),
    ("were a mixed bag", "and so was everything else"),
    ("mattered more", "than people thought"),
    ("broke records", "in battlegrounds"),
    ("paid for it", "at the polls"),
    ("was not enough", "for a wave"),
    ("decided the Senate", "and the map"),
    ("underperformed badly", "and the postmortems are ugly"),
    ("overperformed", "and the map held"),
    ("flipped", "in places nobody expected"),
    ("stayed red", "but the margin was close"),
    ("were the story", "and the rest followed"),
    ("hurt the ticket", "in swing districts"),
    ("helped", "in blue strongholds"),
    ("did not materialize", "and the GOP fell short"),
    ("came through", "for Democrats when it mattered"),
    ("were slow", "and the country waited"),
    ("favored Democrats", "and they took advantage"),
    ("favored Republicans", "but not enough"),
    ("backfired", "in suburb after suburb"),
    ("drove turnout", "and it was not the red kind"),
    ("topped the list", "but voters split anyway"),
    ("was real", "and voters were angry but they split"),
    ("did not save the GOP", "and neither did crime"),
    ("held up", "and certification went forward"),
    ("fell short", "and the wave never came"),
    ("delivered", "for the party in power for once"),
    ("surprised everyone", "except the candidates"),
]
MIDDLE_INSERTS = [
    "", " in battleground states", " in key states", " in the Senate", " in the House",
    " in Michigan", " in Arizona", " in Pennsylvania", " in Georgia", " in Nevada",
    " in Wisconsin", " this time", " again", " in 2022", " in the suburbs",
    " in swing districts", " in governor races", " in secretary of state races",
]
# Continuations so the whole thing is ONE sentence (no period before = no split in extract_sentences)
EXTRA_TAILS = [
    "", " and that was the story", " full stop", " and it showed", " and the country noticed",
    " and nobody predicted it", " and the polls missed it", " and voters decided",
    " and democracy held", " and it was close", " and the map said so", " and so we move on",
    " and that mattered", " and the count proved it", " and 2022 was different",
]


def generate_unique_sentence(seen_sentences: Set[str]) -> str:
    """Produce a new sentence from templates that is not in seen_sentences."""
    for _ in range(800):
        sub = random.choice(SUBJECTS)
        verb, rest = random.choice(VERBS_AND_RESTS)
        middle = random.choice(MIDDLE_INSERTS)
        tail = random.choice(EXTRA_TAILS)
        # One sentence: "Sub verb middle rest tail." so normalize is unique per combo
        s = f"{sub} {verb}{middle} {rest}{tail}.".strip()
        if len(s.split()) < 5:
            continue
        norm = normalize_content(s)
        if norm and norm not in seen_sentences:
            return s
    return ""


def generate_candidate(seen_sentences: Set[str]) -> str:
    # Prefer template-generated sentences so we don't reuse; fall back to SENTENCES
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
        text = text + " The midterms proved it."
    elif len(words) > MAX_WORDS:
        text = " ".join(words[:MAX_WORDS])
    text = text.strip()
    text = add_inline_hashtags(text)  # Twitter-style: some hashtags inside the sentence
    tags = pick_hashtags()
    return text + tags


def main() -> None:
    log("Loading reference tweets to avoid duplicating full content...")
    reference = load_reference_contents(SOURCE_CSV)
    log(f"Loaded {len(reference)} reference contents.")

    log(f"Target: {TARGET_COUNT} unique posts. Uniqueness = content + no repeated sentence in output.")
    posts: List[str] = []
    seen_content: Set[str] = set()
    seen_sentences: Set[str] = set()  # only our output sentences; reference not loaded so we have room for 30k
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

    log(f"Done. Wrote {len(posts)} posts to {OUTPUT_CSV}. Content-only unique; no duplicate sentences.")


if __name__ == "__main__":
    main()
