"""LAPD Crm Cd crosswalk for violent / property outcomes and mechanism subcategories.

Top-level categories (violent, property, other) are mutually exclusive:
violent takes priority over property. These definitions are unchanged so that
`03_analyze.py` and the spatial pipeline stay comparable across rounds.

Mechanism subcategories (v2) partition their parent exactly:
  violent  → interpersonal, robbery, violent_other
  property → theft, structure_burglary, vehicle_burglary,
             motor_vehicle_theft, vandalism, arson

v2 changes vs v1: vandalism and arson are no longer folded into `theft`;
burglary is split into structure vs vehicle; vehicle theft is restricted to
motor vehicles (bike/boat moved into general theft).
"""

# UCR Part I–style violent
VIOLENT_UCR = frozenset({
    110, 113,                 # homicide / manslaughter
    121, 122,                 # rape
    210, 220,                 # robbery
    230, 231, 235, 236,       # aggravated assault (ADW, child, IPV)
    250, 251,                 # shots fired at vehicle / dwelling
    815, 820, 821,            # sexual penetration / oral / sodomy
})

# Broader interpersonal violence (preferred outcome)
VIOLENT = VIOLENT_UCR | frozenset({
    622, 623, 624, 625, 626, 627,  # battery / simple assault / IPV / child
    647,                          # throwing object at moving vehicle
    753, 761,                     # discharge firearms / brandish weapon
    763,                          # stalking
    860,                          # battery with sexual contact
    910, 920, 921, 922,           # kidnapping / trafficking / child stealing
    928, 930,                     # threatening calls / criminal threats
})

# --- Violence subcategories (disjoint) ---

# Interpersonal violence: assault / battery / IPV / threat offenses.
# Named for the offense content, not for an unobserved affective mechanism.
INTERPERSONAL = frozenset({
    622, 623, 624, 625, 626, 627,  # battery / simple assault / IPV / child
    230, 231, 235, 236,           # aggravated assault
    860,                          # battery with sexual contact
    928, 930,                     # threatening calls / criminal threats
})

ROBBERY = frozenset({210, 220})

# --- Property subcategories (disjoint) ---

STRUCTURE_BURGLARY = frozenset({
    310,                          # burglary
    320,                          # burglary, attempted
})

VEHICLE_BURGLARY = frozenset({
    330,                          # burglary from vehicle
    410,                          # burglary from vehicle, attempted
})

MOTOR_VEHICLE_THEFT = frozenset({
    510,                          # vehicle - stolen
    520,                          # vehicle - attempt stolen
    522,                          # vehicle, stolen - other (scooters etc.)
})

# Theft-type offenses only. Vandalism and arson are excluded (see below).
# Bike / boat theft is retained here rather than in motor-vehicle theft.
THEFT = frozenset({
    331, 341, 343, 345, 350, 351, 352, 353,
    420, 421, 440, 441, 442, 443, 444, 445, 450, 451, 452, 453,
    470, 471, 472, 473, 474, 475,
    480, 485, 487,                # bike / boat stolen
})

VANDALISM = frozenset({740, 745})

ARSON = frozenset({648})

# Street property crime = union of the property subcategories above.
PROPERTY = (
    STRUCTURE_BURGLARY | VEHICLE_BURGLARY | MOTOR_VEHICLE_THEFT
    | THEFT | VANDALISM | ARSON
)

# Core categories for the mechanism analysis.
VIOLENCE_OUTCOMES = ["violent", "violent_ucr", "interpersonal", "robbery"]
OPPORTUNITY_OUTCOMES = [
    "property", "theft", "structure_burglary", "vehicle_burglary",
    "motor_vehicle_theft",
]
OPTIONAL_OUTCOMES = ["vandalism", "arson"]
MECHANISM_OUTCOMES = VIOLENCE_OUTCOMES + OPPORTUNITY_OUTCOMES + OPTIONAL_OUTCOMES

# Subcategory flags stored on the daily panel.
MECHANISM_SUBCATEGORIES = [
    "interpersonal", "robbery", "theft", "structure_burglary",
    "vehicle_burglary", "motor_vehicle_theft", "vandalism", "arson",
]


def classify_code(code) -> str:
    """Return 'violent', 'property', or 'other' (mutually exclusive)."""
    try:
        c = int(code)
    except (TypeError, ValueError):
        return "other"
    if c in VIOLENT:
        return "violent"
    if c in PROPERTY:
        return "property"
    return "other"


def is_violent_ucr(code) -> bool:
    try:
        return int(code) in VIOLENT_UCR
    except (TypeError, ValueError):
        return False


def classify_mechanism(code) -> str:
    """Return the disjoint mechanism subcategory for a Crm Cd."""
    try:
        c = int(code)
    except (TypeError, ValueError):
        return "other"
    for name, codes in (
        ("interpersonal", INTERPERSONAL),
        ("robbery", ROBBERY),
        ("structure_burglary", STRUCTURE_BURGLARY),
        ("vehicle_burglary", VEHICLE_BURGLARY),
        ("motor_vehicle_theft", MOTOR_VEHICLE_THEFT),
        ("vandalism", VANDALISM),
        ("arson", ARSON),
        ("theft", THEFT),
    ):
        if c in codes:
            return name
    parent = classify_code(c)
    if parent == "violent":
        return "violent_other"
    if parent == "property":
        return "property_other"
    return "other"


def mechanism_sets():
    """Return {category: frozenset of codes} for the classification table."""
    return {
        "violent": VIOLENT,
        "violent_ucr": VIOLENT_UCR,
        "interpersonal": INTERPERSONAL,
        "robbery": ROBBERY,
        "property": PROPERTY,
        "theft": THEFT,
        "structure_burglary": STRUCTURE_BURGLARY,
        "vehicle_burglary": VEHICLE_BURGLARY,
        "motor_vehicle_theft": MOTOR_VEHICLE_THEFT,
        "vandalism": VANDALISM,
        "arson": ARSON,
    }


# Parent aggregates: they nest their own subcategories, so no disjointness check.
PARENT_CATEGORIES = ["violent", "violent_ucr", "property"]

# Subcategories that must be mutually disjoint within each group.
_VIOLENCE_SIBLINGS = ["interpersonal", "robbery"]
_PROPERTY_SIBLINGS = [
    "theft", "structure_burglary", "vehicle_burglary",
    "motor_vehicle_theft", "vandalism", "arson",
]

SIBLING_GROUPS = {
    name: [s for s in group if s != name]
    for group in (_VIOLENCE_SIBLINGS, _PROPERTY_SIBLINGS)
    for name in group
}
