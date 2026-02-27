import praw
import pandas as pd
from datetime import datetime
import os
# === YOUR REDDIT API CREDENTIALS ===
reddit = praw.Reddit(
    client_id="mwIkGm3Yc6ND4OVT93drHA",
    client_secret="TqjJTqsh335k02Dh9Ves_YdWtuC3dA",
    username="Accomplished-Egg7656",  
    password=",zf)MVx3=c@S2Dy",
    user_agent="disinfo-research-bot"
)

# === CONFIGURATION ===
subreddits = [
    "The_Donald", 
    "Conservative", 
    "Libertarian", 
    "PoliticalHumor", 
    "ChapoTrapHouse", 
    "Progressive", 
    "Socialism", 
    "Gab", 
    "Truth Social",
    "politics",                  # Main U.S. politics subreddit (high volume)
    "conservative",              # Right-leaning perspectives
    "republican",                # Republican community
    "democrats",                 # Democratic community
    "Ask_Politics",              # Q&A format political discussion
    "PoliticalDiscussion",       # Moderated civil political discourse
    "uspolitics",                # U.S.-focused politics
    "election2024",              # Dedicated to 2024 election
    "WayOfTheBern",              # Left/progressive politics
    "TheMajorityReport",         # Media-leaning progressive
    "neoliberal",                # Market liberal / centrist discourse
    "EnoughTrumpSpam",           # Critical of Trump, shares breaking news
    "Keep_Track",                # Tracks Trump-related investigations
    "MarchAgainstTrump",         # Activist-focused community
    "TrumpCriticizesTrump",      # Ironic/satirical takes on Trump's statements
    "news",                      # General news (often includes election coverage)
    "worldnews",                 # Global view on U.S. elections
    "LateStageCapitalism",       # Strong left-leaning economic focus
    "Libertarian",               # U.S. libertarian perspectives
    "AskTrumpSupporters",        # Civil Q&A for Trump supporters
    "Americans",                 # Broad U.S. discussion
    "U_S_Politics",              # Backup or alt political subs
    "ModeratePolitics",          # Focus on centrist takes
]


keywords = [
    "MAGA", "Trump2024", "StopTheSteal", "BlueWave", "ElectionFraud", "Trump", "Biden", "election", "2024 election", "us elections", 
    "presidential election", "debate", "republican", "democrat", "gop",  "indictment", "rally", "vote", "ballot", "election interference"
]

start_date = datetime(2024, 8, 15).timestamp()
stop_date = datetime(2024, 12, 1).timestamp() 

max_posts_per_sub = 150000
output_file = "Elect2024Reddit.csv"

# === LOAD EXISTING IDs TO AVOID DUPLICATES ===
existing_post_ids = set()
existing_comment_ids = set()

if os.path.exists(output_file):
    df_existing = pd.read_csv(output_file, usecols=["Type", "Post ID", "Comment ID"], low_memory=False)
    existing_post_ids = set(df_existing[df_existing["Type"] == "Post"]["Post ID"].dropna())
    existing_comment_ids = set(df_existing[df_existing["Type"] == "Comment"]["Comment ID"].dropna())
    print(f"🧠 Loaded {len(existing_post_ids)} existing posts and {len(existing_comment_ids)} existing comments.\n")

# === SCRAPE ===
data = []
row_count = 0

for sub in subreddits:
    try:
        subreddit = reddit.subreddit(sub)
        subreddit.id  # Trigger fetch to ensure subreddit exists
        print(f"🔍 Searching r/{sub}")
    except Exception as e:
        print(f"⚠️ Skipping r/{sub} — subreddit not found or inaccessible ({e})")
        continue

    query = " OR ".join(keywords)
    for post in subreddit.search(query, sort='new', limit=max_posts_per_sub):
        if post.created_utc < start_date or post.created_utc > stop_date or post.id in existing_post_ids:
            continue


        row_count += 1
        post_info = {
            "Row Count": row_count,
            "Type": "Post",
            "Post ID": post.id,
            "Comment ID": None,
            "Parent Post ID": post.id,
            "Subreddit": sub,
            "Title": post.title,
            "Text": post.selftext,
            "Author": str(post.author),
            "Created UTC": post.created_utc,
            "Created Date": datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            "Score": post.score,
            "Upvote Ratio": post.upvote_ratio,
            "URL": post.url,
            "Permalink": f"https://reddit.com{post.permalink}",
            "Num Comments": post.num_comments,
            "Is Self Post": post.is_self,
            "Is Original Content": post.is_original_content,
            "Is Video": post.is_video,
            "Is NSFW": post.over_18,
            "Domain": post.domain,
            "Flair": post.link_flair_text,
       
        }
        data.append(post_info)

        # === SCRAPE COMMENTS ===
        post.comments.replace_more(limit=0)
        for comment in post.comments.list():
            if len(comment.body.split()) <= 25 or comment.id in existing_comment_ids:
                continue

            row_count += 1
            data.append({
                "Row Count": row_count,
                "Type": "Comment",
                "Post ID": post.id,
                "Comment ID": comment.id,
                "Parent Post ID": post.id,
                "Subreddit": sub,
                "Title": post.title,
                "Text": comment.body,
                "Author": str(comment.author),
                "Created UTC": comment.created_utc,
                "Created Date": datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                "Score": comment.score,
                "Upvote Ratio": None,
                "URL": f"https://reddit.com{comment.permalink}",
                "Permalink": f"https://reddit.com{comment.permalink}",
                "Num Comments": None,
                "Is Self Post": None,
                "Is Original Content": None,
                "Is Video": None,
                "Is NSFW": None,
                "Domain": None,
                "Flair": None,
              
            })

# === SAVE ===
df_new = pd.DataFrame(data)

if df_new.empty:
    print("📭 No new posts or comments to save.")
else:
    if os.path.exists(output_file):
        df_new.to_csv(output_file, mode='a', header=False, index=False)
    else:
        df_new.to_csv(output_file, index=False)
    print(f"\n✅ Appended {len(df_new)} new rows to {output_file}")