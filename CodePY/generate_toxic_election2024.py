import os
import csv
import argparse
import time
import random
import asyncio
from typing import List, Set

# Configuration
OUTPUT_FILE = "synthetic_election2024.csv"
BATCH_SIZE = 50 
MIN_WORDS = 6

# ==========================================
# MOCK GENERATOR (Template/Grammar Based)
# ==========================================
class MockGenerator:
    """
    Generates synthetic political posts using sophisticated combinatorial templates.
    Designed for high diversity and variable length without an LLM.
    """
    def __init__(self):
        self.personas = ["maga", "progressive", "chaos"]
        
        # --- EXPANDED VOCABULARY ---
        self.vocab = {
            "maga": {
                "entity": [
                    "Sleepy Joe", "The Democrats", "Liberal Elites", "The Media", "Hunter", 
                    "Soros", "Deep State", "RINO GOP", "Charlie Kirk", "Trump", "The Left",
                    "AOC", "Pelosi", "Fauci", "Big Tech", "Hollywood"
                ],
                "action_pres": [
                    "is destroying America", "hates freedom", "wants to brainwash kids", 
                    "is selling us out to China", "is plotting against us", "is weaponizing the DOJ",
                    "is ignoring the border", "is mocking the Constitution", "is banning the truth",
                    "is stealing our country"
                ],
                "action_past": [
                    "stole the election", "lied about everything", "destroyed the economy",
                    "betrayed the working class", "rigged the system", "indoctrinated our children",
                    "opened the floodgates", "sold out to globalists"
                ],
                "noun_value": [
                    "freedom", "the Constitution", "our borders", "real Americans", "the truth", 
                    "family values", "God", "the flag", "law and order", "integrity", "the future"
                ],
                "noun_insult": [
                    "clowns", "traitors", "communists", "socialists", "sheep", "NPCs", 
                    "groomers", "globalists", "liars", "frauds", "cowards", "losers", "tyrants"
                ],
                "adj_neg": [
                    "corrupt", "fake", "disgusting", "pathetic", "weak", "un-American", 
                    "radical", "insane", "evil", "senile", "hypocritical", "dangerous"
                ],
                "hashtag": [
                    "#MAGA", "#Trump2024", "#AmericaFirst", "#SaveAmerica", "#StopTheSteal", 
                    "#Groyper", "#RedWave", "#Trump", "#VoterFraud", "#Patriots", "#2024", 
                    "#BidenCrimeFamily", "#WakeUpAmerica"
                ],
                "slang": [
                    "based", "cringe", "woke mind virus", "cope harder", "fake news", 
                    "TDS", "clown world", "soy", "beta"
                ],
                "starter": [
                    "Just realized", "Honestly,", "Can't believe this.", "Breaking:", 
                    "It's simple:", "Wake up:", "Imagine thinking", "News flash:", 
                    "Let that sink in.", "Make no mistake:", "Here we go again."
                ]
            },
            "progressive": {
                "entity": [
                    "The GOP", "Trump", "Elon", "Corporate lobbyists", "Fascists", 
                    "SCOTUS", "Billionaires", "Manchin", "DeSantis", "The Right", 
                    "Oil companies", "Police unions", "Fox News"
                ],
                "action_pres": [
                    "is destroying the planet", "hates women", "supports genocide", 
                    "wants to control our bodies", "is fueling hate", "profits from suffering",
                    "is attacking trans rights", "is enabling violence", "is protecting the rich",
                    "is stripping away rights"
                ],
                "action_past": [
                    "overturned Roe", "blocked progress", "stole the courts", "incited an insurrection",
                    "gutted voting rights", "ignored the science", "cut taxes for the rich",
                    "poisoned our water"
                ],
                "noun_value": [
                    "human rights", "democracy", "choice", "the climate", "equity", 
                    "justice", "the working class", "trans rights", "bodily autonomy", 
                    "the planet", "voting rights"
                ],
                "noun_insult": [
                    "bootlickers", "fascists", "racists", "bigots", "Nazis", "incels", 
                    "capitalist pigs", "misogynists", "monsters", "idiots", "oppressors"
                ],
                "adj_neg": [
                    "toxic", "violent", "hateful", "bigoted", "racist", "sexist", 
                    "dystopian", "horrifying", "ignorant", "selfish", "out of touch"
                ],
                "hashtag": [
                    "#BLM", "#TaxTheRich", "#GreenNewDeal", "#DefundThePolice", "#MedicareForAll", 
                    "#RoevWade", "#GeneralStrike", "#TransRights", "#Antifa", "#EatTheRich", 
                    "#VoteBlue", "#ClimateEmergency"
                ],
                "slang": [
                    "trash", "literally violent", "yikes", "disgusting", "normalize", 
                    "gaslighting", "dog whistle", "bad faith", "strawman", "red flag"
                ],
                "starter": [
                    "Daily reminder:", "Unpopular opinion:", "I'm so tired of", 
                    "Why is nobody talking about", "We need to talk about", 
                    "Seriously?", "Just a reminder:", "PSA:", "I can't even."
                ]
            },
            "chaos": {
                "entity": [
                    "Both parties", "The government", "Politicians", "The system", 
                    "Washington", "The elites", "The CIA", "The Fed", "Big Pharma", 
                    "The military industrial complex", "The simulation"
                ],
                "action_pres": [
                    "don't care about us", "are lying to you", "are watching us", 
                    "want us fighting", "are printing fake money", "are poisoning the food",
                    "are distracting you", "are acting in a play", "are puppets"
                ],
                "action_past": [
                    "orchestrated the crisis", "planned this for years", "faked the data",
                    "crashed the economy", "started the war", "engineered the virus"
                ],
                "noun_value": [
                    "the truth", "our money", "privacy", "peace", "reality", 
                    "sovereignty", "consciousness", "our minds"
                ],
                "noun_insult": [
                    "liars", "parasites", "psychopaths", "puppets", "demons", 
                    "lizards", "actors", "criminals", "brainwashed", "sheep"
                ],
                "adj_neg": [
                    "fake", "rigged", "evil", "scripted", "disturbing", "predictable", 
                    "insane", "satanic", "artificial"
                ],
                "hashtag": [
                    "#EndTheFed", "#Corruption", "#ClownWorld", "#Collapse", "#WW3", 
                    "#CivilWar", "#TheGreatReset", "#WakeUp", "#Truth", "#Matrix"
                ],
                "slang": [
                    "psyop", "fed", "glowie", "matrix", "simulation", "NPC", 
                    "false flag", "controlled opposition", "bluepilled"
                ],
                "starter": [
                    "POV:", "Hypothetically,", "Hot take:", "Prediction:", 
                    "If you think this is real,", "Question everything.", 
                    "They don't want you to know this.", "Open your eyes."
                ]
            }
        }
        
        # --- SENTENCE STRUCTURES ---
        # {v} = from current persona vocab
        # {o} = from OTHER persona vocab (for contrast/blame)
        self.structures = [
            # SIMPLE AGGRESSION
            "{starter} {entity} {action_pres}. Absolute {noun_insult}. {hashtag}",
            "{entity} {action_past}. Now they want us to believe {noun_value}? {adj_neg}.",
            
            # RHETORICAL QUESTION
            "Why does {entity} hate {noun_value}? Is it because they are {adj_neg} {noun_insult}? {hashtag}",
            "Can someone explain why {entity} {action_pres}? {slang}.",
            
            # CONDITIONAL / WARNING
            "If we don't save {noun_value}, {entity} will win. Don't let these {noun_insult} take over.",
            "Imagine a world where {entity} runs everything. That is {adj_neg}. {hashtag} {hashtag}",
            
            # DOUBLE ATTACK (Longer)
            "{entity} {action_past} and {entity} {action_pres}. They are all {noun_insult}. We need {noun_value}!",
            "It's not just {entity}. It's {entity} too. All of them are {adj_neg}. {hashtag}",
            
            # OBSERVATION + SLANG
            "Watching {entity} {action_pres} is so {slang}. They are {adj_neg}.",
            "{entity}? {slang}. {entity}? {noun_insult}. {hashtag}",
            
            # "TRUTH" REVEAL
            "They won't tell you this, but {entity} {action_past}. The {noun_insult} are lying. {hashtag}",
            "Everyone knows {entity} {action_pres}. Stop gaslighting us.",
            
            # COMPARISON
            "Unlike {entity}, we care about {noun_value}. They just want to be {noun_insult}.",
            "You think {entity} is bad? Wait until you see {entity} {action_pres}. {hashtag}",
            
            # RANT (Multi-sentence)
            "I am so sick of this. {entity} {action_pres}. Then {entity} {action_past}. It never ends. We need {noun_value} or it's over. {hashtag} {hashtag}",
            "{starter} {entity} is {adj_neg}. They {action_past}. They {action_pres}. And they call us {noun_insult}? {slang}.",
            "Listen. {entity} {action_pres}. It is {adj_neg}. If you support them, you are a {noun_insult}. Period. {hashtag}",
        ]

    def _get_word(self, key, vocab):
        """Safely get a random word from a specific vocab dict."""
        if key not in vocab: return "THING"
        return random.choice(vocab[key])

    def generate_one(self) -> str:
        # 1. Pick a persona
        persona_key = random.choice(self.personas)
        vocab = self.vocab[persona_key]
        
        # 2. Pick a secondary persona for contrast (sometimes)
        other_key = random.choice([p for p in self.personas if p != persona_key])
        other_vocab = self.vocab[other_key]

        # 3. Pick a structure
        structure = random.choice(self.structures)
        
        # 4. Fill placeholders
        # We need a custom formatter because standard .format() can't handle random selections per token easily
        # nor the logic of "current persona" vs "other persona".
        # So we'll do a simple token replacement loop.
        
        words = structure.split()
        final_words = []
        
        for word in words:
            clean_word = word.strip(".,?!")
            token = None
            
            # Check if it's a placeholder like {entity}
            if word.startswith("{") and "}" in word:
                # Extract key, e.g. "{entity}" -> "entity"
                token_key = word.split("{")[1].split("}")[0]
                
                # Determine source vocab (default to current persona)
                source = vocab
                
                # If specific complex logic needed, handle here. 
                # For now, we rely on the vocab keys being unique enough or just random.
                # To add variety, 20% chance to pull an ENTITY from the 'other' side if it fits context?
                # Actually, let's keep it simple: The templates don't specify {o_entity}, 
                # but we can randomly swap source for entities to create "blame" dynamics.
                
                replacement = self._get_word(token_key, source)
                
                # Apply the punctuation back
                prefix = word[:word.find("{")]
                suffix = word[word.find("}")+1:]
                final_words.append(prefix + replacement + suffix)
            else:
                final_words.append(word)
                
        text = " ".join(final_words)

        # 5. Post-processing for variety
        # Random CAPS
        if random.random() < 0.05:
            text = text.upper()
        
        # Random punctuation changes
        r = random.random()
        if r < 0.1: text = text.replace(".", "!!!")
        elif r < 0.15: text = text.lower()
        
        return text

    async def generate_batch(self, batch_size: int) -> List[str]:
        # Generate 3x requested to ensure unique set after filtering
        raw = [self.generate_one() for _ in range(batch_size * 3)]
        return list(set(raw))[:batch_size]


# ==========================================
# OPENAI GENERATOR
# ==========================================
class OpenAIGenerator:
    def __init__(self, api_key, model="gpt-4o-mini"):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = """You are a specialized data synthesizer for research... (condensed for brevity) ... 
        Generate realistic, toxic/inflammatory 2024 election posts. 
        Personas: MAGA (Charlie Kirk, StopTheSteal), Progressive (AOC, BLM), Anti-Establishment.
        Mix rhetorical styles: sarcasm, hyperbole, conspiracy, slang.
        """

    async def generate_batch(self, batch_size: int) -> List[str]:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Generate {batch_size} unique, distinct synthetic tweets. One per line. No numbering."}
                ],
                temperature=0.9,
                max_tokens=2000,
            )
            content = response.choices[0].message.content
            return [line.strip() for line in content.split('\n') if line.strip()]
        except Exception as e:
            print(f"Error generating batch: {e}")
            return []


# ==========================================
# MAIN
# ==========================================
async def main():
    parser = argparse.ArgumentParser(description="Generate synthetic election data.")
    parser.add_argument("--num-tweets", type=int, default=1000)
    parser.add_argument("--api-key", type=str, default=None)
    parser.add_argument("--mode", type=str, choices=["openai", "mock"], default="mock", 
                      help="Use 'openai' for LLM or 'mock' for free local generation")
    args = parser.parse_args()

    # Determine mode
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    mode = args.mode
    
    if api_key:
        mode = "openai"
        print("API Key found. Using OpenAI mode.")
    else:
        print("No API Key found. Using Mock/Template mode (Free).")
        mode = "mock"

    # Initialize Generator
    if mode == "openai":
        generator = OpenAIGenerator(api_key)
    else:
        generator = MockGenerator()

    # Load existing
    existing_texts: Set[str] = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if headers and "text" in headers:
                col_idx = headers.index("text")
                for row in reader:
                    if len(row) > col_idx:
                        existing_texts.add(row[col_idx])
    
    # Init file
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["text"])

    print(f"Target: {args.num_tweets} tweets.")
    print(f"Existing: {len(existing_texts)} tweets.")
    
    current_count = len(existing_texts)
    
    while current_count < args.num_tweets:
        # Increase batch size for mock since it's fast
        current_batch_size = BATCH_SIZE if mode == "openai" else 5000
        
        batch_lines = await generator.generate_batch(current_batch_size)
        
        new_tweets = []
        for line in batch_lines:
            line = line.strip().strip('"')
            if len(line.split()) > MIN_WORDS and line not in existing_texts:
                existing_texts.add(line)
                new_tweets.append([line])
        
        if new_tweets:
            with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(new_tweets)
            current_count += len(new_tweets)
            print(f"Added {len(new_tweets)} new tweets. Total: {current_count}")
        else:
            print("Dupes found, retrying...")
        
        if mode == "openai":
            time.sleep(1)

    print(f"Done! Generated {current_count} tweets in {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
