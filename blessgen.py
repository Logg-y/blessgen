import utils
import fileparser
import random
import copy
import sys
import os
import traceback
from blessgenerationsettings import BlessGenerationSettings

ver = "1.0.5"

def _parseDataFiles():
    if len(utils.blesseffects) < 0:
        return
    utils.loadEffectLabels()
    return fileparser.blesstemplate.readEffectsFromDir("./data/blesseffects")

class BlessGenerator(object):
    def __init__(self, **options):
        self.blessEffectPool = _parseDataFiles()
        self.options = options
        self.numToGenerate = options.get("numtogenerate", 99)
        self.blessEffectsByPath = {}
        self.blessEffectsByCrosspath = {}
        self.crosspathChance = options.get("crosspathchance", 20)
        self.modoutput = ""
        self.combinationTolerance = 0

        for path in range(0, 8):
            self.blessEffectsByPath[path] = {}
            for level in range(1, 11):
                self.blessEffectsByPath[path][level] = []
            for crossPath in range(path+1, 8):
                crossPathSet = frozenset((path, crossPath))
                self.blessEffectsByCrosspath[crossPathSet] = []

        self._cachedCombinationPool = None
        self._lastLowestEffectCount = None

    def _buildRarestCombinationPool(self):
        lowestEffectCount = None
        pathAndLevelCombinationPool = []
        # Work out what the lowest number of effects for all combos is
        for path, pathsBlessEffectsByLevel in self.blessEffectsByPath.items():
            for level, blessList in pathsBlessEffectsByLevel.items():
                numEffects = len(blessList)
                if level < 5:
                    numEffects -= 1
                if lowestEffectCount is None or numEffects < lowestEffectCount:
                    lowestEffectCount = numEffects
        for crossPathSet, spellList in self.blessEffectsByCrosspath.items():
            numEffects = len(blessList)
            if numEffects < lowestEffectCount:
                lowestEffectCount = numEffects
        if self._lastLowestEffectCount is not None and lowestEffectCount != self._lastLowestEffectCount:
            print(f"New lowest effect count = {lowestEffectCount} (old was {self._lastLowestEffectCount}), reset tolerance")
            self.combinationTolerance = 0

        # Now select anything within the given tolerance
        for path, pathsBlessEffectsByLevel in self.blessEffectsByPath.items():
            for level, blessList in pathsBlessEffectsByLevel.items():
                numEffects = len(blessList)
                # Give more non-incarnate effects
                if level < 5:
                    numEffects -= 2
                if numEffects - lowestEffectCount <= self.combinationTolerance:
                    combo = BlessGenerationSettings(path, None, level)
                    pathAndLevelCombinationPool.append(combo)
        for crossPathSet, spellList in self.blessEffectsByCrosspath.items():
            numEffects = len(blessList)
            if numEffects - lowestEffectCount <= self.combinationTolerance:
                combo = BlessGenerationSettings(*list(crossPathSet), None)
                pathAndLevelCombinationPool.append(combo)
                combo = BlessGenerationSettings(*reversed(list(crossPathSet)), None)
                pathAndLevelCombinationPool.append(combo)
        self._cachedCombinationPool = pathAndLevelCombinationPool
        random.shuffle(self._cachedCombinationPool)
        self._lastLowestEffectCount = lowestEffectCount
        print(f"Possible path combination pool contains {len(self._cachedCombinationPool)} items!")

    def selectBlessSettings(self):
        if self._cachedCombinationPool is None:
            self._buildRarestCombinationPool()
        if len(self._cachedCombinationPool) == 0:
            self.combinationTolerance += 1
            self._buildRarestCombinationPool()
            if self.combinationTolerance > 5:
                raise ValueError("Failed to build an effect from the least common path/level combination pool")
        # Skew even further to nonincarnate (or lesser primary path cost effects)
        tries = 0
        while True:
            settings = self._cachedCombinationPool.pop()
            if tries >= 10:
                break
            if settings.primarypath > 4:
                skipchance = 10 + (settings.primarypath*5)
                if random.random() * 100 < skipchance:
                    self._cachedCombinationPool.append(settings)
                    tries += 1
                    continue
            break

        return settings

    def generateBless(self, settings):
        print(f"Generate bless with settings: {settings}... ({len(self._cachedCombinationPool)} remain)")
        attempt = 1
        bless = None
        while 1:
            effectPool = copy.copy(list(self.blessEffectPool.values()))
            random.shuffle(effectPool)
            settings.allowskipchance = attempt < 2
            while 1:
                if len(effectPool) == 0:
                    break
                effect = effectPool.pop()
                if attempt == 1 and random.random() * 100 < effect.skipchance:
                    continue
                print(f"Try effect {effect.name}... ({len(effectPool)} remain)")
                bless = effect.generateBless(settings)
                if bless is not None:
                    break
            if bless is not None:
                break
            if attempt >= 2:
                return False
            attempt += 1

        if bless is not None:
            if bless.path2 == -1:
                self.blessEffectsByPath[bless.path1][bless.path1level].append(bless)
            else:
                crosspathset = frozenset((bless.path1, bless.path2))
                self.blessEffectsByCrosspath[crosspathset].append(bless)
            self.modoutput += bless.output()
            return True

    def generateAll(self):
        for x in range(0, self.numToGenerate):
            while 1:
                settings = self.selectBlessSettings()
                if self.generateBless(settings):
                    break

def main(**options):
    utils.START_UNIT_ID = options.get("startunitid", 3501)
    gen = BlessGenerator(**options)
    gen.generateAll()
    if not os.path.isdir("./output"):
        os.mkdir("./output")
    outfp = options.get("outfp", None)
    if outfp is None:
        outfp = f"blessgen-{random.random()}.dbm"
    if not outfp.endswith(".dbm"):
        outfp += ".dbm"
    with open(os.path.join("./output", os.path.basename(outfp)), "w", encoding="utf-8") as f:
        f.write(gen.modoutput)


if __name__ == "__main__":
    n = input("Enter mod name:")
    oldstdout = sys.stdout
    log = open("log.txt", "w", encoding="u8")
    sys.stdout = log
    if len(n) == 0:
        n = None
    try:
        main(outfp=n)
    except Exception:
        print(traceback.format_exc())
        sys.stdout = oldstdout
        oldstdout.write(traceback.format_exc())
        input("Failed. Press ENTER to exit.")
    sys.stdout = oldstdout
    input("Complete! Press ENTER to exit.")
