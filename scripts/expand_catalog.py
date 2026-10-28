import json, random
random.seed(7)

keep = list(json.load(open("data/games.json")))

# ~120 hand-picked well-known cracked titles: title|genre|year|sizeGB|version|tags(comma)
PICKS = """
Red Dead Redemption 2|action-adventure|2019|120|v1.33 + All DLCs|open-world,story-rich
Grand Theft Auto V Enhanced|action|2025|110|v1.0 + Online|open-world,multiplayer
The Witcher 3 Complete Edition|rpg|2015|50|v4.04 + Hearts of Stone|fantasy,open-world
Elden Ring|rpg|2022|55|v1.15 + Shadow of the Erdtree|souls-like,open-world
Baldur's Gate 3|rpg|2023|70|v2.1 + Honour Among Thieves|turn-based,story-rich
Hogwarts Legacy|adventure|2023|65|v1.25 + All Quests|action-adventure,magic
Cyberpunk 2077 Ultimate|rpg|2020|67|v2.15 + Phantom Liberty|sci-fi,open-world
God of War Ragnarok|action|2022|100|v1.06 + Norse Saga|mythology,cutscene-heavy
Marvel's Spider-Man 2|action|2023|95|v1.05 + Miles Morales|superhero,open-world
Star Wars Jedi Survivor|action|2023|85|v1.06 + Force Trials|space,combat
Alan Wake 2|horror|2023|90|v1.06 + Night Springs|survival-horror,psychological
Dead Space Remake|horror|2023|50|v1.06 + The Signal|sci-fi-horror,survival
Resident Evil 4 Remake|horror|2023|60|v1.09 + Mercenaries|survival-horror,classic
Resident Evil Village|horror|2021|55|v1.25 + Mr X Showdown|survival-horror,gothic
Silent Hill 2 Remake|horror|2024|75|v1.06 + The Siren|psychological,atmospheric
DOOM Eternal|fps|2020|50|v1.31 + Tyrant's End|fast-paced,demon-slaying
Call of Duty Modern Warfare III|fps|2023|170|v1.08 + Warzone|military,multiplayer
Battlefield 2042|fps|2021|90|v2.4 + Portal Strike|military,all-kill
Apex Legends|battle-royale|2019|90|v1.25 + New Agents|free-to-play,competitive
Fortnite|battle-royale|2017|35|v30.2 + Season 9|free-to-play,building
Warframe|action|2013|15|v35.2 + The Circuit|scifi-shooter,cooperative
Path of Exile|rpg|2013|10|v3.25 + Settlers of Kalier|diablo-like,arpg
Diablo IV|rpg|2023|90|v1.25 + Vessel of Hatred|arpg,dark-fantasy
Genshin Impact|rpg|2020|20|v5.4 + Fontaine Chapter|open-world,anime-style
Honkai Star Rail|rpg|2023|30|v2.5 + Belobog|turn-based,sci-fi
Final Fantasy VII Rebirth|rpg|2024|120|v1.06 + Intermission|japan-rpg,remake
Final Fantasy XVI|rpg|2023|90|v1.06 + Shadow's Edge|japan-rpg,cutscene-heavy
Dragon Quest XI S|rpg|2019|10|v1.12 + Walkthrough|japan-rpg,classic
Xenoblade Chronicles 3 Definitive|rpg|2024|15|v1.06 + World Rebuild|japan-rpg,story-rich
Monster Hunter Rise Sunbreak|action|2022|10|v1.25 + Campfire|monster-hunting,multiplayer
Metroid Prime Remastered|adventure|2023|5|v1.06 + Samus Aran|first-person,space-exploration
Hades II|roguelike|2024|5|v1.06 + Underworld|roguelike,mythology
Hades|roguelike|2020|5|v1.25 + The Fates|roguelike,fast-paced
Terraria|sandbox|2011|2|v1.45 + Journey's End|sandbox,survival
Stardew Valley|simulation|2016|1|v1.65 + Farmhand Mode|farming,cozy
Minecraft Java Edition|sandbox|2011|5|v1.21 + Trails and Tales|block-building,creative
Valheim|survival|2021|3|v0.25 + Hearth and Home|norse-myths,cooperative
Sons of the Forest|survival|2024|10|v0.25 + Survival Kit|survival-crafting,horror
The Forest|survival|2018|5|v1.05 + Canopy Crawler|survival-crafting,open-world
Raft|survival|2018|3|v1.25 + Ocean Depths|ocean-survival,building
Subnautica Below Zero|survival|2021|5|v1.06 + Icebound|underwater,exploration
No Man's Sky|exploration|2019|10|v4.5 + Worlds of Ember|space-exploration,procedural
Starfield|exploration|2023|120|v1.9 + Shattered Space|space,open-world
Mass Effect Legendary Edition|rpg|2021|60|v1.06 + Andromeda|sci-fi,story-rich
Warhammer 40K Space Marine 2|action|2024|70|v1.05 + Vengeance|scifi-shooter,melee-combat
Total War PHARAOH|strategy|2023|40|v1.2 + Gold Edition|turn-based-strategy,egyptian
Civilization VI Gathering Storm|strategy|2018|15|v1.25 + Gods and Kings|turn-based-strategy,classic
XCOM 2 Collection|strategy|2016|10|v1.25 + Alien Invasion|turn-based-strategy,alien-invasion
Company of Heroes 3|strategy|2023|25|v1.05 + Eastern Front|real-time-strategy,wwii
Age of Empires II Definitive|strategy|2019|20|v1.25 + Dawn of the Dukes|rt-strategy,historical
Victoria 3|strategy|2022|15|v1.15 + Steam and Steel|grand-strategy,economic
Stellaris Apocalyptic|strategy|2018|15|v3.2 + Apocalypse Now|space-civilization,galactic
Football Manager 2024|simulation|2023|10|v24.1 + New Clubs|sports-management,football
Cities Skylines II|city-builder|2023|30|v1.06 + Snowfall|city-planning,traffic-systems
The Sims 4|life-sim|2014|15|v1.75 + New Seasons|life-simulation,house-building
Kena Bridge of Spirits|adventure|2019|15|v1.06 + Tiny Guardians|platformer,fantasy
Uncharted Legacy of Thieves|action-adventure|2022|80|v1.05 + All DLCs|treasure-hunting,open-world
Ghost of Tsushima Director's Cut|action|2021|90|v1.05 + Iaido Mastery|samurai-japan,story-rich
Sekiro Shadows Die Twice|action|2019|20|v1.05 + The Corrupted Blade|souls-like,feudal-japan
Death Stranding Director's Cut|action|2022|80|v1.06 + Open Country|strand-theory,delivery-mission
Returnal|action|2021|40|v1.06 + Void Rapture|roguelike-shooter,looping-narrative
Hellblade Senua's Saga|horror|2019|10|v1.05 + The Forsaken|psychological-horror,norse-myths
Control Ultimate Edition|action|2021|40|v1.25 + AWE Expansion|supernatural,bullet-time
Disco Elysium Final Cut|rpg|2019|2|v1.05 + Gold Edition|isometric-rpg,noir-detective
Divinity Original Sin 2|rpg|2017|15|v2.45 + The Deep|turn-based,party-play
Vampire Survivors|roguelite|2022|1|v1.25 + New Characters|top-down-shooter,survivor-like
Cuphead|arcade|2017|2|v1.05 + Infinite Ink|run-and-gun,boss-battles
Celeste|platformer|2018|1|v1.05 + Sidekick Mode|precision-platforming,difficult
Ori and the Will of the Wisps|platformer|2020|5|v1.06 + The Forest Spirit|metroidvania,beautiful-artwork
Hollow Knight Silksong|platformer|2025|3|v1.05 + Royal Court|metroidvania,insect-world
Dead Cells|roguelike|2018|5|v1.25 + The Bad Seed|roguelike,fast-paced
Risk of Rain 2|roguelike|2020|5|v1.25 + Return of the Beast|roguelike,multiplayer-co-op
Slay the Spire|card-game|2019|1|v1.35 + Clans and Relics|deck-builder,tower-climbing
Balatro|poker-like|2024|1|v1.05 + New Bluff Streaks|poker-strategy,score-chasing
Baba Is You|puzzle|2019|1|v1.05 + Rule-Breaking Worlds|logic-puzzles,creative-design
The Talos Principle 2|puzzle|2023|5|v1.06 + Reflections|philosophical,first-person-puzzle
Gris|platformer|2018|2|v1.05 + Color Palette Shifts|artistic,emotional-journey
A Short Hike|adventure|2019|1|v1.05 + The Summit|exploration,relaxing
Goat Simulator 3|comedy|2023|20|v1.06 + Goat Physics Overhaul|physics-comedy,chaotic-fun
Lies of P|action|2023|30|v1.06 + Pinocchio's Tale|souls-like,steampunk
Black Myth Wukong|action|2024|70|v1.05 + The Demon King|chinese-myths,combat-focused
Ghostwire Tokyo|action|2022|80|v1.06 + Spirit Hunter Kit|supernatural-tokyo,open-world
NieR Automata|rpg|2017|20|v1.06 + Machine Age|sci-fi-dystopia,turn-based-combat
Persona 5 Royal|rpg|2020|15|v1.25 + Phantom Thief Life|japan-rpg,stylish-graphics
Octopath Traveler II|rpg|2023|10|v1.06 + The Journey Continues|hd-2d-graphic-style,party-play
A Plague Tale Requiem|adventure|2022|40|v1.06 + Rat Swarm|historical-adventure,rat-infested
The Last of Us Part I|survival|2023|90|v1.06 + No Return|post-apocalyptic,emotional-story
Deathloop|shooter|2022|60|v1.06 + Time Loop Mastery|time-loop-shooter,mystery-solving
High on Life|fps|2022|50|v1.05 + Companion Bot|comedy-fps,alien-invasion
Immortals Fenyx Rising|action|2020|50|v1.06 + Olympus Trials|olympian-myths,platforming
Wasteland 3|rpg|2020|20|v1.06 + Desert Survival|post-apocalypse,western-usa
Outer Wilds|exploration|2019|5|v1.05 + The Star Cluster|space-mystery,time-loop
Grounded|survival|2020|15|v1.25 + Back to Nature|shrunk-down-world,insect-enemy
Stranded Deep|survival|2016|5|v1.25 + Tropical Island|island-survival,crafting-systems
Tomb Raider Legacy Collection|action-adventure|2016|30|v1.05 + Three Tomb Raiders|archaeology,classic-series
Hitman World of Assassination|action|2022|60|v1.12 + All Missions|stealth,sandwich-agent
Dying Light 2 Stay Human|action|2022|80|v1.15 + Follow the White Rabbit|zombie-outbreak,open-world
Dead by Daylight|horror|2016|15|v1.12 + New Killers|asymmetric-multiplayer,horror
Left 4 Dead 2|fps|2009|5|v1.25 + The Sacrifice|co-op-zombies,classic
Borderlands 3|fps|2019|40|v1.25 + Moxx's Big Score|loot-shooter,vivid-colors
Borderlands 4|fps|2025|70|v1.05 + Vault Hunter DLC|loot-shooter,narrative-driven
Outriders|fps|2021|45|v1.12 + Worldslayer|sci-fi-loot,cooperative-play
Anthem Legion|fps|2019|55|v1.06 + Juggernaut|juggernaut-class,flying-combat
War Thunder|fps|2013|20|v1.30 + Tank Battles|tank-battles,air-combat
World of Tanks|fps|2010|15|v1.25 + Armored Assault|armored-assault,tank-warfare
League of Legends|mo-rt|2009|10|v15.2 + Season Reset|team-based,competitive-esports
Smite|mo-rt|2014|10|v1.25 + God Wars|god-wars,multiplayer-online
Rocket League|arcade|2015|5|v14.2 + Rocket Rumble|car-football,fast-paced
Overcooked 2|puzzle|2018|5|v1.25 + New Kitchens|cooking-challenge,cooperative-fun
It Takes Two|adventure|2021|15|v1.06 + New Levels|two-player-adventure,puzzle-solving
Unravel Two|platformer|2018|5|v1.05 + Yarn Puzzles|yarn-puzzles,two-player-coop
A Way Out|adventure|2018|20|v1.06 + Escape Together|escape-together,suspenseful-story
Firewatch|adventure|2017|10|v1.05 + Forest Mystery|forest-mystery,story-rich
What Remains of Edith Finch|horror|2017|5|v1.05 + Family Secrets|family-secrets,psychological-horror
Gone Home|adventure|2013|2|v1.05 + House Mystery|house-mystery,exploration-focused
The Stanley Parable|comedy|2013|5|v1.05 + Office Oddities|office-oddities,humorous-twists
Inside|platformer|2016|2|v1.05 + Dark Worlds|dark-worlds,atmospheric-design
Limbo|platformer|2010|2|v1.05 + The Forgotten Place|forgotten-place,monochrome-art
Cuphead Mug Runners|arcade|2024|2|v1.05 + Multiplayer Mode|multiplayer-run-and-gun,boss-rush
Hades II Early Access|action|2024|5|v1.06 + Underworld Depths|roguelike-action,greek-mythology
"""

GENRE_LABEL = {
    "action":"Action / Adventure","rpg":"RPG","horror":"Horror","strategy":"Strategy",
    "simulation":"Simulation","arcade":"Arcade","puzzle":"Puzzle","platformer":"Platformer",
    "roguelike":"Roguelike","adventure":"Adventure","fps":"FPS","sandbox":"Sandbox",
    "survival":"Survival","exploration":"Exploration","card-game":"Card Game",
    "life-sim":"Life Sim","city-builder":"City Builder","shooter":"Shooter",
    "battle-royale":"Battle Royale","mo-rt":"MOBA / RTS","comedy":"Comedy",
    "poker-like":"Poker-Like","roguelite":"Roguelite","fps":"FPS"
}
REPACKERS = ["FitGirl","DODI","CODEX","RELOADED","SKIDROW","ElAmigos","TOKYO","OiGi","TEAM-OUT","INDIE-CRACK","NINTEN-CAVE","CRACKED.IO"]
GRADS = [
 "linear-gradient(135deg,#0f2027,#203a43,#2c5364)",
 "linear-gradient(135deg,#1a1a2e,#16213e,#0f3460)",
 "linear-gradient(135deg,#000428,#004e92)",
 "linear-gradient(135deg,#1f1c2c,#928dab)",
 "linear-gradient(135deg,#0b0b0b,#3a475a)",
 "linear-gradient(135deg,#000000,#434343)",
 "linear-gradient(135deg,#2c3e50,#4ca1af)",
 "linear-gradient(135deg,#0f0c29,#302b63,#24243e)",
]
TAG_POOL = ["open-world","multiplayer","story-rich","fast-paced","survival-horror","sci-fi","fantasy","turn-based","cozy","atmospheric","pixel-art","retro-style","competitive","single-player","online-only","cross-platform","controller-support","vr-ready","cloud-save","gamepass-available"]

def slug(t):
    return t.lower().replace(" ","-").replace(":","").replace("&","and")

def make(title, genre, year, size_gb, version, tags):
    repacker = random.choice(REPACKERS)
    y = year + (1 if random.random() < 0.3 else 0)
    return {
        "id": slug(title),
        "title": title,
        "genre": genre,
        "genreLabel": GENRE_LABEL.get(genre, "Game"),
        "description": f"A {GENRE_LABEL.get(genre,'game')} experience with rich storylines and engaging gameplay.",
        "crackedBy": repacker,
        "crackedDate": f"{year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "uploadedDate": f"{y}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "size": f"{size_gb} GB",
        "sizeBytes": int(size_gb * 1_000_000_000),
        "version": version,
        "isUpcoming": year >= 2025 and random.random() < 0.4,
        "isJustDropped": year >= 2024 and random.random() < 0.5,
        "isLatest": year >= 2024 and random.random() < 0.3,
        "rating": round(random.uniform(3.5, 5.0), 1),
        "tags": tags,
        "imageGradient": random.choice(GRADS),
        "repack": None,
        "sources": [repacker],
    }

ids = set(g["id"] for g in keep)
out = list(keep[:52])
for line in PICKS.strip().split("\n"):
    parts = [p.strip() for p in line.split("|")]
    if len(parts) != 6: continue
    title, genre, year, size, ver, tags = parts
    e = make(title, genre, int(year), float(size), ver, tags.split(","))
    if e["id"] not in ids:
        ids.add(e["id"]); out.append(e)

# Pad to exactly 500 total with generated entries
i = 1
while len(out) < 500:
    genre = random.choice(list(GENRE_LABEL.keys()))
    entry = make(f"Cracked Game {i}", genre, random.randint(2015,2025),
                round(random.uniform(1,120),1), f"v{random.randint(1,9)}.{random.randint(0,9)} + DLC Pack",
                random.sample(TAG_POOL, k=3))
    i += 1
    if entry["id"] not in ids:
        ids.add(entry["id"]); out.append(entry)

json.dump(out, open("data/games.json","w"), indent=1)
print(f"Wrote data/games.json with {len(out)} games")
print("first:", out[0]["title"])
print("last :", out[-1]["title"])
