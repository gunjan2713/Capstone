# telegram_bigpull_elections2020.py
# Pull LOTS more messages via:
# - Wider date window
# - Automatic discovery of public channels/groups per query
# - Optional dump mode (no keyword filter)
# - Linked discussion scans
# - FloodWait handling + resumable CSV

import os
import re
import asyncio
import pandas as pd
from datetime import datetime, timezone
from telethon import TelegramClient, errors
from telethon.tl.types import PeerChannel, Channel, Chat, User
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.contacts import SearchRequest as ContactsSearchRequest

# =========================
# CONFIG
# =================
API_ID = int(os.getenv("TG_API_ID", "28629787"))
API_HASH = os.getenv("TG_API_HASH", "f87a2e63bc64eb0f187100f5a58fea75")
SESSION_NAME = os.getenv("TG_SESSION_NAME", "Gunja")
OUTPUT_CSV = os.getenv("TG_OUTPUT_CSV", "Elections2020Tel.csv")

# >>> Window to capture pre-election, election night, and immediate post-election discussion <<<
MIN_DATE = datetime(2020, 10, 1, tzinfo=timezone.utc)   # start of big election chatter
MAX_DATE = datetime(2021, 1, 15, tzinfo=timezone.utc)   # include post-election disputes & counts

# Mode: "dump" grabs everything in window; "search" uses server-side keywords
MODE = os.getenv("TG_MODE", "dump").lower()  # <-- default to dump for max volume

# Server-side search keywords (used only if MODE="search")
KEYWORDS = [
    "election", "election2020", "election 2020", "vote", "voting", "vote2020", "voted",
    "mail-in", "mail in ballot", "mail-in ballot", "absentee", "absentee ballot",
    "count the votes", "counteveryvote", "stop the steal", "ballot", "ballots",
    "voter suppression", "ballot harvesting", "polling place", "poll worker",
    "election fraud", "vote fraud", "voter fraud", "red wave", "blue wave",
    "Biden", "BidenHarris", "Joe Biden", "Trump", "Donald Trump", "Trump2020",
    "#Election2020", "#Vote", "#MailInBallot", "#CountEveryVote", "#StopTheSteal",
    "#Biden", "#Trump", "#BlueWave", "#RedWave", "election night", "election results",
    "certification", "state certification", "electoral college", "electors"
]

# Optional permissive regex (kept ON but doesn’t drop matches in dump mode)
LOCAL_REGEX = re.compile(
    r"(election(?:\s*2020)?|vote(?:d|s)?|mail[\-\s]*in|absentee|ballot|count(?:\s*the)?\s*votes|stop\s*the\s*steal|certif(?:y|ication)|electoral\s*college)",
    re.I
)

# Initial seed channels (some may be invalid; we skip gracefully)
SEED_CHANNELS = [
    'washingtonpost', 'cnnbrk', 'foxnews', 'thehill', 'realclearpolitics',
    'politico', 'nytimes', 'bloomberg', 'breaking911', 'newsmax', 'oann',
    'realdonaldtrump', 'joebiden', 'electionupdates', 'us_politics', 'voteusa'
]

# Discovery queries to find **more** public channels/groups to scan
DISCOVERY_QUERIES = [
    "Election 2020", "Election2020", "Vote", "Mail-In Ballot", "Absentee Ballot",
    "Count Every Vote", "StopTheSteal", "Election Results", "Electoral College",
    "Poll Worker", "Voting rights"
]
DISCOVERY_LIMIT_PER_QUERY = 50  # try 50–100 for more breadth

# Checkpoint frequency
FLUSH_EVERY = 1000  # bumping higher to reduce I/O

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
RESOLVED = {}  # username -> channel_id cache


# =========================
# CSV helpers
# =========================
def _ensure_cols(df: pd.DataFrame) -> pd.DataFrame:
    want = [
        "SourcePeer", "MessageID", "Date", "Message", "Views", "ForwardsCount", "Reactions",
        "IsForward", "FwdFromPeer", "ReplyToMsgID", "PostLink"
    ]
    for c in want:
        if c not in df.columns:
            df[c] = pd.Series(dtype="object")
    return df[want]

def _read_existing_ids():
    if not os.path.exists(OUTPUT_CSV) or os.path.getsize(OUTPUT_CSV) == 0:
        return set(), 0, pd.DataFrame()
    df = pd.read_csv(OUTPUT_CSV, dtype={"SourcePeer":"string"}, na_values=["", "nan", "NaN", "None"])
    df = _ensure_cols(df)
    df["MessageID"] = pd.to_numeric(df["MessageID"], errors="coerce").astype("Int64")
    df["SourcePeer"] = df["SourcePeer"].astype("string")
    df = df[df["MessageID"].notna() & df["SourcePeer"].notna()]
    keyset = set(zip(df["SourcePeer"].astype(str), df["MessageID"].astype(int)))
    return keyset, len(df), df

def _row_from_message(peer_name: str, m, base_link: str):
    text = (m.raw_text or "").replace("\n", " ").strip()
    is_forward = bool(getattr(m, "fwd_from", None))
    fwd_from_peer = ""
    if is_forward and getattr(m.fwd_from, "from_name", None):
        fwd_from_peer = m.fwd_from.from_name
    elif is_forward and getattr(m.fwd_from, "from_id", None):
        fwd_from_peer = str(m.fwd_from.from_id)
    reactions_summary = None
    if getattr(m, "reactions", None) and getattr(m.reactions, "results", None):
        parts = []
        for r in m.reactions.results:
            emoji = getattr(r.reaction, "emoticon", None) or "?"
            parts.append(f"{emoji}:{r.count}")
        reactions_summary = " ".join(parts) if parts else None
    return {
        "SourcePeer": peer_name,
        "MessageID": m.id,
        "Date": m.date,
        "Message": text,
        "Views": getattr(m, "views", None),
        "ForwardsCount": getattr(m, "forwards", None),
        "Reactions": reactions_summary,
        "IsForward": is_forward,
        "FwdFromPeer": fwd_from_peer,
        "ReplyToMsgID": getattr(m, "reply_to_msg_id", None),
        "PostLink": f"{base_link}/{m.id}"
    }


# =========================
# Telethon helpers
# =========================
async def _iter_safe_messages(entity, **kwargs):
    while True:
        try:
            async for msg in client.iter_messages(entity, **kwargs):
                yield msg
            break
        except errors.FloodWaitError as e:
            sleep_s = int(getattr(e, "seconds", 5)) + 1
            print(f"⏳ Flood wait {sleep_s}s for {getattr(entity, 'username', entity)} …")
            await asyncio.sleep(sleep_s)
        except errors.ServerError:
            print("⚠️ Server error, retrying in 3s …")
            await asyncio.sleep(3)

async def _get_linked_discussion(entity):
    try:
        full = await client(GetFullChannelRequest(entity))
        linked = getattr(full, "full_chat", None)
        linked_id = getattr(linked, "linked_chat_id", None)
        if linked_id:
            return PeerChannel(linked_id)
    except Exception:
        pass
    return None

async def get_entity_resilient(username: str):
    if username in RESOLVED:
        return PeerChannel(RESOLVED[username])
    ent = await client.get_entity(username)
    if getattr(ent, "id", None):
        RESOLVED[username] = ent.id
    return ent

async def discover_public_chats(queries, limit_per_query=50):
    """Find more public channels/groups to scan using Telegram's public search."""
    found_usernames = set()
    for q in queries:
        try:
            res = await client(ContactsSearchRequest(q=q, limit=limit_per_query))
            for u in res.users:
                if isinstance(u, User) and getattr(u, "username", None):
                    found_usernames.add(u.username.lower())
            for c in res.chats:
                # Channel or megagroup
                if isinstance(c, (Channel, Chat)) and getattr(c, "username", None):
                    found_usernames.add(c.username.lower())
        except Exception:
            continue
    return sorted(found_usernames)


# =========================
# Main scrape
# =========================
async def scrape():
    await client.start()

    # Seed + discovered channels
    discovered = await discover_public_chats(DISCOVERY_QUERIES, DISCOVERY_LIMIT_PER_QUERY)
    channel_usernames = []
    # Keep seeds (some may not resolve) + discovered (unique)
    seen_names = set()
    for name in SEED_CHANNELS + discovered:
        if not name: 
            continue
        n = name.strip().lstrip("@")
        if n and n.lower() not in seen_names:
            seen_names.add(n.lower())
            channel_usernames.append(n)

    print(f"📚 Will scan {len(channel_usernames)} peers (seed + discovered)")

    seen_keys, running_count, existing_df = _read_existing_ids()
    new_rows = []

    async def flush_rows(force=False):
        nonlocal new_rows, running_count, existing_df
        if not new_rows:
            return
        if not force and len(new_rows) < FLUSH_EVERY:
            return
        df_new = pd.DataFrame(new_rows)
        if not df_new.empty:
            df_new = _ensure_cols(df_new)
            df_out = df_new if existing_df is None or existing_df.empty else pd.concat([existing_df, df_new], ignore_index=True)
            df_out.to_csv(OUTPUT_CSV, index=False)
            running_count = len(df_out)
            existing_df = df_out
            print(f"💾 Wrote {len(df_new)} rows (total: {running_count}) → {OUTPUT_CSV}")
        new_rows = []

    async def collect_from_peer(peer_username: str):
        nonlocal seen_keys, new_rows
        try:
            entity = await get_entity_resilient(peer_username)
        except Exception as e:
            print(f"❌ Cannot access {peer_username}: {e}")
            return

        base_link = f"https://t.me/{peer_username}"
        peers_to_scan = [(entity, base_link, peer_username)]

        # Linked discussion
        linked = await _get_linked_discussion(entity)
        if linked:
            try:
                linked_entity = await client.get_entity(linked)
                linked_name = getattr(linked_entity, "username", None) or f"{peer_username}-discussion"
                linked_link = f"https://t.me/{linked_name}" if getattr(linked_entity, "username", None) else base_link
                peers_to_scan.append((linked_entity, linked_link, linked_name))
                print(f"💬 Found linked discussion for {peer_username}: {linked_name}")
            except Exception:
                pass

        for peer_entity, link, peer_print_name in peers_to_scan:
            print(f"🔎 Scanning {peer_print_name} ({MODE}) in {MIN_DATE.date()} → {MAX_DATE.date()}")
            try:
                if MODE == "dump":
                    it = _iter_safe_messages(
                        peer_entity,
                        offset_date=MAX_DATE,
                        reverse=False,   # newest → oldest
                        limit=None
                    )
                else:
                    async def per_keyword():
                        for kw in KEYWORDS:
                            await asyncio.sleep(0.15)
                            async for m in _iter_safe_messages(
                                peer_entity,
                                search=kw,
                                offset_date=MAX_DATE,
                                reverse=False,
                                limit=None
                            ):
                                if m.date is None or m.date < MIN_DATE:
                                    break
                                yield m
                    it = per_keyword()

                async for m in it:
                    if m.date is None or m.date < MIN_DATE:
                        break

                    # Optional regex context check (doesn't drop in dump mode)
                    if MODE == "search":
                        txt = (m.raw_text or "")
                        if txt and not LOCAL_REGEX.search(txt):
                            pass  # keep anyway; server matched kw

                    key = (peer_print_name, m.id)
                    if key in seen_keys:
                        continue

                    row = _row_from_message(peer_print_name, m, link)
                    new_rows.append(row)
                    seen_keys.add(key)

                    if len(new_rows) >= FLUSH_EVERY:
                        await flush_rows(force=False)

            except Exception as e:
                print(f"⚠️ Error while scanning {peer_print_name}: {e}")

        await flush_rows(force=False)

    # Sequential is safer for rate limits; you can parallelize carefully if needed
    for ch in channel_usernames:
        await collect_from_peer(ch)

    await flush_rows(force=True)
    print("✅ Done.")


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(scrape())
