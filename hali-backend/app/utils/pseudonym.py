import secrets

ADJECTIVES = [
    "calm", "gentle", "swift", "quiet", "bright", "still", "serene", "resilient",
    "steady", "brave", "peaceful", "patient", "hopeful", "mindful", "warm", "kind",
    "noble", "sage", "humble", "radiant", "amber", "golden", "silver", "azure"
]

NOUNS = [
    "acacia", "baobab", "mango", "river", "savanna", "lantern", "valley", "cedar",
    "highland", "crane", "breeze", "dawn", "dusk", "hill", "lake", "mara",
    "rift", "tsavo", "amboseli", "flame", "star", "oasis", "forest", "peak"
]


def generate_anon_handle() -> str:
    """Generate a privacy-preserving handle (e.g. 'calm-acacia-42')."""
    adj = secrets.choice(ADJECTIVES)
    noun = secrets.choice(NOUNS)
    num = secrets.randbelow(900) + 100  # 100 to 999
    return f"{adj}-{noun}-{num}"

