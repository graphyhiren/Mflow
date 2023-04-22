import random
import uuid
import hashlib

_EXPERIMENT_ID_FIXED_WIDTH = 18


def _generate_unique_integer_id():
    """
    Utility function for generating a random fixed-length integer
    :param id_length: The target length of the string representation of the integer without
                      leading zeros
    :return: a fixed-width integer
    """

    random_int = uuid.uuid4().int
    # Cast to string to get a fixed length
    random_str = str(random_int)[-_EXPERIMENT_ID_FIXED_WIDTH:]
    # append a random int as string to the end of the generated string for as many
    # leading zeros exist in the generated string in order to preserve the total length
    # once cast back to int
    for s in random_str:
        if s == "0":
            random_str = random_str + str(random.randint(0, 9))
        else:
            break
    return int(random_str)


def _generate_string(sep, integer_scale):
    predicate = random.choice(_GENERATOR_PREDICATES).lower()
    noun = random.choice(_GENERATOR_NOUNS).lower()
    num = random.randint(0, 10**integer_scale)
    return f"{predicate}{sep}{noun}{sep}{num}"


def _generate_random_name(sep="-", integer_scale=3, max_length=20):
    """Helper function for generating a random predicate, noun, and integer combination

    :param sep: String separator for word spacing
    :param integer_scale: dictates the maximum scale range for random integer sampling (power of 10)
    :param max_length: maximum allowable string length

    :return: A random string phrase comprised of a predicate, noun, and random integer
    """
    name = None
    for _ in range(10):
        name = _generate_string(sep, integer_scale)
        if len(name) <= max_length:
            return name
    # If the combined length isn't below the threshold after 10 iterations, truncate it.
    return name[:max_length]


def _generate_dataset_name(digest: str) -> str:
    """
    Generates a unique name for a dataset logged to MLflow Tracking.

    **IMPORTANT: This function is meant to generate a deterministic name for a specified
    dataset digest across MLflow versions. Be **very** careful if editing this function,
    and do not change the deterministic mapping behavior from digest to name; otherwise,
    user workflows may break.**

    :param digest: The dataset digest, e.g. "9ff17540".
    :return: A dataset name of the form <predicate>-data-<integer>, e.g. "unique-data-954".
    """
    assert (
        _GENERATOR_DATASET_INTEGER_UPPER_BOUND * len(_GENERATOR_DATASET_PREDICATES)
        > _GENERATOR_DATASET_DIGEST_MODULO_DIVISOR
    ), "Internal error: MLflow does not define enough unique dataset names."

    # Use a prime number as the modulus when mapping the diges to a name index in order to reduce
    # the likelihood of collisions
    md5_hash = hashlib.md5(digest.encode("utf-8"))
    int_hash = int(md5_hash.hexdigest(), 16)
    name_index = int_hash % _GENERATOR_DATASET_DIGEST_MODULO_DIVISOR
    predicate_index = name_index // _GENERATOR_DATASET_INTEGER_UPPER_BOUND
    predicate = _GENERATOR_DATASET_PREDICATES[predicate_index]
    name_integer_component = name_index % _GENERATOR_DATASET_INTEGER_UPPER_BOUND

    return f"{predicate}-data-{name_integer_component}"


_GENERATOR_NOUNS = [
    "ant",
    "ape",
    "asp",
    "auk",
    "bass",
    "bat",
    "bear",
    "bee",
    "bird",
    "boar",
    "bug",
    "calf",
    "carp",
    "cat",
    "chimp",
    "cod",
    "colt",
    "conch",
    "cow",
    "crab",
    "crane",
    "croc",
    "crow",
    "cub",
    "deer",
    "doe",
    "dog",
    "dolphin",
    "donkey",
    "dove",
    "duck",
    "eel",
    "elk",
    "fawn",
    "finch",
    "fish",
    "flea",
    "fly",
    "foal",
    "fowl",
    "fox",
    "frog",
    "gnat",
    "gnu",
    "goat",
    "goose",
    "grouse",
    "grub",
    "gull",
    "hare",
    "hawk",
    "hen",
    "hog",
    "horse",
    "hound",
    "jay",
    "kit",
    "kite",
    "koi",
    "lamb",
    "lark",
    "loon",
    "lynx",
    "mare",
    "midge",
    "mink",
    "mole",
    "moose",
    "moth",
    "mouse",
    "mule",
    "newt",
    "owl",
    "ox",
    "panda",
    "penguin",
    "perch",
    "pig",
    "pug",
    "quail",
    "ram",
    "rat",
    "ray",
    "robin",
    "roo",
    "rook",
    "seal",
    "shad",
    "shark",
    "sheep",
    "shoat",
    "shrew",
    "shrike",
    "shrimp",
    "skink",
    "skunk",
    "sloth",
    "slug",
    "smelt",
    "snail",
    "snake",
    "snipe",
    "sow",
    "sponge",
    "squid",
    "squirrel",
    "stag",
    "steed",
    "stoat",
    "stork",
    "swan",
    "tern",
    "toad",
    "trout",
    "turtle",
    "vole",
    "wasp",
    "whale",
    "wolf",
    "worm",
    "wren",
    "yak",
    "zebra",
]

_GENERATOR_PREDICATES = [
    "abundant",
    "able",
    "abrasive",
    "adorable",
    "adaptable",
    "adventurous",
    "aged",
    "agreeable",
    "ambitious",
    "amazing",
    "amusing",
    "angry",
    "auspicious",
    "awesome",
    "bald",
    "beautiful",
    "bemused",
    "bedecked",
    "big",
    "bittersweet",
    "blushing",
    "bold",
    "bouncy",
    "brawny",
    "bright",
    "burly",
    "bustling",
    "calm",
    "capable",
    "carefree",
    "capricious",
    "caring",
    "casual",
    "charming",
    "chill",
    "classy",
    "clean",
    "clumsy",
    "colorful",
    "crawling",
    "dapper",
    "debonair",
    "dashing",
    "defiant",
    "delicate",
    "delightful",
    "dazzling",
    "efficient",
    "enchanting",
    "entertaining",
    "enthused",
    "exultant",
    "fearless",
    "flawless",
    "fortunate",
    "fun",
    "funny",
    "gaudy",
    "gentle",
    "gifted",
    "glamorous",
    "grandiose",
    "gregarious",
    "handsome",
    "hilarious",
    "honorable",
    "illustrious",
    "incongruous",
    "indecisive",
    "industrious",
    "intelligent",
    "inquisitive",
    "intrigued",
    "invincible",
    "judicious",
    "kindly",
    "languid",
    "learned",
    "legendary",
    "likeable",
    "loud",
    "luminous",
    "luxuriant",
    "lyrical",
    "magnificent",
    "marvelous",
    "masked",
    "melodic",
    "merciful",
    "mercurial",
    "monumental",
    "mysterious",
    "nebulous",
    "nervous",
    "nimble",
    "nosy",
    "omniscient",
    "orderly",
    "overjoyed",
    "peaceful",
    "painted",
    "persistent",
    "placid",
    "polite",
    "popular",
    "powerful",
    "puzzled",
    "rambunctious",
    "rare",
    "rebellious",
    "respected",
    "resilient",
    "righteous",
    "receptive",
    "redolent",
    "resilient",
    "rogue",
    "rumbling",
    "salty",
    "sassy",
    "secretive",
    "selective",
    "sedate",
    "serious",
    "shivering",
    "skillful",
    "sincere",
    "skittish",
    "silent",
    "smiling",
    "sneaky",
    "sophisticated",
    "spiffy",
    "stately",
    "suave",
    "stylish",
    "tasteful",
    "thoughtful",
    "thundering",
    "traveling",
    "treasured",
    "trusting",
    "unequaled",
    "upset",
    "unique",
    "unleashed",
    "useful",
    "upbeat",
    "unruly",
    "valuable",
    "vaunted",
    "victorious",
    "welcoming",
    "whimsical",
    "wistful",
    "wise",
    "worried",
    "youthful",
    "zealous",
]


# Unique dataset names are generated from dataset digests by mapping the digest to an integer
# and applying the modulo operation with a prime divisor to obtain an index. A prime divisor
# is used to reduce the likelihood of collisions. This index is then mapped to a predicate
# (e.g. "unique") and an integer in the range [0, 10000) (e.g. 954). Finally, the dataset name
# is constructed as <predicate>-data-<integer> (e.g. unique-data-954)
_GENERATOR_DATASET_DIGEST_MODULO_DIVISOR = 2499997
_GENERATOR_DATASET_INTEGER_UPPER_BOUND = 10**4
_GENERATOR_DATASET_PREDICATES = [
    "acute",
    "adept",
    "admired",
    "adroit",
    "aerial",
    "agile",
    "amazing",
    "amiable",
    "ample",
    "angelic",
    "animated",
    "apt",
    "artful",
    "assured",
    "astute",
    "atomic",
    "avid",
    "awesome",
    "beaming",
    "blazing",
    "blissful",
    "bold",
    "brainy",
    "brave",
    "breezy",
    "bright",
    "brisk",
    "buoyant",
    "candid",
    "canny",
    "charming",
    "cheerful",
    "cheery",
    "chipper",
    "clever",
    "cozy",
    "creative",
    "crisp",
    "curious",
    "daring",
    "dashing",
    "dazzled",
    "dazzling",
    "decisive",
    "devoted",
    "diligent",
    "distinct",
    "diverse",
    "divine",
    "driven",
    "durable",
    "dynamic",
    "earnest",
    "effusive",
    "elated",
    "electric",
    "elegant",
    "elite",
    "elusive",
    "eminent",
    "epic",
    "esteemed",
    "ethical",
    "exalted",
    "exciting",
    "fancy",
    "festive",
    "fiery",
    "flawless",
    "fluent",
    "foggy",
    "fond",
    "fresh",
    "friendly",
    "funky",
    "gallant",
    "genial",
    "genuine",
    "gifted",
    "glorious",
    "glowing",
    "graceful",
    "gracious",
    "grateful",
    "groovy",
    "happy",
    "helpful",
    "heroic",
    "holistic",
    "honest",
    "honored",
    "hopeful",
    "humane",
    "humble",
    "humorous",
    "iconic",
    "ideal",
    "idyllic",
    "immense",
    "imminent",
    "infinite",
    "informed",
    "inherent",
    "inspired",
    "intense",
    "intrepid",
    "inviting",
    "ironclad",
    "jaunty",
    "jazzy",
    "jocular",
    "jocund",
    "jolly",
    "jovial",
    "joyful",
    "jubilant",
    "jumpy",
    "keen",
    "kind",
    "kindred",
    "knowing",
    "lavish",
    "learned",
    "legible",
    "likeable",
    "lively",
    "logical",
    "loyal",
    "lucky",
    "luminous",
    "magical",
    "magnetic",
    "majestic",
    "mellow",
    "merry",
    "mindful",
    "mirthful",
    "modern",
    "modest",
    "moving",
    "myriad",
    "mystical",
    "nascent",
    "natural",
    "nifty",
    "nimble",
    "noble",
    "notable",
    "novel",
    "nuanced",
    "patient",
    "peaceful",
    "placid",
    "playful",
    "pleasant",
    "poetic",
    "polished",
    "popular",
    "powerful",
    "precise",
    "pristine",
    "prompt",
    "proper",
    "proud",
    "prudent",
    "purposed",
    "quaint",
    "quality",
    "quick",
    "quiet",
    "quirky",
    "radiant",
    "rare",
    "rational",
    "refined",
    "regal",
    "relevant",
    "reliable",
    "resolute",
    "revered",
    "robust",
    "rustic",
    "salient",
    "sensible",
    "serene",
    "shiny",
    "sincere",
    "skillful",
    "sleek",
    "slick",
    "smart",
    "snazzy",
    "soaring",
    "solid",
    "soulful",
    "sound",
    "special",
    "spiffy",
    "spirited",
    "splendid",
    "stately",
    "steady",
    "stellar",
    "storied",
    "striking",
    "strong",
    "stunning",
    "sublime",
    "sunny",
    "superb",
    "supreme",
    "swift",
    "tactful",
    "talented",
    "tangible",
    "tasteful",
    "terrific",
    "thriving",
    "timely",
    "tolerant",
    "tranquil",
    "trusty",
    "truthful",
    "unerring",
    "unique",
    "united",
    "uplifted",
    "useful",
    "valiant",
    "valuable",
    "varied",
    "vast",
    "vaunted",
    "viable",
    "vibrant",
    "vigilant",
    "vital",
    "vivid",
    "winsome",
    "wise",
    "wistful",
    "witty",
    "wizardly",
    "wondrous",
    "wordly",
    "worthy",
    "zany",
    "zesty",
    "zingy",
    "zippy",
]
