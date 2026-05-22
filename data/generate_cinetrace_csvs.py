"""
CineTrace CSV Generation Pipeline
Generates CSVs that match the exact schema defined in cinetrace.sql
Uses a curated dataset of 60 landmark films with realistic influence links,
cinematic movements, crew, awards, reviews, watchlists, and votes.
"""

import csv
import os
import random
import hashlib
from datetime import datetime, timedelta, date

OUTPUT_DIR = OUTPUT_DIR = r"C:\Users\OMAR\Desktop\CineTrace\Data\cinetrace_csvs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def write_csv(filename, fieldnames, rows):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ {filename} — {len(rows)} rows")

def random_date(start_year=2018, end_year=2024):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def random_ts(start_year=2019, end_year=2024):
    d = random_date(start_year, end_year)
    h, m, s = random.randint(0,23), random.randint(0,59), random.randint(0,59)
    return f"{d} {h:02d}:{m:02d}:{s:02d}"

# ─────────────────────────────────────────────
# 1. DIRECTORS
# ─────────────────────────────────────────────
directors_data = [
    (1,  "Akira Kurosawa",       "Japanese",   1910, "Master of Japanese cinema known for epic samurai films and psychological dramas."),
    (2,  "Federico Fellini",     "Italian",    1920, "Pioneer of Italian neorealism and later art-house cinema, celebrated for dreamlike narratives."),
    (3,  "Ingmar Bergman",       "Swedish",    1918, "Renowned for existential and psychological explorations of the human condition."),
    (4,  "Stanley Kubrick",      "American",   1928, "Perfectionist auteur spanning horror, sci-fi, and historical drama with meticulous visual style."),
    (5,  "Jean-Luc Godard",      "French",     1930, "Founding figure of the French New Wave, known for radical narrative and editorial experimentation."),
    (6,  "François Truffaut",    "French",     1932, "Key New Wave director whose semi-autobiographical works redefined coming-of-age cinema."),
    (7,  "Orson Welles",         "American",   1915, "Innovative filmmaker whose Citizen Kane revolutionised cinematography and narrative structure."),
    (8,  "Alfred Hitchcock",     "British",    1899, "Master of suspense whose psychological thrillers set the template for modern genre filmmaking."),
    (9,  "Francis Ford Coppola", "American",   1939, "Director of The Godfather trilogy and Apocalypse Now, defining American New Hollywood cinema."),
    (10, "Martin Scorsese",      "American",   1942, "New York filmmaker celebrated for crime dramas, documentary work, and film preservation advocacy."),
    (11, "Andrei Tarkovsky",     "Russian",    1932, "Soviet auteur known for deeply meditative, visually poetic explorations of memory and spirituality."),
    (12, "Wong Kar-wai",         "Hong Kong",  1958, "Celebrated for lyrical, fragmented storytelling and saturated visual style in Hong Kong cinema."),
    (13, "Pedro Almodóvar",      "Spanish",    1949, "Spanish auteur known for melodramatic, colourful explorations of identity, desire, and family."),
    (14, "Abbas Kiarostami",     "Iranian",    1940, "Iranian master whose minimalist approach blurred the line between documentary and fiction."),
    (15, "Terrence Malick",      "American",   1943, "Philosophical filmmaker known for sparse dialogue and transcendent, nature-infused imagery."),
    (16, "David Lynch",          "American",   1946, "Surrealist auteur whose films explore the disturbing undercurrents of American suburban life."),
    (17, "Agnès Varda",          "French",     1928, "Pioneer of the French New Wave and feminist cinema, celebrated for playful documentary hybrids."),
    (18, "Ousmane Sembène",      "Senegalese", 1923, "Father of African cinema, whose films gave voice to post-colonial West African experience."),
    (19, "Chantal Akerman",      "Belgian",    1950, "Minimalist filmmaker whose Jeanne Dielman redefined feminist and structural cinema."),
    (20, "Satyajit Ray",         "Indian",     1921, "Bengali auteur whose Apu Trilogy brought Indian cinema to international acclaim."),
]

directors_rows = [
    {"director_id": d[0], "name": d[1], "nationality": d[2], "birth_year": d[3], "biography": d[4]}
    for d in directors_data
]
write_csv("directors.csv", ["director_id","name","nationality","birth_year","biography"], directors_rows)

# ─────────────────────────────────────────────
# 2. CINEMATOGRAPHERS
# ─────────────────────────────────────────────
cinematographers_data = [
    (1,  "Kazuo Miyagawa",        "Japanese",  1908),
    (2,  "Gianni Di Venanzo",     "Italian",   1920),
    (3,  "Sven Nykvist",          "Swedish",   1922),
    (4,  "John Alcott",           "British",   1931),
    (5,  "Raoul Coutard",         "French",    1924),
    (6,  "Nestor Almendros",      "Spanish",   1930),
    (7,  "Gregg Toland",          "American",  1904),
    (8,  "Robert Burks",          "American",  1909),
    (9,  "Gordon Willis",         "American",  1931),
    (10, "Michael Chapman",       "American",  1935),
    (11, "Vadim Yusov",           "Russian",   1929),
    (12, "Christopher Doyle",     "Australian",1952),
    (13, "José Luis Alcaine",     "Spanish",   1938),
    (14, "Mahmoud Kalari",        "Iranian",   1951),
    (15, "Néstor Almendros",      "Spanish",   1930),
    (16, "Frederick Elmes",       "American",  1946),
    (17, "Nurith Aviv",           "French",    1945),
    (18, "Georges Caristan",      "French",    1920),
    (19, "Babette Mangolte",      "French",    1941),
    (20, "Subrata Mitra",         "Indian",    1930),
]

cinematographers_rows = [
    {"cinematographer_id": c[0], "name": c[1], "nationality": c[2], "birth_year": c[3]}
    for c in cinematographers_data
]
write_csv("cinematographers.csv", ["cinematographer_id","name","nationality","birth_year"], cinematographers_rows)

# ─────────────────────────────────────────────
# 3. FILMS
# ─────────────────────────────────────────────
films_data = [
    # (film_id, title, release_year, country, synopsis, director_id, cinematographer_id, budget, language, runtime_min)
    (1,  "Rashomon",                     1950, "Japan",        "A murder is recounted by four unreliable witnesses in feudal Japan.",                                                        1,  1,  None,        "Japanese",  88),
    (2,  "Seven Samurai",                1954, "Japan",        "A poor village hires seven masterless samurai to protect them from bandits.",                                                1,  1,  None,        "Japanese",  207),
    (3,  "La Dolce Vita",                1960, "Italy",        "A journalist wanders through Rome's celebrity nightlife seeking meaning.",                                                   2,  2,  None,        "Italian",   174),
    (4,  "8½",                           1963, "Italy",        "A filmmaker struggles with creative block while juggling memory and fantasy.",                                               2,  2,  None,        "Italian",   138),
    (5,  "The Seventh Seal",             1957, "Sweden",       "A knight returning from the Crusades plays chess with Death.",                                                              3,  3,  None,        "Swedish",   96),
    (6,  "Persona",                      1966, "Sweden",       "A nurse caring for a mute actress begins to lose her own identity.",                                                        3,  3,  None,        "Swedish",   83),
    (7,  "2001: A Space Odyssey",        1968, "UK",           "A voyage to Jupiter descends into confrontation between man and artificial intelligence.",                                   4,  4,  10500000,    "English",   149),
    (8,  "A Clockwork Orange",           1971, "UK",           "A violent young man undergoes experimental aversion therapy in a dystopian Britain.",                                       4,  4,  2200000,     "English",   136),
    (9,  "Breathless",                   1960, "France",       "A small-time car thief goes on the run in Paris with an American student.",                                                  5,  5,  400000,      "French",    90),
    (10, "The 400 Blows",               1959, "France",       "A misunderstood Parisian boy drifts toward delinquency after repeated failures at school.",                                  6,  6,  None,        "French",    99),
    (11, "Citizen Kane",                 1941, "USA",          "The life of a media magnate is pieced together after his death through testimonies.",                                        7,  7,  839727,      "English",   119),
    (12, "Vertigo",                      1958, "USA",          "A detective with a fear of heights becomes obsessed with a mysterious woman.",                                               8,  8,  2479000,     "English",   128),
    (13, "The Godfather",                1972, "USA",          "The patriarch of a powerful crime family reluctantly hands power to his son.",                                               9,  9,  6000000,     "English",   175),
    (14, "Apocalypse Now",               1979, "USA",          "A Special Forces captain is sent into the jungle to assassinate a rogue colonel.",                                          9,  9,  31500000,    "English",   147),
    (15, "Taxi Driver",                  1976, "USA",          "A mentally unstable veteran works as a night-time cab driver in a decaying New York.",                                      10, 10, 1300000,     "English",   114),
    (16, "Goodfellas",                   1990, "USA",          "The rise and fall of a mobster over three decades in the New York underworld.",                                              10, 10, 25000000,    "English",   146),
    (17, "Andrei Rublev",                1966, "USSR",         "An icon painter journeys through a turbulent 15th century Russia.",                                                          11, 11, None,        "Russian",   183),
    (18, "Stalker",                      1979, "USSR",         "A guide leads two men into the mysterious Zone where wishes are supposedly granted.",                                        11, 11, None,        "Russian",   162),
    (19, "In the Mood for Love",         2000, "Hong Kong",    "Two neighbours suspect their spouses of having an affair and grow close.",                                                   12, 12, None,        "Cantonese", 98),
    (20, "Chungking Express",            1994, "Hong Kong",    "Two heartbroken policemen navigate lonely city life and unexpected connections.",                                           12, 12, None,        "Cantonese", 102),
    (21, "All About My Mother",          1999, "Spain",        "A nurse travels to Barcelona to find the father of her late son.",                                                          13, 13, 3000000,     "Spanish",   101),
    (22, "Talk to Her",                  2002, "Spain",        "Two men form an unlikely friendship while caring for comatose women they love.",                                            13, 13, 6000000,     "Spanish",   112),
    (23, "Close-Up",                     1990, "Iran",         "A real-life impostor poses as celebrated director Mohsen Makhmalbaf.",                                                      14, 14, None,        "Persian",   98),
    (24, "Taste of Cherry",              1997, "Iran",         "A man drives around Tehran looking for someone to bury him after his planned suicide.",                                     14, 14, None,        "Persian",   95),
    (25, "Days of Heaven",               1978, "USA",          "A farmworker and his lover scheme to inherit a dying wheat farmer's fortune.",                                               15, 15, 3000000,     "English",   94),
    (26, "The Tree of Life",             2011, "USA",          "A Texas family in the 1950s grapples with loss, memory, and the origins of existence.",                                     15, 15, 32000000,    "English",   139),
    (27, "Blue Velvet",                  1986, "USA",          "A young man discovers a severed ear and is drawn into a dark criminal underworld.",                                         16, 16, 6000000,     "English",   120),
    (28, "Mulholland Drive",             2001, "USA",          "An aspiring actress and an amnesiac woman investigate a mystery in Los Angeles.",                                           16, 16, 15000000,    "English",   147),
    (29, "Cléo from 5 to 7",            1962, "France",       "A singer wanders Paris waiting for cancer test results over two real-time hours.",                                           17, 17, None,        "French",    90),
    (30, "Vagabond",                     1985, "France",       "The last days of a drifting young woman are reconstructed through witness interviews.",                                     17, 17, None,        "French",    105),
    (31, "Black Girl",                   1966, "Senegal",      "A Senegalese woman's hopes are crushed by exploitation when she works for a French family.",                               18, 18, None,        "French",    65),
    (32, "Xala",                         1975, "Senegal",      "A corrupt businessman becomes afflicted with impotence on his wedding night.",                                              18, 18, None,        "Wolof",     123),
    (33, "Jeanne Dielman",               1975, "Belgium",      "Three days in the life of a widowed housewife slowly reveal a simmering crisis.",                                           19, 19, None,        "French",    201),
    (34, "News from Home",               1977, "Belgium",      "Letters from a mother are read over footage of New York City streets.",                                                     19, 19, None,        "French",    85),
    (35, "Pather Panchali",              1955, "India",        "A young boy grows up in poverty in rural Bengal in the first part of the Apu Trilogy.",                                     20, 20, None,        "Bengali",   125),
    (36, "The World of Apu",             1959, "India",        "The final chapter of the Apu Trilogy follows Apu into adulthood and fatherhood.",                                          20, 20, None,        "Bengali",   106),
    (37, "Yojimbo",                      1961, "Japan",        "A wandering samurai plays two rival gangs against each other in a lawless town.",                                           1,  1,  None,        "Japanese",  110),
    (38, "Amarcord",                     1973, "Italy",        "Episodic memories of small-town Italian life under Fascism in the 1930s.",                                                  2,  2,  None,        "Italian",   127),
    (39, "Wild Strawberries",            1957, "Sweden",       "An elderly professor reflects on his life during a long car journey.",                                                      3,  3,  None,        "Swedish",   91),
    (40, "Full Metal Jacket",            1987, "UK",           "Marine recruits endure brutal training before being deployed to Vietnam.",                                                   4,  4,  30000000,    "English",   116),
    (41, "Vivre Sa Vie",                 1962, "France",       "A young woman drifts into prostitution in twelve tableaux.",                                                                5,  5,  None,        "French",    85),
    (42, "Jules and Jim",                1962, "France",       "Two friends fall for the same free-spirited woman in the years around World War I.",                                        6,  5,  None,        "French",    105),
    (43, "Touch of Evil",                1958, "USA",          "A corrupt border-town detective clashes with a Mexican drug enforcement officer.",                                           7,  7,  895000,      "English",   95),
    (44, "Rear Window",                  1954, "USA",          "A photographer confined to a wheelchair suspects his neighbour of murder.",                                                  8,  8,  1000000,     "English",   112),
    (45, "The Godfather Part II",        1974, "USA",          "The story of the Corleone family expands into both past and present.",                                                      9,  9,  13000000,    "English",   202),
    (46, "Raging Bull",                  1980, "USA",          "The self-destructive rise and fall of boxer Jake LaMotta.",                                                                 10, 10, 18000000,    "English",   129),
    (47, "Mirror",                       1975, "USSR",         "Fragmented memories, dreams, and historical footage interweave in a meditation on identity.",                               11, 11, None,        "Russian",   108),
    (48, "Happy Together",               1997, "Hong Kong",    "A turbulent gay relationship between two Hong Kong men plays out in Buenos Aires.",                                         12, 12, None,        "Cantonese", 96),
    (49, "Volver",                       2006, "Spain",        "A woman returns to her village haunted by secrets and the apparent ghost of her mother.",                                   13, 13, 5000000,     "Spanish",   121),
    (50, "Where Is the Friend's House?", 1987, "Iran",         "A young boy searches a neighbouring village to return a classmate's notebook.",                                             14, 14, None,        "Persian",   83),
    (51, "Badlands",                     1973, "USA",          "A teenager and her older boyfriend go on a killing spree across the midwest.",                                              15, 15, 350000,      "English",   94),
    (52, "Eraserhead",                   1977, "USA",          "A man in an industrial wasteland is horrified by his severely deformed child.",                                             16, 16, 100000,      "English",   89),
    (53, "One Sings, the Other Doesn't", 1977, "France",       "Two women maintain a friendship across fifteen years of political and personal change.",                                    17, 17, None,        "French",    120),
    (54, "Ceddo",                        1977, "Senegal",      "A princess is kidnapped by an Imam as Islam encroaches on traditional African society.",                                    18, 18, None,        "Wolof",     120),
    (55, "Je Tu Il Elle",                1974, "Belgium",      "A young woman leaves home in an act of detachment and encounters strangers on the road.",                                   19, 19, None,        "French",    90),
    (56, "Aparajito",                    1956, "India",        "The middle chapter of the Apu Trilogy follows Apu's education and his mother's sacrifice.",                                 20, 20, None,        "Bengali",   110),
    (57, "Kagemusha",                    1980, "Japan",        "A petty thief is made to impersonate a dying warlord in 16th-century Japan.",                                               1,  1,  6500000,     "Japanese",  162),
    (58, "Satyricon",                    1969, "Italy",        "Two students pursue love and adventure in a fragmentary vision of ancient Rome.",                                           2,  2,  None,        "Italian",   128),
    (59, "Scenes from a Marriage",       1973, "Sweden",       "A married couple's relationship slowly dissolves over years of separation.",                                                3,  3,  None,        "Swedish",   169),
    (60, "Eyes Wide Shut",               1999, "UK",           "A doctor embarks on a surreal odyssey through sexual encounters in New York.",                                              4,  4,  65000000,    "English",   159),
]

films_rows = [
    {
        "film_id": f[0], "title": f[1], "release_year": f[2], "country": f[3],
        "synopsis": f[4], "director_id": f[5], "cinematographer_id": f[6],
        "budget": f[7] if f[7] else "", "language": f[8], "runtime_min": f[9]
    }
    for f in films_data
]
write_csv("films.csv",
    ["film_id","title","release_year","country","synopsis","director_id","cinematographer_id","budget","language","runtime_min"],
    films_rows)

# ─────────────────────────────────────────────
# 4. GENRES
# ─────────────────────────────────────────────
genres_data = [
    (1,  "Drama",           "Narrative films focused on realistic characters and emotional themes."),
    (2,  "Thriller",        "Films designed to generate suspense, tension, and excitement."),
    (3,  "Crime",           "Films centred on criminal acts, investigations, or the criminal underworld."),
    (4,  "Science Fiction", "Speculative films exploring futuristic technology, space, and artificial intelligence."),
    (5,  "Horror",          "Films intended to frighten, disturb, or unsettle the audience."),
    (6,  "Romance",         "Films focused on love relationships and emotional intimacy."),
    (7,  "War",             "Films set during armed conflicts depicting combat and its human cost."),
    (8,  "Historical",      "Films set in or depicting a specific historical period or event."),
    (9,  "Documentary",     "Non-fiction films presenting factual information about real events or people."),
    (10, "Experimental",    "Films that challenge conventional narrative and formal filmmaking structures."),
    (11, "Comedy",          "Films intended to provoke laughter through character, situation, or dialogue."),
    (12, "Adventure",       "Films emphasising journeys, quests, and physically daring situations."),
    (13, "Philosophical",   "Films centrally concerned with existential, ethical, or metaphysical questions."),
    (14, "Social Realism",  "Films that depict the everyday lives of working-class or marginalised people."),
    (15, "Feminist",        "Films that foreground female experience and critique patriarchal structures."),
]
genres_rows = [{"genre_id": g[0], "name": g[1], "description": g[2]} for g in genres_data]
write_csv("genres.csv", ["genre_id","name","description"], genres_rows)

# ─────────────────────────────────────────────
# 5. FILM_GENRES
# ─────────────────────────────────────────────
film_genres_data = [
    # (film_id, genre_id)
    (1,1),(1,8),(1,13),
    (2,1),(2,12),(2,7),
    (3,1),(3,11),(3,14),
    (4,1),(4,13),(4,11),
    (5,1),(5,13),(5,5),
    (6,1),(6,10),(6,5),
    (7,4),(7,13),(7,12),
    (8,4),(8,3),(8,5),
    (9,3),(9,1),(9,11),
    (10,1),(10,14),(10,11),
    (11,1),(11,3),(11,13),
    (12,2),(12,1),(12,6),
    (13,3),(13,1),(13,8),
    (14,7),(14,1),(14,13),
    (15,3),(15,1),(15,14),
    (16,3),(16,1),(16,8),
    (17,1),(17,8),(17,13),
    (18,4),(18,13),(18,1),
    (19,6),(19,1),(19,14),
    (20,6),(20,1),(20,11),
    (21,1),(21,14),(21,15),
    (22,1),(22,6),(22,13),
    (23,9),(23,10),(23,1),
    (24,1),(24,13),(24,14),
    (25,1),(25,6),(25,14),
    (26,1),(26,13),(26,8),
    (27,2),(27,5),(27,1),
    (28,2),(28,5),(28,10),
    (29,1),(29,15),(29,14),
    (30,1),(30,15),(30,14),
    (31,1),(31,14),(31,15),
    (32,1),(32,14),(32,11),
    (33,1),(33,15),(33,14),
    (34,9),(34,10),(34,15),
    (35,1),(35,14),(35,8),
    (36,1),(36,14),(36,6),
    (37,3),(37,12),(37,11),
    (38,1),(38,11),(38,8),
    (39,1),(39,13),(39,8),
    (40,7),(40,1),(40,14),
    (41,1),(41,14),(41,15),
    (42,6),(42,1),(42,8),
    (43,3),(43,2),(43,1),
    (44,2),(44,3),(44,1),
    (45,3),(45,1),(45,8),
    (46,1),(46,3),(46,14),
    (47,1),(47,13),(47,10),
    (48,6),(48,1),(48,14),
    (49,1),(49,5),(49,15),
    (50,1),(50,14),(50,11),
    (51,3),(51,1),(51,14),
    (52,5),(52,10),(52,1),
    (53,1),(53,15),(53,14),
    (54,1),(54,8),(54,14),
    (55,1),(55,10),(55,15),
    (56,1),(56,14),(56,8),
    (57,1),(57,8),(57,12),
    (58,1),(58,8),(58,10),
    (59,1),(59,6),(59,14),
    (60,2),(60,6),(60,1),
]
film_genres_rows = [{"film_id": fg[0], "genre_id": fg[1]} for fg in film_genres_data]
write_csv("film_genres.csv", ["film_id","genre_id"], film_genres_rows)

# ─────────────────────────────────────────────
# 6. CINEMATIC MOVEMENTS
# ─────────────────────────────────────────────
movements_data = [
    (1,  "Italian Neorealism",        "Italy",   1942, 1952, "Post-war movement using non-actors and location shooting to depict working-class life."),
    (2,  "French New Wave",           "France",  1958, 1973, "Innovative movement rejecting classical Hollywood in favour of personal, reflexive filmmaking."),
    (3,  "Japanese Golden Age",       "Japan",   1950, 1965, "Period of extraordinary creative output in Japanese studio cinema led by Kurosawa and others."),
    (4,  "Soviet Poetic Cinema",      "USSR",    1960, 1985, "Soviet movement prioritising lyrical, non-narrative imagery over socialist realism."),
    (5,  "New Hollywood",             "USA",     1967, 1980, "Director-driven American cinema challenging studio conventions with darker, ambiguous narratives."),
    (6,  "Third Cinema",              "Africa",  1960, 1990, "Political filmmaking from Latin America and Africa challenging colonialism and Western values."),
    (7,  "Taiwanese New Wave",        "Taiwan",  1982, 1995, "Contemplative, realist movement foregrounding Taiwanese social change and identity."),
    (8,  "Hong Kong New Wave",        "HK",      1979, 1997, "Energetic Hong Kong movement blending genre cinema with personal artistic vision."),
    (9,  "Iranian New Wave",          "Iran",    1969, 2000, "Austere, humanist movement often focusing on children and the rural poor."),
    (10, "Structural Film",           "USA",     1965, 1980, "American avant-garde movement foregrounding film's material properties over narrative."),
    (11, "Feminist Cinema",           "France",  1970, 1990, "Films by and for women, challenging the male gaze and conventional representations of femininity."),
    (12, "Bengali Parallel Cinema",   "India",   1952, 1984, "Art-house Indian cinema outside the Bollywood mainstream, grounded in literary realism."),
]
movements_rows = [
    {"movement_id": m[0], "name": m[1], "origin_country": m[2], "start_year": m[3], "end_year": m[4], "description": m[5]}
    for m in movements_data
]
write_csv("cinematic_movements.csv",
    ["movement_id","name","origin_country","start_year","end_year","description"],
    movements_rows)

# ─────────────────────────────────────────────
# 7. FILM_MOVEMENTS
# ─────────────────────────────────────────────
film_movements_data = [
    # (film_id, movement_id, role)
    (1,3,"foundational"),(2,3,"foundational"),(37,3,"foundational"),(57,3,"foundational"),
    (3,1,"late"),(4,1,"late"),(38,1,"late"),
    (9,2,"foundational"),(10,2,"foundational"),(29,2,"foundational"),(41,2,"key work"),
    (42,2,"key work"),(5,2,"influenced"),(30,2,"late"),
    (17,4,"foundational"),(18,4,"key work"),(47,4,"key work"),
    (13,5,"key work"),(14,5,"key work"),(15,5,"foundational"),(25,5,"key work"),
    (51,5,"foundational"),(16,5,"late"),(46,5,"key work"),
    (31,6,"foundational"),(32,6,"key work"),(54,6,"key work"),
    (19,8,"key work"),(20,8,"foundational"),(48,8,"key work"),
    (23,9,"key work"),(24,9,"key work"),(50,9,"foundational"),
    (33,11,"foundational"),(34,11,"key work"),(55,11,"foundational"),(53,11,"key work"),
    (35,12,"foundational"),(36,12,"key work"),(56,12,"key work"),
    (11,5,"influenced"),(12,5,"influenced"),(43,5,"influenced"),
    (7,5,"influenced"),(8,5,"key work"),
]
film_movements_rows = [{"film_id": fm[0], "movement_id": fm[1], "role": fm[2]} for fm in film_movements_data]
write_csv("film_movements.csv", ["film_id","movement_id","role"], film_movements_rows)

# ─────────────────────────────────────────────
# 8. INFLUENCE_LINKS
# ─────────────────────────────────────────────
# source → influenced target; target_film_id matches schema column name
influence_links_data = [
    # (link_id, source_film_id, target_film_id, influence_type, evidence_url, notes, recorded_at)
    (1,  1,  9,  "narrative structure",  None, "Godard cited Rashomon's unreliable narration as liberating for his own storytelling.",  "2021-03-15"),
    (2,  2,  13, "ensemble staging",     None, "Coppola acknowledged Seven Samurai as a template for group loyalty and betrayal.",        "2020-07-10"),
    (3,  11, 13, "visual grammar",       None, "Gordon Willis and Coppola drew on Citizen Kane's low-angle lighting for The Godfather.", "2020-07-11"),
    (4,  11, 7,  "deep focus",           None, "Kubrick studied Gregg Toland's deep focus technique extensively before 2001.",           "2019-04-22"),
    (5,  12, 28, "obsessive protagonist","None","Lynch acknowledged Vertigo's psychological doubling as a key reference for Mulholland Drive.", "2022-01-08"),
    (6,  9,  20, "jump cuts",            None, "Wong Kar-wai's fragmented editing in Chungking Express draws on Godard's jump cuts.",    "2021-11-30"),
    (7,  5,  18, "metaphysical imagery", None, "Tarkovsky described The Seventh Seal as confirming cinema's capacity for philosophy.",   "2019-06-17"),
    (8,  17, 26, "memory structure",     None, "Malick's fragmentary childhood memories in Tree of Life echo Tarkovsky's Mirror.",       "2022-09-04"),
    (9,  2,  40, "military camaraderie", None, "Kubrick's Full Metal Jacket uses Seven Samurai's group dynamics in a war context.",      "2020-12-01"),
    (10, 15, 25, "lyrical landscapes",   None, "Days of Heaven's visual poetry is a direct development of Badlands' approach.",         "2021-05-19"),
    (11, 10, 30, "child protagonist",    None, "Varda acknowledged The 400 Blows' influence on her portrayal of marginal youth.",       "2022-03-11"),
    (12, 33, 19, "domestic duration",    None, "Wong Kar-wai has cited Jeanne Dielman's temporal realism as an influence.",             "2021-08-25"),
    (13, 35, 50, "rural humanism",       None, "Kiarostami's minimalist rural films owe a clear debt to Satyajit Ray's Apu Trilogy.",    "2020-10-13"),
    (14, 11, 43, "deep space staging",   None, "Orson Welles' own Touch of Evil continues his exploration of deep-focus grammar.",       "2019-02-28"),
    (15, 13, 16, "crime epic structure", None, "Scorsese has repeatedly cited The Godfather as the model for Goodfellas.",              "2020-04-06"),
    (16, 9,  41, "handheld freedom",     None, "Godard's Vivre Sa Vie continues Breathless' experiment in location handheld shooting.", "2021-07-14"),
    (17, 6,  55, "female interiority",   None, "Akerman cited Persona as foundational for her exploration of women's inner lives.",     "2022-06-01"),
    (18, 3,  38, "episodic Rome",        None, "Amarcord revisits La Dolce Vita's episodic portrait of Italian social life.",           "2020-09-09"),
    (19, 4,  28, "subjective reality",   None, "Lynch's Mulholland Drive shares 8½'s structure of a protagonist confusing fantasy and reality.", "2022-01-09"),
    (20, 52, 27, "surreal suburban dread","None","Blue Velvet develops the surrealist horror Eraserhead established.",                  "2021-04-17"),
    (21, 31, 32, "colonial critique",    None, "Sembène's Xala extends the political critique he launched with Black Girl.",             "2020-11-22"),
    (22, 1,  23, "meta-narrative",       None, "Close-Up's play with reality and fiction owes much to Rashomon's shifting perspectives.","2021-06-30"),
    (23, 18, 24, "existential journey",  None, "Taste of Cherry's contemplative structure follows Stalker's slow existential road movie.", "2022-02-14"),
    (24, 14, 26, "war as metaphysics",   None, "The Tree of Life's battlefield imagery consciously echoes Apocalypse Now.",             "2022-10-05"),
    (25, 44, 12, "voyeurism theme",      None, "Hitchcock deepened Rear Window's voyeurism theme in Vertigo.",                          "2019-09-18"),
    (26, 37, 13, "honour code",          None, "The Godfather's code of silence mirrors the samurai honour code Yojimbo examines.",     "2020-08-03"),
    (27, 47, 8,  "fragmented memory",    None, "Mirror's disorienting time structure anticipates the fragmented consciousness of Eyes Wide Shut.", "2022-04-21"),
    (28, 29, 53, "female solidarity",    None, "Varda's own One Sings builds on the feminist wandering established in Cléo from 5 to 7.", "2021-12-12"),
    (29, 35, 56, "coming of age",        None, "Aparajito is a direct sequel continuing Pather Panchali's portrait of Apu's growth.",   "2019-01-05"),
    (30, 11, 15, "urban alienation",     None, "Taxi Driver's visual debt to Citizen Kane appears in its nocturnal low-angle city shots.", "2021-02-07"),
]
influence_rows = [
    {
        "link_id": il[0], "source_film_id": il[1], "target_film_id": il[2],
        "influence_type": il[3], "evidence_url": il[4] if il[4] else "",
        "notes": il[5], "recorded_at": il[6]
    }
    for il in influence_links_data
]
write_csv("influence_links.csv",
    ["link_id","source_film_id","target_film_id","influence_type","evidence_url","notes","recorded_at"],
    influence_rows)

# ─────────────────────────────────────────────
# 9. CREW_MEMBERS  (person_id, not crew_id)
# ─────────────────────────────────────────────
crew_members_data = [
    (1,  "Ishirō Honda",          "Japanese",   "Screenwriter"),
    (2,  "Toshiro Mifune",        "Japanese",   "Actor"),
    (3,  "Tullio Pinelli",        "Italian",    "Screenwriter"),
    (4,  "Giulietta Masina",      "Italian",    "Actor"),
    (5,  "Harriet Andersson",     "Swedish",    "Actor"),
    (6,  "Bibi Andersson",        "Swedish",    "Actor"),
    (7,  "Arthur C. Clarke",      "British",    "Screenwriter"),
    (8,  "Malcolm McDowell",      "British",    "Actor"),
    (9,  "Jean-Paul Belmondo",    "French",     "Actor"),
    (10, "Jeanne Moreau",         "French",     "Actor"),
    (11, "Bernard Herrmann",      "American",   "Composer"),
    (12, "Kim Novak",             "American",   "Actor"),
    (13, "Marlon Brando",         "American",   "Actor"),
    (14, "Robert Duvall",         "American",   "Actor"),
    (15, "Jodie Foster",          "American",   "Actor"),
    (16, "Robert De Niro",        "American",   "Actor"),
    (17, "Eduard Artemyev",       "Russian",    "Composer"),
    (18, "Tony Leung",            "Hong Kong",  "Actor"),
    (19, "Maggie Cheung",         "Hong Kong",  "Actor"),
    (20, "Cecilia Roth",          "Spanish",    "Actor"),
    (21, "Javier Bardem",         "Spanish",    "Actor"),
    (22, "Hossain Sabzian",       "Iranian",    "Actor"),
    (23, "Homayoun Ershadi",      "Iranian",    "Actor"),
    (24, "Linda Manz",            "American",   "Actor"),
    (25, "Brad Pitt",             "American",   "Actor"),
    (26, "Isabella Rossellini",   "Italian",    "Actor"),
    (27, "Naomi Watts",           "American",   "Actor"),
    (28, "Corinne Marchand",      "French",     "Actor"),
    (29, "Sandrine Bonnaire",     "French",     "Actor"),
    (30, "Mbissine Thérèse Diop", "Senegalese", "Actor"),
    (31, "Thierno Leye",          "Senegalese", "Actor"),
    (32, "Delphine Seyrig",       "French",     "Actor"),
    (33, "Kanu Bannerjee",        "Indian",     "Actor"),
    (34, "Soumitra Chatterjee",   "Indian",     "Actor"),
    (35, "Tatsuya Nakadai",       "Japanese",   "Actor"),
    (36, "Nino Rota",             "Italian",    "Composer"),
    (37, "Max von Sydow",         "Swedish",    "Actor"),
    (38, "R. Lee Ermey",          "American",   "Actor"),
    (39, "Anna Karina",           "Danish",     "Actor"),
    (40, "Oskar Werner",          "Austrian",   "Actor"),
    (41, "Akim Tamiroff",         "Russian",    "Actor"),
    (42, "Grace Kelly",           "American",   "Actor"),
    (43, "Al Pacino",             "American",   "Actor"),
    (44, "Joe Pesci",             "American",   "Actor"),
    (45, "Anatoli Solonitsyn",    "Russian",    "Actor"),
    (46, "Faye Dunaway",          "American",   "Actor"),
    (47, "Nicole Kidman",         "Australian", "Actor"),
    (48, "Rula Jebreal",          "Palestinian","Actor"),
    (49, "Penélope Cruz",         "Spanish",    "Actor"),
    (50, "Babak Ahmadpour",       "Iranian",    "Actor"),
]
crew_rows = [
    {"person_id": c[0], "full_name": c[1], "nationality": c[2], "specialisation": c[3]}
    for c in crew_members_data
]
write_csv("crew_members.csv", ["person_id","full_name","nationality","specialisation"], crew_rows)

# ─────────────────────────────────────────────
# 10. FILM_CREW (uses person_id, has leadp)
# ─────────────────────────────────────────────
film_crew_data = [
    # (film_id, person_id, role, leadp)
    (1,  2,  "Lead Actor",    True),
    (1,  1,  "Co-writer",     False),
    (2,  2,  "Lead Actor",    True),
    (3,  4,  "Supporting Actor", True),
    (4,  4,  "Lead Actor",    True),
    (4,  36, "Composer",      False),
    (5,  37, "Lead Actor",    True),
    (6,  5,  "Lead Actor",    True),
    (6,  6,  "Supporting Actor", True),
    (7,  7,  "Screenwriter",  False),
    (8,  8,  "Lead Actor",    True),
    (9,  9,  "Lead Actor",    True),
    (10, 10, "Supporting Actor", False),
    (11, 11, "Composer",      False),
    (12, 12, "Lead Actress",  True),
    (12, 11, "Composer",      False),
    (13, 13, "Lead Actor",    True),
    (13, 14, "Supporting Actor", True),
    (13, 36, "Composer",      False),
    (13, 43, "Supporting Actor", True),
    (14, 14, "Lead Actor",    True),
    (15, 16, "Lead Actor",    True),
    (15, 15, "Supporting Actress", True),
    (16, 16, "Lead Actor",    True),
    (16, 44, "Supporting Actor", True),
    (17, 45, "Lead Actor",    True),
    (17, 17, "Composer",      False),
    (18, 45, "Lead Actor",    True),
    (18, 17, "Composer",      False),
    (19, 18, "Lead Actor",    True),
    (19, 19, "Lead Actress",  True),
    (20, 18, "Supporting Actor", False),
    (21, 20, "Lead Actress",  True),
    (22, 21, "Lead Actor",    True),
    (23, 22, "Lead Actor",    True),
    (24, 23, "Lead Actor",    True),
    (25, 24, "Lead Actress",  True),
    (26, 25, "Narrator",      False),
    (27, 26, "Lead Actress",  True),
    (28, 27, "Lead Actress",  True),
    (29, 28, "Lead Actress",  True),
    (30, 29, "Lead Actress",  True),
    (31, 30, "Lead Actress",  True),
    (32, 31, "Lead Actor",    True),
    (33, 32, "Lead Actress",  True),
    (35, 33, "Lead Actor",    True),
    (36, 34, "Lead Actor",    True),
    (37, 35, "Lead Actor",    True),
    (38, 36, "Composer",      False),
    (39, 37, "Lead Actor",    True),
    (40, 38, "Supporting Actor", True),
    (41, 39, "Lead Actress",  True),
    (42, 40, "Lead Actor",    True),
    (43, 41, "Supporting Actor", True),
    (44, 42, "Lead Actress",  True),
    (45, 43, "Lead Actor",    True),
    (45, 14, "Supporting Actor", True),
    (46, 16, "Lead Actor",    True),
    (47, 45, "Lead Actor",    True),
    (47, 17, "Composer",      False),
    (49, 49, "Lead Actress",  True),
    (50, 50, "Lead Actor",    True),
    (57, 35, "Lead Actor",    True),
    (60, 47, "Lead Actress",  True),
]
film_crew_rows = [
    {"film_id": fc[0], "person_id": fc[1], "role": fc[2], "leadp": 1 if fc[3] else 0}
    for fc in film_crew_data
]
write_csv("film_crew.csv", ["film_id","person_id","role","leadp"], film_crew_rows)

# ─────────────────────────────────────────────
# 11. AWARDS
# ─────────────────────────────────────────────
awards_data = [
    (1,  1,  "Venice Film Festival",   "Golden Lion",                  1950, "Won"),
    (2,  1,  "Academy Awards",         "Best Foreign Language Film",   1952, "Nominated"),
    (3,  2,  "Venice Film Festival",   "Silver Lion",                  1954, "Won"),
    (4,  3,  "Palme d'Or",             "Best Film",                    1960, "Won"),
    (5,  4,  "Academy Awards",         "Best Costume Design",          1964, "Won"),
    (6,  5,  "BAFTA",                  "Best Film",                    1958, "Nominated"),
    (7,  7,  "Academy Awards",         "Best Visual Effects",          1969, "Won"),
    (8,  7,  "BAFTA",                  "Best Film",                    1969, "Won"),
    (9,  8,  "Venice Film Festival",   "Jury Special Prize",           1971, "Won"),
    (10, 9,  "BAFTA",                  "Best Screenplay",              1961, "Won"),
    (11, 11, "Academy Awards",         "Best Picture",                 1942, "Nominated"),
    (12, 11, "Academy Awards",         "Best Director",                1942, "Nominated"),
    (13, 12, "National Board of Review","Top Ten Films",               1958, "Won"),
    (14, 13, "Academy Awards",         "Best Picture",                 1973, "Won"),
    (15, 13, "Academy Awards",         "Best Director",                1973, "Nominated"),
    (16, 14, "Palme d'Or",             "Best Film",                    1979, "Won"),
    (17, 15, "Palme d'Or",             "Best Film",                    1976, "Won"),
    (18, 16, "Academy Awards",         "Best Picture",                 1991, "Nominated"),
    (19, 16, "BAFTA",                  "Best Film",                    1991, "Nominated"),
    (20, 17, "Cannes Film Festival",   "FIPRESCI Prize",               1969, "Won"),
    (21, 18, "BAFTA",                  "Best Foreign Language Film",   1980, "Nominated"),
    (22, 19, "Hong Kong Film Awards",  "Best Director",                2001, "Won"),
    (23, 19, "Cannes Film Festival",   "Best Soundtrack",              2001, "Won"),
    (24, 21, "Academy Awards",         "Best Foreign Language Film",   2000, "Won"),
    (25, 22, "Academy Awards",         "Best Original Screenplay",     2003, "Won"),
    (26, 22, "Goya Awards",            "Best Film",                    2002, "Won"),
    (27, 24, "Palme d'Or",             "Best Film",                    1997, "Won"),
    (28, 25, "Academy Awards",         "Best Cinematography",          1979, "Nominated"),
    (29, 26, "Palme d'Or",             "Best Film",                    2011, "Won"),
    (30, 28, "Cannes Film Festival",   "Best Director",                2001, "Won"),
    (31, 29, "Prix Louis Delluc",      "Best French Film",             1962, "Won"),
    (32, 33, "Sight & Sound Poll",     "Greatest Film of All Time",    2022, "Won"),
    (33, 35, "Cannes Film Festival",   "Best Human Document",          1956, "Won"),
    (34, 36, "National Film Award",    "Best Film",                    1960, "Won"),
    (35, 38, "Academy Awards",         "Best Foreign Language Film",   1975, "Won"),
    (36, 45, "Academy Awards",         "Best Picture",                 1975, "Won"),
    (37, 46, "Academy Awards",         "Best Actor",                   1981, "Nominated"),
    (38, 47, "Cannes Film Festival",   "FIPRESCI Prize",               1980, "Won"),
    (39, 57, "Palme d'Or",             "Best Film",                    1980, "Won"),
    (40, 60, "Venice Film Festival",   "Special Jury Prize",           1999, "Won"),
]
awards_rows = [
    {"award_id": a[0], "film_id": a[1], "award_name": a[2], "category": a[3], "year": a[4], "outcome": a[5]}
    for a in awards_data
]
write_csv("awards.csv", ["award_id","film_id","award_name","category","year","outcome"], awards_rows)

# ─────────────────────────────────────────────
# 12. USERS  (password_hash, created_at, role)
# ─────────────────────────────────────────────
usernames = [
    ("cinephile_pk",   "cinephile@example.com",  "user"),
    ("reelcritic",     "reelcritic@example.com", "user"),
    ("shadowplay",     "shadowplay@example.com", "user"),
    ("kurosawa_fan",   "kfan@example.com",       "user"),
    ("nouvelle_vague", "nv@example.com",         "user"),
    ("admin_alice",    "alice@cinetrace.io",      "admin"),
    ("admin_bob",      "bob@cinetrace.io",        "admin"),
    ("tarkovsky_zone", "tzone@example.com",       "user"),
    ("filmrat",        "filmrat@example.com",     "user"),
    ("cinematheque",   "ct@example.com",          "user"),
    ("parallax_view",  "parallax@example.com",    "user"),
    ("deep_focus",     "deepfocus@example.com",   "user"),
    ("auteur_watch",   "auteur@example.com",       "user"),
    ("iris_diaphragm", "iris@example.com",        "user"),
    ("jump_cut",       "jumpcut@example.com",     "user"),
    ("long_take",      "longtake@example.com",    "user"),
    ("rack_focus",     "rackfocus@example.com",   "user"),
    ("dutch_angle",    "dutch@example.com",       "user"),
    ("mise_en_scene",  "mise@example.com",        "user"),
    ("tracking_shot",  "tracking@example.com",    "user"),
]
users_rows = []
for i, (uname, email, role) in enumerate(usernames, 1):
    pw_hash = hashlib.sha256(f"password_{uname}".encode()).hexdigest()
    users_rows.append({
        "user_id": i, "username": uname, "email": email,
        "password_hash": pw_hash, "role": role,
        "created_at": random_ts(2019, 2023)
    })
write_csv("users.csv", ["user_id","username","email","password_hash","role","created_at"], users_rows)

# ─────────────────────────────────────────────
# 13. REVIEWS  (body not review_text, is_flagged, created_at)
# ─────────────────────────────────────────────
review_bodies = {
    1:  "Rashomon's layered unreliability is breathtaking. Every retelling shifts the moral ground beneath your feet.",
    2:  "Seven Samurai is a masterclass in ensemble storytelling. The final battle is still unmatched in cinema.",
    7:  "2001 demands patience but rewards it with images that burn into the mind. HAL remains the most chilling AI in film.",
    9:  "Breathless invented a new cinematic vocabulary. Its restless energy still feels contemporary.",
    11: "Citizen Kane earns every superlative. The depth-of-field work alone changed how films are made.",
    13: "The Godfather is not just the greatest crime film. It is one of the greatest films about power, loyalty, and loss.",
    19: "In the Mood for Love is among the most achingly beautiful films ever made. Doyle's cinematography is transcendent.",
    33: "Jeanne Dielman is one of the most radical acts of feminist filmmaking. Its slow accumulation is devastating.",
    35: "Pather Panchali moves with the weight of lived experience. Ray's humanism is unmatched.",
    18: "Stalker's Zone is the ultimate cinematic metaphor for desire and fear. A hypnotic, demanding masterpiece.",
}
reviews_rows = []
review_id = 1
film_ids_all = [f[0] for f in films_data]
for user in users_rows:
    if user["role"] == "admin":
        continue
    sample_films = random.sample(film_ids_all, k=random.randint(3, 8))
    for fid in sample_films:
        body = review_bodies.get(fid, f"A remarkable film that continues to reward on repeated viewings. Essential world cinema.")
        reviews_rows.append({
            "review_id": review_id,
            "user_id": user["user_id"],
            "film_id": fid,
            "body": body,
            "rating": random.randint(6, 10),
            "created_at": random_ts(2020, 2024),
            "is_flagged": 0
        })
        review_id += 1

# Add a couple of flagged reviews
reviews_rows[5]["is_flagged"] = 1
reviews_rows[12]["is_flagged"] = 1

write_csv("reviews.csv",
    ["review_id","user_id","film_id","body","rating","created_at","is_flagged"],
    reviews_rows)

# ─────────────────────────────────────────────
# 14. WATCHLISTS  (list_id, list_name, is_public)
# ─────────────────────────────────────────────
watchlist_names = [
    "New Wave Essentials", "Tarkovsky Road", "Feminist Masterpieces",
    "Japanese Classics", "Crime & Punishment", "African Cinema Gems",
    "Philosophical Cinema", "All-Time Favourites", "Hidden Gems",
    "Cinematography Showcase", "Award Winners", "Personal Watchlist",
    "Long Takes", "Double Features", "Road to Cannes",
]
watchlists_rows = []
wl_id = 1
user_watchlists = {}
for user in users_rows:
    n = random.randint(1, 3)
    user_watchlists[user["user_id"]] = []
    for _ in range(n):
        name = random.choice(watchlist_names)
        is_public = random.choice([0, 1])
        watchlists_rows.append({
            "list_id": wl_id, "user_id": user["user_id"],
            "list_name": name, "is_public": is_public,
            "created_at": random_ts(2020, 2024)
        })
        user_watchlists[user["user_id"]].append(wl_id)
        wl_id += 1
write_csv("watchlists.csv", ["list_id","user_id","list_name","is_public","created_at"], watchlists_rows)

# ─────────────────────────────────────────────
# 15. WATCHLIST_ITEMS  (list_id, film_id, added_at)
# ─────────────────────────────────────────────
watchlist_items_set = set()
watchlist_items_rows = []
for wl in watchlists_rows:
    lid = wl["list_id"]
    for fid in random.sample(film_ids_all, k=random.randint(3, 10)):
        if (lid, fid) not in watchlist_items_set:
            watchlist_items_set.add((lid, fid))
            watchlist_items_rows.append({
                "list_id": lid, "film_id": fid,
                "added_at": random_ts(2020, 2024)
            })
write_csv("watchlist_items.csv", ["list_id","film_id","added_at"], watchlist_items_rows)

# ─────────────────────────────────────────────
# 16. INFLUENCE_VOTES  (vote_id, link_id, user_id, vote, voted_at)
# ─────────────────────────────────────────────
votes_set = set()
votes_rows = []
vote_id = 1
link_ids = [il[0] for il in influence_links_data]
for user in users_rows:
    sample_links = random.sample(link_ids, k=random.randint(4, 10))
    for lid in sample_links:
        if (lid, user["user_id"]) not in votes_set:
            votes_set.add((lid, user["user_id"]))
            votes_rows.append({
                "vote_id": vote_id, "link_id": lid,
                "user_id": user["user_id"],
                "vote": random.choice([1, 1, 1, -1]),  # mostly upvotes
                "voted_at": random_ts(2021, 2024)
            })
            vote_id += 1
write_csv("influence_votes.csv", ["vote_id","link_id","user_id","vote","voted_at"], votes_rows)

# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
print(f"\n✅ All CSVs written to {OUTPUT_DIR}")
all_files = sorted(os.listdir(OUTPUT_DIR))
print(f"   {len(all_files)} files: {', '.join(all_files)}")
