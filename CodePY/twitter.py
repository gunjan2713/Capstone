# twitter_collect.py
from __future__ import annotations
from twikit import Client, TooManyRequests
import csv, asyncio, os, re, math, random
from datetime import datetime, timedelta, timezone
from typing import Iterable

# ========= CONFIG =========
OUTPUT = "midterm_tweets223.csv"
COOKIES = "cookies1.json"
LANG = "en"
PRODUCTS = ["Latest", "Top"]         # try both to widen coverage
BATCH_SIZE = 500                      # flush every N rows
WINDOW_HOURS = 24                     # per-window size
START = datetime(2022, 8, 1, tzinfo=timezone.utc)
END   = datetime(2022, 11, 30, tzinfo=timezone.utc)  # exclusive
QUERY_SHARDS = [
    "#RedWave OR #BlueWave OR #ElectionDay",
    "#Vote2022 OR #Midterms OR #Midterms2022",
    "#GOP OR #Democrats OR #Politics OR #MAGA OR #ProtectDemocracy"
]
MIN_NEW_TWEETS = 200_000

# ========= UTIL =========
def daterange(start: datetime, end: datetime, step_hours: int) -> Iterable[tuple[datetime, datetime]]:
    cur = start
    delta = timedelta(hours=step_hours)
    while cur < end:
        nxt = min(cur + delta, end)
        yield cur, nxt
        cur = nxt

def ensure_csv_with_header(path: str, header: list[str]) -> bool:
    exists = os.path.isfile(path)
    if not exists:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            w.writerow(header)
    return exists

def rows_from_tweet(t, running_count: int) -> list:
    # prefer entities if available; fall back to regex as a safety
    try:
        tags = [h["text"] for h in (t.entities.get("hashtags") or [])]
    except Exception:
        tags = re.findall(r"#(\w+)", t.full_text or "")

    def nz(x):  # normalize None -> ""
        return "" if x is None else x

    return [
        str(t.id),
        running_count,
        nz(getattr(t.user, "id", "")),
        nz(getattr(t.user, "screen_name", getattr(t.user, "username", ""))),
        nz(t.user.name if t.user else ""),
        nz(t.full_text),
        nz(getattr(t, "created_at", "")),
        int(getattr(t, "retweet_count", 0) or 0),
        int(getattr(t, "favorite_count", 0) or 0),
        nz(getattr(t.user, "description", "")),
        int(getattr(t.user, "followers_count", 0) or 0),
        int(getattr(t.user, "following_count", 0) or 0),
        int(getattr(t, "reply_count", 0) or 0),
        nz(getattr(t.user, "location", "")),
        nz(getattr(t, "lang", "")),
        int(bool(getattr(t, "is_quote_status", False))),
        int(bool(getattr(t, "retweeted", False))),
        nz(getattr(t, "in_reply_to_status_id", "")),
        nz(getattr(t, "conversation_id", "")),
        "|".join(tags),
        int(bool(getattr(t.user, "verified", False))),
        nz(getattr(t.user, "created_at", "")),
        int(bool(getattr(t, "possibly_sensitive", False))),
        nz(getattr(t, "source", "")),
        nz(getattr(getattr(t, "place", None), "full_name", "")),
    ]

HEADER = [
    "tweet_id","row_num","user_id","user_handle","user_name","text","tweet_created_at",
    "retweets","likes","user_bio","followers","following","replies","user_location",
    "lang","is_quote","is_retweet","in_reply_to_status_id","conversation_id","hashtags",
    "user_verified","user_created_at","possibly_sensitive","source","place"
]

# ========= MAIN =========
async def search_window(client: Client, q: str, since: datetime, until: datetime, product: str):
    # twikit search_tweet expects 'since:' and 'until:' inside the query
    # format dates as YYYY-MM-DD (UTC) to match your original usage
    s = since.strftime("%Y-%m-%d")
    u = until.strftime("%Y-%m-%d")
    full_q = f"({q}) lang:{LANG} since:{s} until:{u}"

    tweets = await client.search_tweet(full_q, product=product)
    while True:
        if not tweets:
            break
        for t in tweets:
            yield t
        try:
            tweets = await tweets.next()
        except TooManyRequests as e:
            reset = datetime.fromtimestamp(e.rate_limit_reset, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            sleep_s = max(0, (reset - now).total_seconds()) + random.uniform(1.5, 4.0)
            print(f"[{now}] RL hit. Sleeping {sleep_s:.1f}s (until {reset}).")
            await asyncio.sleep(sleep_s)
            continue
        except Exception as ex:
            # mild backoff + retry a few times could be added here
            print(f"[{datetime.now(timezone.utc)}] paging error: {ex}. Breaking window.")
            break

async def main():
    # load existing ids to dedupe
    seen = set()
    total_rows = 0
    if os.path.isfile(OUTPUT):
        with open(OUTPUT, "r", encoding="utf-8", newline="") as f:
            r = csv.reader(f)
            next(r, None)
            for row in r:
                if row:
                    seen.add(row[0])
                    total_rows += 1

    ensure_csv_with_header(OUTPUT, HEADER)

    client = Client(language='en-US')
    client.load_cookies(COOKIES)

    new_rows = 0
    batch = []

    with open(OUTPUT, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)

        for since, until in daterange(START, END, WINDOW_HOURS):
            print(f"=== Window {since.date()} {since.hour:02d}:00 → {until.date()} {until.hour:02d}:00 ===")
            for shard in QUERY_SHARDS:
                for product in PRODUCTS:
                    # iterate a window+shard+product “triple”
                    async for t in search_window(client, shard, since, until, product):
                        tid = str(getattr(t, "id", ""))
                        if not tid or tid in seen:
                            continue
                        seen.add(tid)
                        total_rows += 1
                        new_rows += 1
                        batch.append(rows_from_tweet(t, total_rows))

                        if len(batch) >= BATCH_SIZE:
                            w.writerows(batch); batch.clear(); f.flush()
                            print(f"[{datetime.now(timezone.utc)}] wrote {new_rows} new (total {total_rows}).")

                        if new_rows >= MIN_NEW_TWEETS:
                            break
                    if new_rows >= MIN_NEW_TWEETS:
                        break
                if new_rows >= MIN_NEW_TWEETS:
                    break
            if new_rows >= MIN_NEW_TWEETS:
                break

        # flush remainder
        if batch:
            w.writerows(batch); f.flush()

    print(f"Done. New rows this run: {new_rows}. Total rows in CSV: {total_rows}.")

if __name__ == "__main__":
    asyncio.run(main())
