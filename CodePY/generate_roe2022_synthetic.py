import csv
import random
from typing import List, Set


TARGET_POST_COUNT = 20_000
MIN_WORDS = 6
MAX_WORDS = 60


RANDOM_SEED = 2022


INTRO_QUESTION = [
    "How are we supposed to call this justice",
    "Does anyone honestly believe this is freedom",
    "What kind of democracy rolls back fundamental rights",
    "How do we explain this to the next generation",
    "When did courts start ignoring real people's lives",
    "Why does a handful of judges get to decide our futures",
    "What happens when precedent means nothing to the powerful",
    "Do we really have bodily autonomy in this country anymore",
    "How many lives will be thrown into chaos by this ruling",
    "Who takes responsibility when politics rewrites our private decisions",
]


INTRO_WARNING = [
    "This decision is not the end of the story",
    "People will travel further and pay more just to get basic care",
    "Clinics are closing while lawmakers celebrate on television",
    "Doctors now have to call lawyers before treating patients",
    "Survivors of assault are being turned into test cases",
    "Young people are watching and learning that rights can vanish overnight",
    "Every new ban adds more confusion, fear, and delay to care",
    "The fallout from this ruling will last for generations",
    "Families with wanted pregnancies are suddenly facing impossible choices",
    "Healthcare workers are being forced to choose between ethics and prison",
]


INTRO_MOBILIZE = [
    "If you are angry, channel it into action",
    "We cannot vote away every problem but we can vote out extremists",
    "Courts can overturn precedent but they cannot cancel our turnout",
    "Donate, organize, knock doors, and protect people seeking care",
    "This is not a drill, it is a midterm issue",
    "Rights on paper mean nothing if we stop fighting for them",
    "Protests, court challenges, and elections are all fronts of the same struggle",
    "Talk to your friends who still think voting does not matter",
    "Support funds helping people travel for safe medical care",
    "Remember every lawmaker who celebrated this ruling on camera",
]


INTRO_SUPPORT_DECISION = [
    "Some people are relieved the court finally reversed Roe",
    "For decades activists have pushed to return abortion decisions to the states",
    "Many are cheering what they see as a victory for unborn life",
    "Supporters of the ruling say it corrects a historic mistake",
    "There is a movement that believes this is a moral turning point",
    "For some communities this decision fulfills a long promised goal",
    "Opponents of Roe call this a restoration of constitutional order",
    "Backers of the ruling argue voters should decide abortion policy locally",
    "Religious conservatives are framing this as an answer to prayer",
    "Some commentators insist this will empower families and protect children",
]


TOPICS_RIGHTS = [
    "control over our own pregnancies",
    "access to safe and legal abortion care",
    "the basic idea of bodily autonomy",
    "the right to decide if and when to give birth",
    "privacy in conversations with our doctors",
    "freedom from politicians micromanaging pregnancies",
    "equal citizenship for people who can get pregnant",
    "the promise that rights expand rather than shrink",
    "our ability to plan families and futures",
    "the line between personal faith and public law",
]


TOPICS_FUTURE = [
    "contraception access could be the next battlefield",
    "privacy rights for queer families may be questioned next",
    "interracial marriage and same sex marriage should never be on the table",
    "data from period tracking apps might be used in courtrooms",
    "prosecutors may start testing how far they can criminalize miscarriages",
    "people will cross multiple state lines for routine healthcare",
    "big tech companies will quietly hand over users' messages",
    "insurance coverage for pregnancy and birth will become even more unequal",
    "states could compete to see who can pass the harshest restrictions",
    "constitutional rights will depend more and more on zip code",
]


BLAME_TARGETS = [
    "a radical Supreme Court majority",
    "state legislators who brag about forced birth on television",
    "governors signing bans at celebratory rallies",
    "members of Congress who treat real lives like talking points",
    "donor networks quietly funding every new restriction",
    "judges who treat precedent as optional when it suits them",
    "political strategists using our rights as bargaining chips",
    "attorneys general promising to prosecute doctors and nurses",
    "extremist groups writing model bills behind closed doors",
    "every official who said elections do not have consequences",
]


CONSEQUENCES = [
    "people in medical crisis will be told to come back when they are sicker",
    "low income patients will bear the heaviest burden",
    "rural communities will lose what little reproductive healthcare they had",
    "abuse victims will be pushed deeper into dangerous situations",
    "pregnancy complications will become courtroom debates instead of medical decisions",
    "doctors will leave hostile states rather than risk prison",
    "parents will be forced to choose between rent and travel for care",
    "inequality between states will harden into permanent lines",
    "young people will delay dreams because they cannot trust their rights",
    "emergency rooms will become the front lines of legal battles",
]


CALLS_TO_ACTION = [
    "Register, show up, and vote in every election you can",
    "Support organizations funding travel, lodging, and childcare for patients",
    "Back local candidates who commit to protecting reproductive freedom",
    "Volunteer for clinic escort programs in your community",
    "Push your city and state to become a safe harbor for care",
    "Demand explicit protections for contraception and privacy in law",
    "Join protests that center the people most affected by these bans",
    "Ask your representatives where they stand on criminalizing doctors",
    "Donate to legal defense funds challenging extremist laws",
    "Refuse to normalize a world where rights can vanish overnight",
]


FEELINGS = [
    "angry and exhausted but not surprised",
    "heartbroken for everyone suddenly left without options",
    "worried about friends in states rushing to ban care",
    "furious that ideology is winning over evidence based medicine",
    "afraid of what this means for survivors of assault",
    "worried that marginalized communities will be hit hardest again",
    "tired of watching the same people lose rights over and over",
    "deeply skeptical that this court can be trusted",
    "determined to fight back in every legal way possible",
    "convinced that silence now will be remembered later",
]


HASHTAGS_GENERAL = [
    "#Roe2022",
    "#RoeVWade",
    "#Dobbs",
    "#AbortionRights",
    "#BodilyAutonomy",
    "#ReproductiveJustice",
    "#AbortionIsHealthcare",
    "#MyBodyMyChoice",
    "#ForcedBirth",
    "#SupremeCourt",
]


HASHTAGS_MOBILIZE = [
    "#Vote",
    "#Midterms",
    "#VoteThemOut",
    "#ProtectOurRights",
    "#Protest",
    "#MarchForOurRights",
    "#Organize",
    "#TakeToTheStreets",
    "#CourtInTheStreets",
    "#Democracy",
]


HASHTAGS_SUPPORT_DECISION = [
    "#ProLife",
    "#EndRoe",
    "#LifeWins",
    "#UnbornLivesMatter",
    "#StatesRights",
    "#ProtectTheUnborn",
    "#ProLifeGeneration",
    "#ChooseLife",
    "#CultureOfLife",
    "#LifeIsAFundamentalRight",
]


BLOCKED_SUBSTRINGS = [
    # Intentionally keep this list minimal and rely on curated phrases above.
    # This hook exists so additional blocked terms can be added easily later.
]


def _word_count(text: str) -> int:
    return len(text.strip().split())


def _has_blocked_substring(text: str) -> bool:
    lowered = text.lower()
    return any(bad in lowered for bad in BLOCKED_SUBSTRINGS)


def _build_hashtag_block(source: List[str], min_tags: int = 1, max_tags: int = 3) -> str:
    count = random.randint(min_tags, max_tags)
    tags = random.sample(source, k=count)
    return " " + " ".join(tags)


def _make_rhetorical_question() -> str:
    intro = random.choice(INTRO_QUESTION)
    topic = random.choice(TOPICS_RIGHTS)
    blame = random.choice(BLAME_TARGETS)
    consequence = random.choice(CONSEQUENCES)
    hashtags = _build_hashtag_block(HASHTAGS_GENERAL)
    template = (
        f"{intro} while {blame} pretend this is fine, "
        f"and {topic} turns into a privilege instead of a right, "
        f"knowing that {consequence}?{hashtags}"
    )
    return template


def _make_warning_post() -> str:
    intro = random.choice(INTRO_WARNING)
    future = random.choice(TOPICS_FUTURE)
    consequence = random.choice(CONSEQUENCES)
    feeling = random.choice(FEELINGS)
    hashtags = _build_hashtag_block(HASHTAGS_GENERAL)
    template = (
        f"{intro}. Today it is abortion, tomorrow {future}. "
        f"If we accept this ruling, {consequence}. "
        f"I am {feeling}.{hashtags}"
    )
    return template


def _make_blame_post() -> str:
    blame = random.choice(BLAME_TARGETS)
    topic = random.choice(TOPICS_RIGHTS)
    consequence = random.choice(CONSEQUENCES)
    hashtags = _build_hashtag_block(HASHTAGS_GENERAL)
    template = (
        f"{blame} knew exactly what overturning Roe would do. "
        f"They were warned that taking away {topic} would have consequences. "
        f"Now {consequence}, and they still call it a win.{hashtags}"
    )
    return template


def _make_mobilization_post() -> str:
    intro = random.choice(INTRO_MOBILIZE)
    call = random.choice(CALLS_TO_ACTION)
    feeling = random.choice(FEELINGS)
    hashtags = _build_hashtag_block(HASHTAGS_GENERAL + HASHTAGS_MOBILIZE)
    template = (
        f"{intro}. I am {feeling}. {call}. "
        f"This ruling may stand today but our response will define tomorrow.{hashtags}"
    )
    return template


def _make_support_decision_post() -> str:
    intro = random.choice(INTRO_SUPPORT_DECISION)
    topic = random.choice(TOPICS_RIGHTS)
    future = random.choice(TOPICS_FUTURE)
    hashtags = _build_hashtag_block(HASHTAGS_SUPPORT_DECISION)
    template = (
        f"{intro}. They argue that local voters should set limits, "
        f"that courts went too far before. "
        f"Even then, they will have to answer hard questions about {topic} "
        f"and whether future fights over {future} are really worth celebrating.{hashtags}"
    )
    return template


POST_GENERATORS = [
    _make_rhetorical_question,
    _make_warning_post,
    _make_blame_post,
    _make_mobilization_post,
    _make_support_decision_post,
]


def generate_posts(target_count: int) -> List[str]:
    random.seed(RANDOM_SEED)
    posts: List[str] = []
    seen: Set[str] = set()

    while len(posts) < target_count:
        generator = random.choice(POST_GENERATORS)
        candidate = generator().strip()

        if _has_blocked_substring(candidate):
            continue

        wc = _word_count(candidate)
        if wc < MIN_WORDS or wc > MAX_WORDS:
            continue

        if candidate in seen:
            continue

        seen.add(candidate)
        posts.append(candidate)

    random.shuffle(posts)
    return posts


def write_csv(path: str, posts: List[str]) -> None:
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text"])
        for post in posts:
            writer.writerow([post])


def main() -> None:
    posts = generate_posts(TARGET_POST_COUNT)
    output_path = "Roe2022_synthetic_posts.csv"
    write_csv(output_path, posts)


if __name__ == "__main__":
    main()

