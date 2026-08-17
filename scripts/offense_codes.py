"""LAPD Crm Cd crosswalk for violent / property outcomes and mechanism subcategories.

Top-level categories (violent, property, other) are mutually exclusive:
violent takes priority over property.

Mechanism subcategories partition within their parent where possible:
  violent  → interpersonal, robbery  (disjoint)
  property → theft, burglary, vehicle_theft  (disjoint)
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

# Street property crime
PROPERTY = frozenset({
    310, 320, 330, 410,           # burglary (+ from vehicle / attempted)
    331, 341, 343, 345, 350, 351, 352, 353,
    420, 421, 440, 441, 442, 443, 444, 445, 450, 451, 452, 453,
    470, 471, 472, 473, 474, 475,
    480, 485, 487,                # bike / boat stolen
    510, 520, 522,                # vehicle stolen
    648,                          # arson
    740, 745,                     # vandalism
})

# --- Mechanism subcategories (disjoint within parent) ---

# Interpersonal / affective violence: assault, battery, IPV, threats
INTERPERSONAL = frozenset({
    622, 623, 624, 625, 626, 627,  # battery / simple assault / IPV / child
    230, 231, 235, 236,           # aggravated assault
    860,                          # battery with sexual contact
    928, 930,                     # threatening calls / criminal threats
})

ROBBERY = frozenset({210, 220})

BURGLARY = frozenset({310, 320, 330, 410})

VEHICLE_THEFT = frozenset({510, 520, 522, 480, 485, 487})

THEFT = frozenset({
    331, 341, 343, 345, 350, 351, 352, 353,
    420, 421, 440, 441, 442, 443, 444, 445, 450, 451, 452, 453,
    470, 471, 472, 473, 474, 475,
    648,                          # arson (opportunity channel)
    740, 745,                     # vandalism
})

MECHANISM_OUTCOMES = [
    "violent", "violent_ucr", "interpersonal", "robbery",
    "property", "theft", "burglary", "vehicle_theft",
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
    """Return mechanism subcategory or parent category label."""
    try:
        c = int(code)
    except (TypeError, ValueError):
        return "other"
    if c in INTERPERSONAL:
        return "interpersonal"
    if c in ROBBERY:
        return "robbery"
    if c in BURGLARY:
        return "burglary"
    if c in VEHICLE_THEFT:
        return "vehicle_theft"
    if c in THEFT:
        return "theft"
    parent = classify_code(c)
    if parent == "violent":
        return "violent_other"
    if parent == "property":
        return "property_other"
    return "other"


def mechanism_sets():
    """Return {category: frozenset of codes} for classification table."""
    return {
        "violent": VIOLENT,
        "violent_ucr": VIOLENT_UCR,
        "interpersonal": INTERPERSONAL,
        "robbery": ROBBERY,
        "property": PROPERTY,
        "theft": THEFT,
        "burglary": BURGLARY,
        "vehicle_theft": VEHICLE_THEFT,
    }
