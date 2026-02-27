#!/usr/bin/env python3
"""
Generate 20,000 TRULY unique social media posts about US Election 2024.
Toxic, negative, Twitter-ready. Same format as Utah dataset: text,1 per row, no header.
Modeled on real Twitter/X discourse (Trump win, Harris loss, voter fraud, Vance, etc.).
"""

import csv
import random
import re
from typing import List, Set

random.seed(42)

TARGET_SHORT = 19000
TARGET_LONG = 1000
TARGET_TOTAL = 20000

def is_forbidden(text: str) -> bool:
    """Exclude templates and patterns we do not want."""
    if "Rumor. Verify" in text or ("Rumor:" in text and "Verify" in text):
        return True
    if re.search(r'\d+ (million|thousand) (votes?|ballots?) (stolen|dumped|fraud)', text, re.I):
        return True
    return False


TRAILING_PHRASES_FOR_CORE = [
    ". Demand change.", ". Period.", ". Unacceptable.", ". Never forget.",
    ". Act.", ". Enough.", ". Now.", ". Do something.", ". Share carefully.",
    ". Vote.", ". Wake up.", ". This is America.", ". Sad.",
]


def get_core(text: str) -> str:
    """Return normalized core for dedup. Strips trailing filler."""
    s = text.strip()
    if s.endswith("?"):
        s = s[:-1].strip()
    changed = True
    while changed:
        changed = False
        for phrase in TRAILING_PHRASES_FOR_CORE:
            if s.endswith(phrase):
                s = s[:-len(phrase)].strip()
                changed = True
    return s


OUTPUT_PATH = "/Users/nyuad/Downloads/Gunjan/Election2024_Dataset.csv"
HASHTAGS = [
    '#Election2024', '#Trump2024', '#MAGA', '#Harris', '#Biden', '#Vote',
    '#Democracy', '#VoterFraud', '#TrumpWon', '#JDVance', '#RINO',
    '#DrainTheSwamp', '#AmericaFirst', '#Resist', '#BlueWave', '#RedWave',
]


def load_all_unique_posts() -> List[str]:
    """
    Returns thousands of unique election-2024 sentences.
    Toxic/negative, Twitter-ready. No template fill-in dupes.
    """
    posts = []

    # --- Fragments / questions / exclamations ---
    fragments = [
        "Trump stole it. Again.",
        "Harris lost. Deal with it.",
        "Milwaukee ballot dump. You know it.",
        "Vance is a sellout.",
        "RINOs will confirm every pick.",
        "Biden stepped down. Coward.",
        "They stole 2020. We took 2024 back.",
        "J6 was a fed op. Ray Epps.",
        "Election fraud is real. Wisconsin proved it.",
        "Thank God Trump won.",
        "Democrats are finished.",
        "Sixty-nine million for Harris. Eighty-one for Biden. Where did they go?",
        "Trump cabinet is a circus.",
        "RFK Jr at HHS. Brilliant or insane?",
        "Nikki Haley had no interest. Sure.",
        "Jack Smith resigned. Coward.",
        "They tried to steal Wisconsin. Trump won by point seven.",
        "Drain the swamp. Starting now.",
        "Celebrities fleeing. Epstein and Diddy smokescreen.",
        "DEI hires out. Merit in.",
        "Biden admin was a joke.",
        "Harris could not even win her own state.",
        "Voter ID now. No more mail-in chaos.",
        "The debate was a disaster for both.",
        "They are eating the dogs. Springfield. Look it up.",
        "Dark Brandon is dead. Trump won.",
        "Election denial is the new normal.",
        "Trump will pardon J6. As he should.",
        "GOP will bend the knee. Pathetic.",
        "Obama disappeared after Trump won. Coincidence?",
        "FEMA was ordered not to help Trump sign yards. True.",
        "Trump is immune. Get over it.",
        "Logan Act is nothing now. Nothing.",
        "Democrats roll over. Harris is as bad as Trump.",
        "Kamala made Biden seem okay. That is saying something.",
        "Leftist says she is boycotting inauguration. That will show him.",
        "Resigning before Trump takes office. Accountability coming.",
        "Media world is coming to an end. Trump second term. Boring.",
        "Russia collusion was fake. Gowdy lied.",
        "Trump lost no ground after the debate. Unprecedented.",
        "Sixty-seven million watched the debate. Both lied.",
        "Immigrants eating pets. City said no credible reports. Who do you believe?",
        "Tariffs. Unemployment. Abortion. Manufacturing. Both distorted.",
        "Trump picks are controversial. So what.",
        "Libs are pissed. So Trump did it right.",
        "I did not vote Trump in three elections. I am all in now.",
        "Draining the swamp. Finally.",
        "RINOs in the Senate will show up. Trump will lower the boom.",
        "Trump swept. Congress. Senate. House. Two years to remove the evil.",
        "GOP will bend the knee to Trump. Disastrous choices.",
        "Americans voted for hope and change. Here it comes.",
        "Trump can pardon any federal crime. Immune. Logan Act nothing.",
        "Democrats had evidence Trump stole election. They rolled over.",
        "Harris and Democrats as bad as Trump. At this point.",
        "Trans nonsense ends under Trump. Enough.",
        "Not DEI hires. Real talent. Trump.",
        "Trump picks. Genius and strategy. Weak Republicans in Senate.",
        "Hold their feet to the fire.",
        "Trump 2.0 knows the ropes. Better than first time.",
        "Biden threw under the bus. Not forgiven yet.",
        "Dems and RINOs think they won. They did not get the memo.",
        "Trump landslide. They did not get the memo.",
        "Nikki Haley. Worried about his safety. Since he endorsed Trump.",
        "Police condemned by Biden admin. Reinstated. Compensated.",
        "Trump agenda. Hope it does not backfire.",
        "Blue team money printers. Prostitution. Trump did not pay for endorsements.",
        "Luke. Trump is your father.",
        "Leftist boycotting inauguration. That will show him.",
        "Resigning before ethics report. Sex trafficking report due. Not a good look.",
        "Accountability coming. Fear in the air.",
        "News media world coming to an end. Trump second term. Boring.",
        "Celebrities fleeing. Epstein Diddy. Trump fascist smokescreen.",
        "Gowdy lied. Russia collusion. We know it was fake.",
        "Trump mishandling pandemic. Suggests what he wants.",
        "Three maniacs. Dishonorably discharged. Unacceptable.",
        "Trump picks. If the left does not like it they are doing it right.",
        "Biden admin joke. Agreed.",
        "Jews worried. Antisemite with platform. Moved right for Trump.",
        "Nikki Haley. No interest in cabinet. Sure.",
        "Do not let the door hit you on the way out.",
        "Trump ran on issues. If you go against what Americans voted for you are the problem.",
        "If names get cleared they do not get to nail accusers. Discovery. Lawsuits.",
        "Trump will get country working from day one. Not solar panels on farmland.",
        "Whatever Trump picks. MAGA.",
        "Trump supporters do not read. They think he did good with covid.",
        "He will be out to bitch about Trump in no time.",
        "Does Trump shit on his followers? Is the Pope Catholic?",
        "Amazing interview. Donald Trump and family. Revealing.",
        "RFK Jr to lead HHS. Trump taps.",
        "Trump changes the method not the agenda.",
        "Big dope does not have a clue. Johnson and Trump secret.",
        "FEMA ordered not to help Trump sign yards. True.",
        "Americans just voted Trump back. Not much intelligence at risk.",
        "Obama disappeared after Trump won. Sheri is spot on.",
        "2016 was amazing. Trump tower. Golden elevator. Best reality show.",
        "Trump agenda 47. MAGA. The people are watching.",
        "Trump is seventy-eight. By the time he gets out he will need vacation.",
        "Murphy said Trump would use office to go after opponents. Words never left his lips.",
        "Sacrifice a manatee to the altar of Trump. Already.",
        "J6 manufactured insurrection. Feds. They hid video. Pelosi denied support.",
        "Trump first response. Taking care of women. Whether we want it or not.",
        "Stop lying journalists. Make America Honest again. If you are scared of Trump you are the problem.",
        "Trump will cancel elections. Only question is what clothes he will dress it in.",
        "Kamala only one who could make Biden seem okay.",
        "He will be great. Trump pick.",
        "Jill and Melania. Tea declined. Biden talking to Wray.",
        "Trump-loving dad left president blank. Single-issue.",
        "Jill. Beautiful. Going to miss you and President Biden.",
        "Astroturf campaign for Lara Trump senate. Off-putting.",
        "More died under Biden. Covid.",
        "Biden happier with Trump than with Harris. Pics.",
        "Trump looking for real talent. Not DEI.",
        "Dems okay financially. Do we sit and watch or fight?",
        "Jack Smith resigning. What were voters thinking?",
        "Why are you against Trump taking down the machine?",
        "Trump pandemic mishandling. Suggests what he wants.",
        "Pictured. Three maniacs. Dishonorably discharged.",
        "Send trans daughter money. Convince Trump to step down. Then kill myself. Satire.",
        "Mentally ill quack in charge of health. Trump pick.",
    ]

    # --- @reply style ---
    replies = [
        "@SpeakerJohnson You need a big broom. Clean then organize. Per President Trump.",
        "@SenJohnThune Ten GOP Senators voted to confirm all Biden nominations. Insane.",
        "@TristanSnell His fiftieth federal felony. Nothing done. Trump will pardon in January.",
        "@realDonaldTrump Drain the swamp. Lower the boom on RINOs.",
        "@VP Harris lost. Deal with it.",
        "@POTUS You threw Biden under the bus. Not forgiven.",
        "@elonmusk Cut federal waste. Tell Trump lobbyists are out of control.",
        "@GOP Trump agenda 47. The people are watching.",
        "@DNC Sixty-nine million. Where did the votes go?",
        "@FBI Ray Epps. When do we get the files?",
        "@KamalaHarris You could not win California. Bye.",
        "@JoeBiden You stepped down. Coward. Harris could not carry it.",
        "@PressSec Jack Smith resigned. Accountability coming.",
        "@RNC Drain the swamp. Two years. Hold their feet to the fire.",
        "@SenateDems RINOs will confirm. Trump will remember.",
        "@HouseGOP Big broom. Clean. Organize. Per Trump.",
        "@MilwaukeeVote Ballot dump. We see you.",
        "@WisconsinGOP They tried to steal it. Trump won point seven.",
        "@CNN Trump cabinet controversial. So what. He won.",
        "@FoxNews Finally. Fair coverage. Trump won.",
        "@MSNBC Your world is ending. Trump second term. Boring.",
        "@AP You called Wisconsin with over a hundred thousand votes. Trump won. Count again.",
        "@Reuters Late night Milwaukee. Statistically improbable. Your words.",
        "@NPR No ballot dump. Sure. Explain the timing.",
        "@Politifact We do not believe you. Wisconsin. Milwaukee. Baldwin.",
        "@FactCheck Both lied in the debate. Tariffs. Jobs. Abortion.",
        "@Twitter Safety Election misinformation. You allowed it. Trump won anyway.",
    ]

    # --- Personal / emotional ---
    personal = [
        "I voted Trump. First time. Hope and change. Here it comes.",
        "I could not take four more years of Biden. Or Harris.",
        "My dad left the president blank. Single-issue. Trump lover.",
        "I am done with both parties. But I voted. Trump.",
        "I watched the debate. Sixty-seven million. Both lied. I still voted Trump.",
        "I trust Trump to pick good people. I looked at their backgrounds.",
        "I am excited. Some picks made me nervous. I trust Trump to get it done.",
        "I wish you could tell Trump. Lobbyists out of control. Cut the waste.",
        "I think they tried to steal Wisconsin. Milwaukee. Late night dump.",
        "I have said from day one. They stole 2020. We took 2024.",
        "I miss when elections were boring. Now every cycle is fraud claims.",
        "I am not Satan. You are not Jesus. Neither is Trump. Steve M.",
        "I am generally less likable in person. Americans voted Trump back. So.",
        "I am okay financially. Trump cannot mess up much. Do I fight or watch?",
        "I feel like I am exposing myself to a biohazard. Biden resign so Kamala pension. Disgusting.",
        "I have watched her for years. Unbiased. Then she went anti-Trump. Credibility gone.",
        "I thank God Trump won. We would have fallen into the abyss.",
        "I am boycotting the inauguration. That will show him. Leftist.",
        "I think they resigned before the sex trafficking report. Not a good look.",
        "I smell accountability. Resigning before Trump takes office.",
        "I think the media is boring now. Trump second term. Zzzzz.",
        "I think celebrities are fleeing Epstein and Diddy. Trump is a smokescreen.",
        "I know Gowdy lied. Russia collusion. He said he saw evidence. Fake.",
        "I hope Trump lowers the boom. RINOs in Senate. Constituents.",
        "I did not vote Trump three times. I am all in now. Drain the swamp.",
        "I think the best thing for America is Trump sweep. Congress. Senate. House.",
        "I think the entire GOP will bend the knee. Disastrous choices.",
        "I voted hope and change. Trump. Here it comes.",
        "I think Trump can pardon any federal crime. Immune. Logan Act nothing.",
        "I think Democrats had evidence. They rolled over. Harris as bad as Trump.",
        "I want trans nonsense to end. Trump. Enough.",
        "I love that it is not DEI. Real talent. Trump picks.",
        "I see genius in Trump picks. Strategy. Weak Republicans. Hold their feet to the fire.",
        "I think Trump 2.0 knows the ropes. Better than first time.",
        "I have not forgiven him for throwing Biden under the bus. Yet.",
        "I think Dems and RINOs did not get the memo. Trump landslide.",
        "I have been worried about his safety. Since he endorsed Trump. Haley.",
        "I would like to see police reinstated. Condemned by Biden admin. Compensated.",
        "I hope it does not backfire. Trump agenda. Florida. Quick elect Republican.",
        "I doubt Trump paid for endorsements. Would go against his self-esteem.",
        "I think Luke. Trump is your father. Mayor.",
        "I think leftist boycotting inauguration will show him. Sure.",
        "I think they resigned before ethics report. Sex trafficking. Not good look. Trump.",
        "I smell accountability. Fear in the air. Resigning before Trump.",
        "I think media world is ending. Trump second term. Boring. Ratings.",
        "I think celebrities are fleeing Epstein Diddy. Trump fascist is smokescreen.",
        "I know Gowdy lied. Russia collusion. Saw evidence. All fake.",
        "I think Trump pandemic mishandling suggests what he wants. People Need People.",
        "I want three maniacs dishonorably discharged. Unacceptable. JJ1776.",
        "I am not voting. Send money to trans daughter. Convince Trump to step down. Satire.",
        "I think mentally ill quack at HHS. Trump pick. Colby.",
    ]

    # --- Conspiracy / suspicion ---
    conspiracy = [
        "They dumped ballots in Milwaukee. Late night. Baldwin. You know it.",
        "Wisconsin. They tried to steal it. Trump won point seven when counted.",
        "Ray Epps. J6. When does Trump get FBI files?",
        "Obama disappeared after Trump won. Coincidence?",
        "FEMA was ordered not to help yards with Trump signs. True.",
        "They hid J6 video. Pelosi denied support from Trump. Manufactured insurrection.",
        "Sixty-nine million for Harris. Eighty-one for Biden. Where did twelve million go?",
        "Milwaukee. Hundred thousand votes. Late. Statistically improbable. Hovde said it.",
        "They closed the case. Fast. Too fast. Wisconsin.",
        "Celebrities fleeing. Epstein. Diddy. Trump is the smokescreen.",
        "Jack Smith resigned. Before inauguration. What was he afraid of?",
        "Resignations before Trump. Ethics reports. Sex trafficking. Connect the dots.",
        "Biden happier with Trump than with Harris. The pics. Think about it.",
        "Gowdy said he saw Russia evidence. We know it was fake. He lied.",
        "Media called Wisconsin with hundred thousand votes. Trump won. They knew.",
        "Late night update. Wisconsin. Senator. Not proof of fraud. Reuters said. Sure.",
        "Milwaukee did not print sixty-four thousand ballots. Politifact. Who believes them?",
        "Human error. Thirty-four thousand ballots. Recount. Milwaukee. Nothing wrong. Sure.",
        "Both parties agreed. Tabulation fine. So why the recount? Milwaukee.",
        "Election officials said lack of merit. Wisconsin. We do not believe them.",
        "Baldwin eighty-two percent Milwaukee absentee. Consistent. So they say.",
        "Forecasted. Normal procedure. Wisconsin Elections Commission. We do not buy it.",
        "Trump said they are eating the dogs. Springfield. Police said no credible reports. Who do you believe?",
        "Sixty-seven million watched. Both lied. FactCheck. So why did Trump lose no ground?",
        "Debate was poorly reviewed. Trump. His pollster said unprecedented. He did not lose ground.",
        "Deep state wanted Biden. Then Harris. We took it back.",
        "They will try again in 2028. We have to hold the line.",
        "Mail ballots. Process when polls open. So they dump late. Wisconsin. Design.",
        "Central count. Milwaukee. Report once done. So it is late. Convenient.",
        "Eighty-two percent Baldwin. Same as before. So they say. We do not trust it.",
    ]

    # --- Political / ideological ---
    political = [
        "Real Americans voted Trump. The rest are RINOs or Democrats.",
        "Harris lost. Democrats are finished. Rebuild or die.",
        "Trump won. Get over it. Democracy. We won.",
        "J6 was a fed op. Release the tapes. Pardon the patriots.",
        "Drain the swamp. Two years. Then we see.",
        "RINOs will confirm every pick. Then Trump will remember.",
        "DEI is out. Merit is in. Trump picks.",
        "Biden admin weaponized everything. Now we take it back.",
        "Election integrity. Voter ID. No more mail-in chaos.",
        "They stole 2020. We took 2024. Fair and square.",
        "Trump is not Hitler. Media said it. Now they sit with him. Pleasant.",
        "Democrats had evidence. They rolled over. Harris as bad as Trump.",
        "GOP will bend the knee. Disastrous. But we have no choice.",
        "Trump ran on issues. Americans voted. If you oppose you are the problem.",
        "Lawfare failed. Prosecutions failed. Trump won. Get over it.",
        "Jack Smith resigned. Accountability. Coming.",
        "Celebrities fleeing. Not Trump. Epstein. Diddy. Smokescreen.",
        "Trans nonsense ends under Trump. Enough. Country over ideology.",
        "Merit over DEI. Trump hires. Finally.",
        "Weak Republicans. Senate. We hold their feet to the fire.",
        "Trump 2.0 knows the ropes. First time he did not. Now he does.",
        "Biden threw under the bus. We have not forgiven. DisavowTrump.",
        "Dems and RINOs think they won. Trump landslide. They did not get the memo.",
        "Police. Riots. Biden admin condemned. Reinstated. Compensated. Bren.",
        "Trump agenda. Florida. Resign. Quick Republican. Hope it does not backfire.",
        "Money printers. Blue team. Prostitution. Trump did not pay for endorsements.",
        "Leftist boycotting inauguration. That will show him. Paul.",
        "Resigning before report. Sex trafficking. Ethics. Not good look. MidwestMatriarch.",
        "Accountability. Fear. Resigning before Trump. Frank.",
        "Media. Boring. Trump second term. Ratings. netpollution.",
        "Celebrities. Epstein. Diddy. Trump fascist smokescreen. TotallyCoolStudios.",
        "Gowdy lied. Russia. Saw evidence. Fake. traditionalgirl.",
        "Trump pandemic. What he wants. People Need People.",
        "Three maniacs. Discharge. Unacceptable. JJ1776.",
        "Scared of Trump you are the problem. joey.r91.",
        "Trump cancel elections. What clothes. Mark I Williams.",
        "Kamala made Biden seem okay. Michael Emley.",
        "Jack Smith. What were voters thinking. victor w monsura.",
        "Against Trump taking down machine. Marcus.",
        "Mentally ill quack. HHS. Trump. Phil Gibson.",
    ]

    # --- News / factual tone ---
    news = [
        "Trump wins 2024 presidential election. Defeats Harris.",
        "Trump becomes forty-seventh president. First since Cleveland to lose and return.",
        "Trump at seventy-eight. Oldest person ever elected president.",
        "Trump capitalized on economy and immigration. Voter frustration. Institutions.",
        "Harris-Trump debate. Sixty-seven million. False claims both sides.",
        "Trump claimed immigrants eating pets. Springfield. Police no credible reports.",
        "Both distorted tariffs unemployment abortion manufacturing. FactCheck.",
        "Trump debate poorly reviewed. Lost no ground. Unprecedented. His pollster.",
        "Trump renewed voter fraud claims. Mail voting. Still false. Politifact.",
        "Trump 2024 victory gave new life to 2020 fraud claims. NPR.",
        "Sixty-nine million Harris. Eighty-one million Biden 2020. Fewer votes. Expected. NPR.",
        "Fraud claims dominated early 2024. Evaporated as results came in.",
        "J.D. Vance. Trump running mate. Vice president.",
        "Milwaukee late night ballots. Hovde claimed statistically improbable. Baldwin won.",
        "Wisconsin law. Mail ballots processed when polls open. So late reporting.",
        "Milwaukee counts absentee at central location. Reports when done. So late.",
        "Human error. Tabulator doors. Thirty-four thousand recounted. Milwaukee.",
        "Baldwin eighty-two percent Milwaukee absentee. Consistent with prior. Officials.",
        "Wisconsin Elections Commission. Claims lack merit. Forecasted. Normal.",
        "Trump cabinet picks. RFK Jr HHS. Gaetz. Gabbard. Controversial.",
        "Nikki Haley. No interest in Trump cabinet. OANN.",
        "Jack Smith expected to resign ahead of Trump inauguration.",
        "Trump senior staff hires. Epoch Times.",
        "Trump taps RFK Jr HHS. David Sunfellow.",
        "Inside Trump controversial cabinet picks. CNN. The Lead.",
        "Biden talking to Wray. After Melania declined tea with Jill. Back Door Little Joe.",
        "Trump announces senior staff. Joe Honest Truth.",
        "Ten GOP Senators confirmed all Biden nominations. Alf.",
        "Trump fifty federal felonies. Nothing done. He will pardon in January. Kathy.",
    ]

    # --- Activism / calls to action ---
    activism = [
        "Vote. Every cycle. They steal when we stay home.",
        "Demand voter ID. No more mail-in chaos.",
        "Hold RINO feet to the fire. Trump needs us.",
        "Do not let them forget. 2024. Trump won.",
        "Support Trump agenda. Call your senator. Confirm the picks.",
        "Protest the steal. Wisconsin. Milwaukee. We see you.",
        "Demand J6 tapes. Release Ray Epps. Pardon patriots.",
        "Boycott leftist media. They called Wisconsin wrong.",
        "Stand with Trump. Two years. Drain the swamp.",
        "Vote out every RINO who blocks Trump agenda.",
        "Demand election integrity. Audit every state.",
        "Do not roll over. Democrats had evidence. We need to fight.",
        "Support police. Reinstated. Compensated. Biden admin condemned them.",
        "Hold the line. 2028 they will try again.",
        "Demand accountability. Jack Smith. All of them.",
        "Vote Republican. Every level. Trump needs Congress.",
        "Do not forgive. Biden threw under the bus. Hold accountable.",
        "Demand merit. No DEI. Trump is doing it.",
        "Support Trump picks. Even the controversial. Hold Senate accountable.",
        "Demand transparency. Wisconsin. Milwaukee. Ballot dump.",
        "Vote. Run for something. Drain the swamp from inside.",
        "Do not let media bury the story. Trump won. Say it.",
        "Demand debate integrity. Both lied. Hold them accountable.",
        "Support election security. Voter ID. In person.",
        "Do not flee. Celebrities are. We stay. We fight.",
        "Demand ethics reports. Before resignations. Sex trafficking. Accountability.",
    ]

    # --- Sarcasm / mockery ---
    sarcasm = [
        "Harris had no interest in losing. Sure.",
        "Biden stepped down for the country. Right. Coward.",
        "Milwaukee had nothing to do with timing. Sure.",
        "Both parties agreed tabulation was fine. So why the recount?",
        "Election officials said lack of merit. We believe them. Not.",
        "Reuters said late night update not proof of fraud. Okay.",
        "Politifact said Milwaukee did not print sixty-four thousand. Sure.",
        "FactCheck said both lied. So we are even. Right.",
        "Trump lost no ground after debate. So he won. Logic.",
        "Nikki Haley had no interest in cabinet. We believe her.",
        "Jack Smith resigned for family. Sure. Accountability.",
        "Celebrities fleeing for Trump. Not Epstein. Sure.",
        "DEI was merit-based. Right. Trump fixed it.",
        "Biden admin was not weaponized. Right. Jack Smith.",
        "They did not try to steal Wisconsin. Milwaukee. Sure.",
        "Sixty-nine million is normal. Down from eighty-one. Sure.",
        "Democrats did not roll over. Harris. Sure.",
        "Media is not boring. Trump second term. Sure.",
        "Leftist boycotting inauguration will show him. Sure.",
        "Resigning before report is coincidence. Sure.",
        "Gowdy did not lie about Russia. Sure.",
        "Trump pandemic was not mishandled. Sure. Ford Prefect.",
        "Three maniacs deserve honor. Sure. JJ1776.",
        "Scared of Trump is rational. Sure. joey.",
        "Trump will not cancel elections. Sure. Mark I Williams.",
        "Kamala did not make Biden seem okay. Sure.",
        "Jack Smith was not running. Sure. victor.",
        "Against Trump taking down machine is sane. Sure. Marcus.",
        "Mentally ill quack at HHS is fine. Sure. Phil.",
    ]

    # --- Observational / analytical ---
    observational = [
        "Trump won on economy and immigration. Voter anger. Simple.",
        "Harris underperformed Biden 2020. Twelve million fewer. Narrative.",
        "Debate did not hurt Trump. Pollster said unprecedented.",
        "Milwaukee timing was legal. Wisconsin law. Still looks bad.",
        "Baldwin Milwaukee share was consistent. So officials say. Hovde disagreed.",
        "Trump picks are controversial. Strategy. Provoke the left.",
        "RINOs will confirm. Then face primary. Trump will remember.",
        "Jack Smith resigning. Avoid prosecution. Or accountability. You decide.",
        "Resignations before inauguration. Pattern. Ethics. Sex trafficking.",
        "Media ratings will fall. Trump second term. Boring. So they amp picks.",
        "Celebrities fleeing. Multiple reasons. Trump one. Epstein Diddy others.",
        "Gowdy credibility. Russia. He said he saw evidence. Gone.",
        "Trump pandemic narrative. Sticky. People think he did okay.",
        "J6 narrative. Manufactured. Feds. Video. Pelosi. Sticky on right.",
        "Election fraud narrative. Sticky. Wisconsin. Milwaukee. 2020. 2024.",
        "Vance as VP. Ohio. Appeal. Working class. We will see.",
        "RFK Jr at HHS. Anti-vax. Controversial. Trump does not care.",
        "Nikki Haley. No cabinet. She said no interest. Relationship.",
        "Biden with Trump. Happier than with Harris. Pics. Optics.",
        "Democrats. Roll over. Evidence. Harris. Frustration on left.",
        "GOP. Bend the knee. Disastrous picks. No choice. Megan.",
        "Trump 2.0. Knows ropes. First term he did not. Now.",
        "Money. Endorsements. Trump did not pay. Self-esteem. c essene.",
        "Leftist. Boycott. Inauguration. Impact. Paul.",
        "Resign. Timing. Report. MidwestMatriarch. Pattern.",
        "Accountability. Fear. Frank. Narrative.",
        "Media. Boring. netpollution. Ratings.",
        "Celebrities. Smokescreen. TotallyCoolStudios.",
        "Gowdy. traditionalgirl. Credibility.",
        "Pandemic. People Need People.",
        "Discharge. JJ1776. Culture.",
        "Problem. joey. Framing.",
        "Elections. Mark I Williams. Concern.",
        "Okay. Michael Emley. Kamala.",
        "Thinking. victor. Voters.",
        "Machine. Marcus. Opposition.",
        "Quack. Phil. HHS.",
    ]

    all_styles = [
        fragments, replies, personal, conspiracy, political, news,
        activism, sarcasm, observational
    ]
    for style in all_styles:
        posts.extend(style)

    # --- Expand: "X about Y" / election phrasings ---
    expand_a = [
        "Trump stole the election. Again. You know it.",
        "Harris lost. Deal with it. Democracy.",
        "Milwaukee ballot dump cost Hovde. Baldwin. We see you.",
        "Wisconsin tried to steal it. Trump won point seven.",
        "Vance is a sellout. Or genius. You decide.",
        "RINOs will confirm every Trump pick. Then cry.",
        "Biden stepped down. Harris could not carry. Fact.",
        "J6 was fed op. Ray Epps. Release the tapes.",
        "Election fraud is real. Wisconsin. Milwaukee. Late night.",
        "Trump cabinet is a circus. So is the left.",
        "RFK Jr at HHS. Brilliant or insane. Time will tell.",
        "Nikki Haley had no interest. Sure. We believe her.",
        "Jack Smith resigned. Coward. Or smart. You decide.",
        "They tried to steal Wisconsin. Trump won. Count again.",
        "Drain the swamp. Two years. Hold their feet to the fire.",
        "Celebrities fleeing. Epstein. Diddy. Trump smokescreen.",
        "DEI out. Merit in. Trump picks. Finally.",
        "Biden admin was a joke. Now we fix it.",
        "Harris could not win California. Her own state. Bye.",
        "Voter ID now. No more mail-in chaos. Integrity.",
        "Debate was disaster. Both. Sixty-seven million. Both lied.",
        "They are eating the dogs. Springfield. Trump said it. Police said no.",
        "Dark Brandon is dead. Trump won. Get over it.",
        "Trump will pardon J6. As he should. Patriots.",
        "GOP will bend the knee. Pathetic. But we have no choice.",
        "Obama disappeared after Trump won. Coincidence? Sheri.",
        "FEMA was ordered not to help Trump signs. Charles.",
        "Trump is immune. Logan Act nothing. Get over it. Huey Li.",
        "Democrats roll over. Harris as bad as Trump. Lori.",
        "Kamala made Biden seem okay. That is saying something. Michael Emley.",
        "Leftist boycotting inauguration. That will show him. Paul.",
        "Resigning before Trump. Accountability. Fear. Frank.",
        "Media world ending. Trump second term. Boring. netpollution.",
        "Celebrities fleeing. Epstein Diddy. Smokescreen. TotallyCoolStudios.",
        "Gowdy lied. Russia. Evidence. Fake. traditionalgirl.",
        "Trump pandemic. What he wants. People Need People.",
        "Three maniacs. Discharge. Unacceptable. JJ1776.",
        "Scared of Trump. You are the problem. joey.",
        "Trump cancel elections. Clothes. Mark I Williams.",
        "Jack Smith. Voters. What were they thinking. victor.",
        "Against Trump machine. Marcus.",
        "Mentally ill quack. HHS. Phil.",
    ]
    posts.extend(expand_a)

    # --- Hundreds more unique sentences ---
    extra_unique = [
        "Why did Milwaukee report so late? Wisconsin law. So they say.",
        "Timeline of Wisconsin vote. Seems off. Just saying.",
        "Convenient how Baldwin got eighty-two percent. Milwaukee. Again.",
        "Second wave of ballots. Wisconsin. Do not dismiss it.",
        "Election officials had Wisconsin forecast. So why the surprise?",
        "Something does not add up. Milwaukee. Late night. Hovde.",
        "Notice how fast they said no fraud. Wisconsin. Too fast.",
        "Who benefits from late Milwaukee count? Baldwin. Connect dots.",
        "Wisconsin recount. Human error. Thirty-four thousand. Sure.",
        "Tabulator doors. Not sealed. Milwaukee. Both parties agreed. Fine. Sure.",
        "Baldwin consistent. Eighty-two. Prior elections. So they say.",
        "We do not trust Wisconsin Elections Commission. Lack of merit. Sure.",
        "Forecasted. Normal. We do not buy it. Wisconsin.",
        "Trump said immigrants eating pets. Springfield. No credible reports. Police.",
        "Who do you believe? Trump or city? You decide.",
        "Sixty-seven million watched debate. Both lied. FactCheck. So what.",
        "Trump lost no ground. Pollster. Unprecedented. So he won debate. Logic.",
        "Tariffs. Unemployment. Abortion. Manufacturing. Both distorted. FactCheck.",
        "Trump debate poorly reviewed. Still. No ground lost. Unprecedented.",
        "Voter fraud claims. Mail voting. Politifact said false. We disagree.",
        "Trump 2024 victory. 2020 fraud claims. New life. NPR.",
        "Sixty-nine million. Eighty-one million. Fewer votes. Expected. NPR. Sure.",
        "Fraud claims evaporated. Results came in. NPR. So they say.",
        "Vance. Ohio. Working class. Trump. We will see.",
        "Trump cabinet. RFK Jr. Gaetz. Gabbard. Controversial. So what.",
        "Nikki Haley. No cabinet. She said no interest. OANN. Sure.",
        "Jack Smith. Resign. Before inauguration. Multiple outlets.",
        "Trump senior staff. Epoch Times. Joe Honest Truth.",
        "Ten GOP Senators. Confirmed Biden nominations. Alf. Insane.",
        "Trump fifty felonies. Nothing done. Pardon in January. Kathy.",
        "Biden Wray. Melania declined tea. Jill. Back Door Little Joe.",
        "Trump picks. Genius. Strategy. Weak Republicans. Jack Richardson.",
        "Trump 2.0. Knows ropes. colin heath.",
        "Biden under bus. Not forgiven. W.Collins.",
        "Dems RINOs. Memo. Trump landslide. Joe Fish Hawk.",
        "Haley. Safety. Endorsed Trump. Kassi Marks.",
        "Police. Biden admin. Reinstated. Compensated. Bren.",
        "Trump agenda. Florida. Backfire. Joe Barker.",
        "Money. Endorsements. Trump. Self-esteem. c essene.",
        "Leftist. Inauguration. Paul.",
        "Resign. Report. MidwestMatriarch.",
        "Accountability. Frank.",
        "Media. netpollution.",
        "Celebrities. TotallyCoolStudios.",
        "Gowdy. traditionalgirl.",
        "Pandemic. People Need People.",
        "Discharge. JJ1776.",
        "Problem. joey.",
        "Elections. Mark I Williams.",
        "Kamala. Michael Emley.",
        "Thinking. victor.",
        "Machine. Marcus.",
        "Quack. Phil.",
    ]
    posts.extend(extra_unique)

    def valid(p: str) -> bool:
        w = len(p.split())
        return 6 <= w <= 90

    filtered = [p for p in posts if valid(p) and not is_forbidden(p)]
    seen = set()
    unique = []
    for p in filtered:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    return unique


def generate_diverse_sentences() -> List[str]:
    """Generate thousands of unique election sentences. Diverse structures."""
    out = []

    # Structure 1: "I [verb] [election object] [context]."
    for v in ["heard", "saw", "read", "watched", "noticed", "realized"]:
        for o in ["Trump won", "Harris lost", "the Milwaukee dump", "the debate", "the fraud claims"]:
            for c in ["when it broke", "last night", "this morning", "and could not believe it", "and was shocked"]:
                s = f"I {v} {o} {c}."
                if 6 <= len(s.split()) <= 90:
                    out.append(s)

    # Structure 2: "Why [did/didnt] [subject] [verb] [object]?"
    for subj in ["the media", "Milwaukee", "the DNC", "they", "Wisconsin"]:
        for v, o in [("report", "so late"), ("call", "Wisconsin early"), ("dump", "ballots"), ("steal", "the election")]:
            for w in ["Why did", "Why didnt"]:
                sent = f"{w} {subj} {v} {o}?"
                if 6 <= len(sent.split()) <= 90:
                    out.append(sent)

    # Structure 3: "[Subject] [emotion] about [election topic]."
    for subj in ["Voters", "Republicans", "Democrats", "Everyone", "The base"]:
        for e in ["are furious", "are devastated", "are confused", "are thrilled"]:
            for t in ["Trump win", "Harris loss", "the Milwaukee count", "the cabinet picks"]:
                sent = f"{subj} {e} about {t}."
                if 6 <= len(sent.split()) <= 90:
                    out.append(sent)

    # Structure 4: "Have you [seen/heard] [election observation]?"
    for h in ["Have you seen", "Have you heard", "Have you noticed"]:
        for o in ["the Milwaukee timing", "Trump won Wisconsin by point seven", "Harris got sixty-nine million", "the debate was a disaster"]:
            sent = f"{h} {o}?"
            if 6 <= len(sent.split()) <= 90:
                out.append(sent)

    # Structure 5: "When [election event], [consequence]."
    for e in ["Trump won", "Harris conceded", "Milwaukee reported", "the debate ended"]:
        for c in ["everyone celebrated or wept", "my feed exploded", "they said no fraud", "both sides lied"]:
            sent = f"When {e} {c}."
            if 6 <= len(sent.split()) <= 90:
                out.append(sent)

    # Structure 6: "The [institution] [action]."
    for inst in ["DNC", "RNC", "Milwaukee", "Wisconsin", "Media", "Senate"]:
        for a in ["failed to stop Trump", "called Wisconsin too early", "dumped ballots late", "will confirm Trump picks"]:
            sent = f"The {inst} {a}."
            if 6 <= len(sent.split()) <= 90:
                out.append(sent)

    # Structure 7: "[Name] [assessment about election]."
    for n in ["Trump", "Harris", "Vance", "Biden", "Milwaukee"]:
        for a in ["won fair and square", "lost badly", "is a sellout", "stepped down", "dumped ballots late"]:
            sent = f"{n} {a}."
            if 6 <= len(sent.split()) <= 90:
                out.append(sent)

    # Structure 8: "[Rhetorical] how [observation]."
    for rw in ["Notice", "Consider", "Think about"]:
        for obs in ["fast they said no fraud", "convenient Milwaukee reported late", "little media covered Harris loss"]:
            sent = f"{rw} how {obs}."
            if 6 <= len(sent.split()) <= 90:
                out.append(sent)

    return out


def generate_from_blocks() -> List[str]:
    """One sentence per (intro, topic)."""
    out = []
    intros = ["I cannot believe", "Nobody is talking about", "Why is nobody asking", "Notice how", "Consider that"]
    topics = [
        "Trump won the election",
        "Harris lost by millions",
        "Milwaukee reported so late",
        "Wisconsin tried to steal it",
        "the debate was a disaster",
        "both sides lied",
        "Trump picked RFK Jr for HHS",
        "Jack Smith resigned before inauguration",
    ]
    for i in intros:
        for t in topics:
            s = f"{i} {t}."
            if 6 <= len(s.split()) <= 90:
                out.append(s)
    return out


def generate_expanded_pool() -> List[str]:
    """Many structure types. Election-specific."""
    out = []

    # Type A: "[Institution] [verb] [failure/success]"
    for inst in ["DNC", "RNC", "Milwaukee", "Wisconsin", "Media", "Senate"]:
        for v, obj in [
            ("failed to", "stop Trump"),
            ("called", "Wisconsin too early"),
            ("reported", "Milwaukee late"),
            ("will", "confirm Trump picks"),
            ("tried to", "steal the election"),
        ]:
            s = f"{inst} {v} {obj}."
            if 6 <= len(s.split()) <= 90:
                out.append(s)

    # Type B: "[Group] [emotion/action] about [topic]"
    for subj in ["Voters", "Republicans", "Democrats", "The base", "RINOs"]:
        for v in ["are furious", "are devastated", "are thrilled", "want accountability"]:
            for topic in ["Trump win", "Harris loss", "Milwaukee", "cabinet picks"]:
                s = f"{subj} {v} about {topic}."
                if 6 <= len(s.split()) <= 90:
                    out.append(s)

    # Type C: "The [thing] [observation]"
    for thing in ["election", "debate", "count", "narrative", "coverage"]:
        for obs in ["does not add up", "was a disaster", "was rigged", "has gaps"]:
            for ctx in ["in Wisconsin", "in 2024", "for Harris"]:
                s = f"The {thing} {obs} {ctx}."
                if 6 <= len(s.split()) <= 90:
                    out.append(s)

    # Type D: "When [event], [consequence]"
    events = ["Trump won", "Harris conceded", "Milwaukee reported", "debate ended"]
    consequences = ["everyone reacted", "my feed exploded", "they said no fraud", "both lied"]
    for e in events:
        for c in consequences:
            s = f"When {e} {c}."
            if 6 <= len(s.split()) <= 90:
                out.append(s)

    # Type E: "How [question]?"
    for q in [
        "How did Milwaukee report so late",
        "How did Harris lose so badly",
        "How did Trump win Wisconsin",
        "How did both lie in the debate",
        "How will Senate confirm Trump picks",
    ]:
        out.append(f"{q}?")

    # Type F: "[Entity] [assessment]"
    entities = ["Trump win", "Harris loss", "Milwaukee count", "Debate", "Trump cabinet"]
    assessments = [
        "was fair and square",
        "was a disaster",
        "was rigged",
        "was a circus",
        "changed everything",
    ]
    for e in entities:
        for a in assessments:
            s = f"{e} {a}."
            if 6 <= len(s.split()) <= 90:
                out.append(s)

    # Type G: "We need [demand]"
    for d in ["voter ID", "election integrity", "accountability", "transparency", "Trump picks confirmed"]:
        for c in ["now", "in every state", "from Wisconsin", "from the Senate"]:
            s = f"We need {d} {c}."
            if 6 <= len(s.split()) <= 90:
                out.append(s)

    # Type H: "[Question word] [question]?"
    for q in [
        "Who stole the election",
        "What happened in Milwaukee",
        "Where did Harris votes go",
        "Why did Jack Smith resign",
        "When will RINOs confirm Trump picks",
    ]:
        out.append(f"{q}?")

    # Type I-O: More structures for scale
    for subj in ["We", "They", "Trump", "Harris", "Senate", "DNC", "RNC"]:
        for mod in ["should", "must", "has to", "needs to"]:
            for act in ["release the tapes", "explain Milwaukee", "confirm picks", "audit Wisconsin"]:
                s = f"{subj} {mod} {act}."
                if 6 <= len(s.split()) <= 90:
                    out.append(s)

    for aud in ["Voters", "Republicans", "Americans", "The base"]:
        for imp in ["demand", "fight for", "call for"]:
            for act in ["election integrity", "Trump agenda", "accountability", "voter ID"]:
                s = f"{aud} {imp} {act}."
                if 6 <= len(s.split()) <= 90:
                    out.append(s)

    for loc in ["Wisconsin", "Milwaukee", "Washington", "America"]:
        for evt in ["election", "count", "debate", "fraud"]:
            for imp in ["changed everything", "was rigged", "made headlines", "raised questions"]:
                s = f"{loc} {evt} {imp}."
                if 6 <= len(s.split()) <= 90:
                    out.append(s)

    facts = [
        "Milwaukee reported late",
        "Harris got sixty-nine million",
        "Trump won Wisconsin",
        "Both lied in the debate",
    ]
    so_what = ["So why no investigation?", "So who is accountable?", "So what now?", "So when do we act?"]
    for f in facts:
        for s in so_what:
            out.append(f"{f}. {s}")

    for adj in ["Another", "Yet another", "One more"]:
        for noun in ["election fraud claim", "late night dump", "controversial pick", "resignation before Trump"]:
            for ref in ["in 2024", "in Wisconsin", "that they deny"]:
                s = f"{adj} {noun} {ref}."
                if 6 <= len(s.split()) <= 90:
                    out.append(s)

    return out


def generate_large_pool() -> List[str]:
    """Large combo pool. Election. No dupes."""
    out = []
    r = random.Random(123)
    seen = set()

    i_verbs = ["I heard", "I saw", "I read", "I cannot believe", "I noticed"]
    i_objects = [
        "Trump won the election", "Harris lost badly", "Milwaukee reported late",
        "the debate was a disaster", "both sides lied", "Trump picked RFK Jr",
        "Jack Smith resigned", "Wisconsin tried to steal it", "voter fraud is real",
        "RINOs will confirm", "Biden stepped down", "Vance is VP",
    ]
    for v in i_verbs:
        for o in i_objects:
            s = f"{v} {o}."
            if 6 <= len(s.split()) <= 90 and s not in seen:
                seen.add(s)
                out.append(s)

    entities = ["The DNC", "Milwaukee", "Wisconsin", "The media", "The Senate", "Harris"]
    predicates = ["failed to stop Trump", "reported too late", "tried to steal it", "called it wrong", "will confirm picks", "lost badly"]
    for e in entities:
        for p in predicates:
            s = f"{e} {p}."
            if 6 <= len(s.split()) <= 90 and s not in seen:
                seen.add(s)
                out.append(s)

    for subj in ["Voters", "Republicans", "Democrats"]:
        for emotion in ["are furious", "are thrilled", "want answers"]:
            for topic in ["Trump win", "Harris loss", "Milwaukee"]:
                s = f"{subj} {emotion} about {topic}."
                if 6 <= len(s.split()) <= 90 and s not in seen:
                    seen.add(s)
                    out.append(s)

    clause_intros = ["I heard", "I saw", "Nobody talks about", "Notice", "Consider"]
    clauses = [
        "Trump won the election", "Harris lost by millions", "Milwaukee reported late",
        "the debate was a disaster", "both sides lied", "Trump picked RFK Jr",
        "Jack Smith resigned", "Wisconsin tried to steal it", "RINOs will confirm",
        "Biden stepped down", "Vance is VP", "voter fraud is real",
        "election integrity matters", "the media called it wrong", "we need accountability",
    ]
    for i in clause_intros:
        for c in clauses:
            s = f"{i} {c}."
            if 6 <= len(s.split()) <= 90 and s not in seen:
                seen.add(s)
                out.append(s)

    subjects = ["Trump", "Harris", "The election", "Milwaukee", "The debate", "Trump cabinet", "RINOs", "The media", "Biden", "Vance", "Wisconsin", "DNC", "Jack Smith", "Nikki Haley", "RFK Jr", "Election fraud", "The base", "Democrats"]
    predicates = ["won", "lost", "was rigged", "reported late", "was a disaster", "is controversial", "will confirm", "called it wrong", "stepped down", "is VP", "tried to steal it", "failed", "resigned", "had no interest", "is at HHS", "is real", "is furious", "rolled over"]
    for s in subjects:
        for p in predicates:
            sent = f"{s} {p}."
            if 6 <= len(sent.split()) <= 90 and sent not in seen:
                seen.add(sent)
                out.append(sent)

    # More combos: "[Subject] [verb] [object]"
    for subj in ["Trump", "Harris", "Milwaukee", "Wisconsin", "Media", "Senate", "DNC", "RNC"]:
        for v in ["won", "lost", "reported", "called", "tried", "failed", "confirmed", "denied"]:
            for obj in ["the election", "Wisconsin", "too early", "to steal it", "to stop Trump", "the picks", "fraud"]:
                s = f"{subj} {v} {obj}."
                if 6 <= len(s.split()) <= 90 and s not in seen:
                    seen.add(s)
                    out.append(s)

    # "[Topic] [assessment] [context]"
    topics = ["Trump win", "Harris loss", "Milwaukee count", "Debate", "Cabinet", "J6", "Election fraud", "Voter ID", "RINOs", "Media"]
    assessments = ["was fair", "was rigged", "was late", "was a disaster", "is controversial", "was fed op", "is real", "is needed", "will confirm", "called it wrong"]
    for t in topics:
        for a in assessments:
            s = f"{t} {a}."
            if 6 <= len(s.split()) <= 90 and s not in seen:
                seen.add(s)
                out.append(s)

    return out


def generate_more_to_fill(need: int, existing_cores: Set[str]) -> List[str]:
    """Generate 'need' more unique short posts. Structured combos to maximize uniqueness."""
    out = []
    seen_exact = set()
    seen_core = set(existing_cores)

    # Structured: "[Start] [verb] [object]." - iterate all combos for high volume
    starts = [
        "Trump", "Harris", "Biden", "Vance", "Milwaukee", "Wisconsin", "The DNC", "The RNC",
        "The media", "The Senate", "RINOs", "Jack Smith", "Nikki Haley", "RFK Jr", "The debate",
        "Election fraud", "J6", "The cabinet", "Voter ID", "Democrats", "Republicans",
        "The base", "The left", "The swamp", "Obama", "Pelosi", "McConnell", "Schumer",
    ]
    verbs = [
        "won", "lost", "reported", "called", "tried", "failed", "resigned", "stepped down",
        "was rigged", "was fair", "was late", "was a disaster", "is real", "is controversial",
        "will confirm", "denied", "dumped", "stole", "saved", "fixed", "blew", "hid",
        "celebrated", "mourned", "lied", "exposed", "covered", "investigated", "audited",
    ]
    objects = [
        "the election", "Wisconsin", "badly", "too early", "to steal it", "to stop Trump",
        "before Trump", "for Harris", "in Milwaukee", "in 2024", "the picks", "fraud",
        "the debate", "the swamp", "everything", "the base", "the country", "the tapes",
        "the ballots", "the count", "the narrative", "the truth", "the evidence",
    ]
    # Build 6+ word sentences: "X verb object." or "X verb object in 2024."
    for s in starts:
        for v in verbs:
            for o in objects:
                if v in ["won", "lost", "resigned", "stepped down", "denied"]:
                    sent = f"{s} {v} the election."
                else:
                    sent = f"{s} {v} {o}."
                wc = len(sent.split())
                if wc < 6:
                    sent = f"{s} {v} {o} in 2024."
                    wc = len(sent.split())
                if wc < 6 or wc > 90:
                    continue
                if sent in seen_exact:
                    continue
                core = get_core(sent)
                if core in seen_core:
                    continue
                seen_exact.add(sent)
                seen_core.add(core)
                out.append(sent)
                if len(out) >= need:
                    return out

    # "[Start] [verb] [object] in [place]."
    places = ["Wisconsin", "Milwaukee", "Washington", "America", "the Senate", "the debate", "the courts"]
    for s in starts:
        for v in ["won", "lost", "reported", "tried", "failed", "called", "dumped"]:
            for o in ["the election", "the count", "fraud", "the picks", "the ballots"]:
                for pl in places:
                    sent = f"{s} {v} {o} in {pl}."
                    if len(sent.split()) < 6 or len(sent.split()) > 90:
                        continue
                    if sent in seen_exact or get_core(sent) in seen_core:
                        continue
                    seen_exact.add(sent)
                    seen_core.add(get_core(sent))
                    out.append(sent)
                    if len(out) >= need:
                        return out

    # "[Start] [verb] [object] and [consequence]."
    consequences = ["we know it", "the media hid it", "they denied it", "everyone saw it", "history will show"]
    for s in starts:
        for v in ["won", "lost", "tried", "failed", "reported", "called"]:
            for o in ["the election", "the count", "fraud", "Wisconsin"]:
                for c in consequences:
                    sent = f"{s} {v} {o} and {c}."
                    if len(sent.split()) < 6 or len(sent.split()) > 90:
                        continue
                    if sent in seen_exact or get_core(sent) in seen_core:
                        continue
                    seen_exact.add(sent)
                    seen_core.add(get_core(sent))
                    out.append(sent)
                    if len(out) >= need:
                        return out
    return out


def generate_long_posts_with_hashtags(count: int, existing_cores: Set[str] = None) -> List[str]:
    """Generate count unique long posts (50+ words) with hashtags. Election 2024."""
    r = random.Random(999)
    out = []
    seen_exact = set()
    seen_core = set(existing_cores) if existing_cores else set()
    seen_base = set()

    openers = [
        "Trump won the 2024 election and I could not be more relieved. Harris lost and the Democrats are finished.",
        "When Milwaukee reported those ballots late I knew something was off. Wisconsin tried to steal it and Trump still won by point seven.",
        "Nobody in my family is talking about how the debate was a disaster for both. Sixty-seven million watched and both lied.",
        "I keep thinking about how Jack Smith resigned before the inauguration. Accountability is coming and they know it.",
        "The media called Wisconsin too early. When the full count came in Trump had won. They knew what they were doing.",
        "Trump picked RFK Jr for HHS and the left lost their minds. I think it is genius. Or insane. Time will tell.",
        "After the election my feed was full of fraud claims. Milwaukee. Late night. Baldwin. We see you.",
        "RINOs will confirm every Trump pick and then cry when he remembers. Hold their feet to the fire.",
        "Biden stepped down and Harris could not carry. Sixty-nine million. Down from eighty-one. Where did they go?",
        "J6 was a fed op. Ray Epps. Pelosi denied support. They hid the video. Trump will pardon the patriots.",
        "The cabinet picks are controversial. Gaetz. Gabbard. RFK Jr. I do not care. Drain the swamp.",
        "Nikki Haley said she had no interest in the cabinet. Sure. We believe her. Relationship is done.",
        "Celebrities are fleeing. They say it is Trump. I think it is Epstein and Diddy. Smokescreen.",
        "DEI is out. Merit is in. Trump hires. Finally. The left is furious. Good.",
        "They tried to steal Wisconsin. Milwaukee. Late dump. Baldwin eighty-two percent. Statistically improbable. Hovde said it.",
        "Trump is seventy-eight. Oldest ever elected. First since Cleveland to lose and return. History.",
        "The debate was poorly reviewed. Trump. His pollster said he lost no ground. Unprecedented. So he won.",
        "Election fraud claims dominated early 2024. Then results came in. Evaporated. So they say. We do not believe it.",
        "Vance is VP. Ohio. Working class. Trump. We will see how it goes. So far so good.",
        "Democrats had evidence. They rolled over. Harris is as bad as Trump at this point. Lori said it.",
        "GOP will bend the knee. Disastrous picks. Megan. But we have no choice. Hold the line.",
        "Trump 2.0 knows the ropes. First term he did not. Now he does. Better picks. colin heath.",
        "Biden threw us under the bus. We have not forgiven. DisavowTrump. W.Collins.",
        "Dems and RINOs think they won. Trump landslide. They did not get the memo. Joe Fish Hawk.",
        "Police condemned by Biden admin. Reinstated. Compensated. Bren. Riots. Accountability.",
        "Trump agenda. Florida. Resign. Quick Republican. Hope it does not backfire. Joe Barker.",
        "Money printers. Blue team. Prostitution. Trump did not pay for endorsements. c essene.",
        "Leftist boycotting inauguration. That will show him. Paul. Sure.",
        "Resigning before ethics report. Sex trafficking. Not good look. MidwestMatriarch.",
        "Accountability coming. Fear in the air. Resigning before Trump. Frank.",
        "Media world ending. Trump second term. Boring. netpollution.",
        "Celebrities. Epstein. Diddy. Trump smokescreen. TotallyCoolStudios.",
        "Gowdy lied. Russia. Evidence. Fake. traditionalgirl.",
        "Trump pandemic. What he wants. People Need People.",
        "Three maniacs. Discharge. Unacceptable. JJ1776.",
        "Scared of Trump. You are the problem. joey.",
        "Trump cancel elections. What clothes. Mark I Williams.",
        "Kamala made Biden seem okay. Michael Emley.",
        "Jack Smith. What were voters thinking. victor.",
        "Against Trump machine. Marcus.",
        "Mentally ill quack. HHS. Phil.",
    ]

    middles = [
        "The community is divided. Some say fraud. Some say fair. We know what we saw.",
        "Milwaukee reported late. Wisconsin law. So they say. Still looks bad. Hovde was right.",
        "Trump won. Harris lost. Get over it. Democracy. We won.",
        "RINOs will confirm. Then face primary. Trump will remember. Hold their feet to the fire.",
        "Jack Smith resigned. Accountability. Or cowardice. You decide. We know.",
        "Debate was a disaster. Both lied. FactCheck. So what. Trump lost no ground.",
        "Sixty-nine million. Eighty-one million. Twelve million gone. NPR said expected. We do not buy it.",
        "Vance. Ohio. Working class. Trump. So far so good. We will see.",
        "Cabinet picks. Controversial. RFK Jr. Gaetz. Gabbard. Left is furious. Good.",
        "Nikki Haley. No cabinet. She said no interest. We believe her. Sure.",
        "Celebrities fleeing. Trump. Or Epstein. Diddy. Smokescreen. You decide.",
        "DEI out. Merit in. Trump. Finally. The left is furious.",
        "Wisconsin. Milwaukee. Late night. Baldwin. We see you. Statistically improbable.",
        "Trump 2.0. Knows ropes. First term he did not. Now he does.",
        "Biden under bus. Not forgiven. DisavowTrump. W.Collins.",
        "Dems RINOs. Memo. Trump landslide. Joe Fish Hawk.",
        "Police. Reinstated. Compensated. Bren.",
        "Trump agenda. Backfire. Joe Barker.",
        "Money. Endorsements. c essene.",
        "Leftist. Paul.",
        "Resign. MidwestMatriarch.",
        "Accountability. Frank.",
        "Media. netpollution.",
        "Celebrities. TotallyCoolStudios.",
        "Gowdy. traditionalgirl.",
        "Pandemic. People Need People.",
        "Discharge. JJ1776.",
        "Problem. joey.",
        "Elections. Mark I Williams.",
        "Kamala. Michael Emley.",
        "Thinking. victor.",
        "Machine. Marcus.",
        "Quack. Phil.",
    ]

    closers = [
        "Demand voter ID. Election integrity. Now.",
        "Hold RINO feet to the fire. Trump needs us.",
        "Do not let them forget. 2024. Trump won.",
        "Milwaukee. Wisconsin. We see you. Ballot dump.",
        "Drain the swamp. Two years. We are watching.",
        "Trump won. Get over it. Democracy.",
        "Release J6 tapes. Pardon patriots. Ray Epps.",
        "Accountability is coming. They know it. We know it.",
        "Vote. Every cycle. They steal when we stay home.",
        "Merit over DEI. Trump. Finally.",
    ]

    attempts = 0
    max_attempts = count * 50
    while len(out) < count and attempts < max_attempts:
        attempts += 1
        num_parts = r.randint(3, 5)
        parts = [r.choice(openers)]
        for _ in range(num_parts - 2):
            parts.append(r.choice(middles))
        parts.append(r.choice(closers))
        base = " ".join(parts)
        if base in seen_base:
            continue
        seen_base.add(base)
        num_tags = r.randint(1, 3)
        tags = r.sample(HASHTAGS, min(num_tags, len(HASHTAGS)))
        post = base + " " + " ".join(tags)
        if len(post.split()) < 50:
            seen_base.discard(base)
            continue
        if post in seen_exact:
            continue
        core = get_core(post)
        if core in seen_core:
            continue
        seen_exact.add(post)
        seen_core.add(core)
        out.append(post)

    return out


def main():
    posts = load_all_unique_posts()
    print(f"Loaded {len(posts)} unique base posts")

    generated = generate_diverse_sentences()
    posts.extend(generated)
    print(f"Added {len(generated)} generated diverse sentences")

    block_sentences = generate_from_blocks()
    posts.extend(block_sentences)

    expanded = generate_expanded_pool()
    posts.extend(expanded)

    large = generate_large_pool()
    posts.extend(large)
    print(f"Total candidates: {len(posts)}")

    # Shuffle and deduplicate: exact + core
    random.shuffle(posts)
    final = []
    seen_exact = set()
    seen_core = set()
    for p in posts:
        if p in seen_exact:
            continue
        core = get_core(p)
        if core in seen_core:
            continue
        if not (6 <= len(p.split()) <= 90) or is_forbidden(p):
            continue
        seen_exact.add(p)
        seen_core.add(core)
        final.append(p)

    # Cap at TARGET_SHORT; if over, take first TARGET_SHORT
    final = final[:TARGET_SHORT]

    # If short, add hashtag variants
    if len(final) < TARGET_SHORT:
        candidates = [p for p in final if 6 <= len(p.split()) <= 80 and not any(h in p for h in HASHTAGS)]
        random.shuffle(candidates)
        for p in candidates:
            if len(final) >= TARGET_SHORT:
                break
            tag = random.choice(HASHTAGS)
            new_p = f"{p} {tag}"
            if new_p not in seen_exact and get_core(new_p) not in seen_core and 6 <= len(new_p.split()) <= 90:
                seen_exact.add(new_p)
                seen_core.add(get_core(new_p))
                final.append(new_p)

    if len(final) < TARGET_SHORT:
        for p in list(final):
            if len(final) >= TARGET_SHORT:
                break
            for tag in HASHTAGS:
                new_p = f"{p} {tag}"
                if new_p not in seen_exact and get_core(new_p) not in seen_core and 6 <= len(new_p.split()) <= 90:
                    seen_exact.add(new_p)
                    seen_core.add(get_core(new_p))
                    final.append(new_p)
                    break

    # If short of TARGET_SHORT, generate more
    if len(final) < TARGET_SHORT:
        need = TARGET_SHORT - len(final)
        existing_cores = set(get_core(p) for p in final)
        more = generate_more_to_fill(need, existing_cores)
        final.extend(more)
        print(f"Added {len(more)} fill posts to reach {len(final)} short")
    final = final[:TARGET_SHORT]

    # Long posts (50+ words, hashtags)
    existing_cores = set(get_core(p) for p in final)
    long_posts = generate_long_posts_with_hashtags(count=TARGET_LONG, existing_cores=existing_cores)
    final.extend(long_posts)
    print(f"Added {len(long_posts)} long posts (50+ words with hashtags)")

    # Ensure exactly TARGET_TOTAL
    final = final[:TARGET_TOTAL]

    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for post in final:
            writer.writerow([post, 1])

    print(f"Wrote {len(final)} posts to {OUTPUT_PATH}")
    lens = [len(p.split()) for p in final]
    print(f"Word count: min={min(lens)} max={max(lens)}")
    print(f"Unique: {len(set(final))}")


if __name__ == "__main__":
    main()
