import re

START_BLESS_ID = 1
START_UNIT_ID = 3501
blesseffects = {}
EFFECT_IDS_TO_LABELS = {}

def loadEffectLabels():
    global EFFECT_IDS_TO_LABELS
    if len(EFFECT_IDS_TO_LABELS) == 0:
        with open("effectenum.txt", "r", encoding="utf8") as f:
            for line in f:
                if line.strip() == "":
                    continue
                m = re.match("\\W*(.*)=(\\d*)", line)
                if m is None:
                    raise ValueError(f"Bad effect enum line: {line}")
                effectID = int(m.group(2))
                effectLabel = m.group(1)
                print(f"{effectID} -> {effectLabel}")
                EFFECT_IDS_TO_LABELS[effectID] = effectLabel

def _selectFlag(flagpool, allowed):
    "From flagpool, chooses one bitflag at random which is specified in allowed. Returns None if there were no flags to return"
    l = []
    for x in flagpool:
        if x.value > -1:
            if allowed & x:
                l.append(x)
    if len(l) == 0:
        return None
    return random.choice(l)


def breakdownflag(flag):
    "Split a given bitflag into a list of exponents such that sum([2 ** x for x in breakdownflag(flag)]) == flag"
    n = 0
    out = []
    while 1:
        if 2 ** n > flag: return out
        if flag & 2 ** n: out.append(n)
        n += 1

def breakdownflagcomponents(flag):
    "Split a given bitflag into a list of its components, such that sum(breakdownflag(flag)) == flag"
    n = 0
    out = []
    while 1:
        if 2 ** n > flag: return out
        if flag & 2 ** n: out.append(2**n)
        n += 1


def pathstotext(path: int) -> str:
    acc = ""
    if path & PathFlags.FIRE:
        acc += "F"
    if path & PathFlags.AIR:
        acc += "A"
    if path & PathFlags.WATER:
        acc += "W"
    if path & PathFlags.EARTH:
        acc += "E"
    if path & PathFlags.ASTRAL:
        acc += "S"
    if path & PathFlags.DEATH:
        acc += "D"
    if path & PathFlags.NATURE:
        acc += "N"
    if path & PathFlags.BLOOD:
        acc += "B"
    if acc == "":
        acc += "_"
    return acc


def _writetoconsole(line):
    """Because PyInstaller and PySimpleGUI don't play nice unless specifying STDIN as well, I had to make
    this be converted to exe with --window to avoid the console coming up.
    For some reason after doing that, sys.stderr has to be flushed after every line to allow the GUI process
    to pick it up"""
    sys.stderr.write(line)
    sys.stderr.flush()
