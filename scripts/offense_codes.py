"""LAPD Crm Cd crosswalk for violent / property outcomes.

Categories are mutually exclusive: violent takes priority over property.

violent_ucr  — UCR Part I violent-style offenses (homicide, rape, robbery,
               aggravated assault, and closely related Part-1 sexual assaults /
               shots-fired codes).

violent      — broader interpersonal-violence series used as the preferred
               outcome: violent_ucr plus simple assault / battery / IPV,
               brandishing, criminal threats, kidnapping, stalking, etc.

property     — street property crime: burglary, larceny/theft, vehicle theft,
               arson, vandalism. Fraud / identity theft / bunco / embezzlement
               are intentionally excluded (not the heat-exposure channel).
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
