import random
from blesseffect import BlessEffect

class BlessTemplate(object):
    def __init__(self, name):
        self.name = name
        self.paths = 0
        self.pathlevel = 0
        self.effect10buffs = 0
        self.multipick = 0
        self.alwaysactive = 0
        self.reqcrosspath = 0
        self.names = {}
        self.skipchance = 0
        self.descr = ""
        self.effects = {}
        self.scaleeffects = {}
        self.posscaleaffinities = {}
        self.negscaleaffinities = {}
        self.maxeffectvalues = {}
        self.generations = []
    def generateBless(self, settings):
        self.settings = settings
        self.blessobj = BlessEffect()
        if settings.allowskipchance and len(self.generations) > 0:
            return None
        if not self._canGenerate():
            return None
        self._assignEffectPaths()
        if self.blessobj.path1 in self.generations:
            print(f"Effect has already generated for this path")
            return None
        self.finalpowerlevel = self._determineFinalPowerlevel()
        if self.finalpowerlevel is None:
            return None
        if not self._determinePathLevels():
            return None
        if not self._scaleToBlesspointCost():
            return None
        self._assignNameToBless()
        self._assignScalesToBless()
        self.generations.append(self.blessobj.path1)
        return self.blessobj
    def _assignScalesToBless(self):
        for scale, aff in self.posscaleaffinities.items():
            amt = aff // 100
            if aff > 0:
                self.blessobj.scales[scale] = amt * -1
        for scale, aff in self.negscaleaffinities.items():
            amt = aff // 100
            if aff > 0:
                self.blessobj.scales[scale] = amt
    def _assignEffectPaths(self):
        if self.settings.primarypath is not None:
            self.blessobj.path1 = self.settings.primarypath
        if self.settings.secondarypath is not None:
            self.blessobj.path2 = self.settings.secondarypath
    def _assignNameToBless(self):
        if 2**self.blessobj.path1 not in self.names:
            raise ValueError(f"Bless {self.name} is missing a name for path {self.blessobj.path1}")
        self.blessobj.name = random.choice(self.names[2**self.blessobj.path1])
    def _determineAllowedPathLevelsAtPowerLevel(self, powerlevel):
        if self.settings.secondarypath is None:
            if not self.reqcrosspath:
                if self.settings.primarypath is not None:
                    self.blessobj.path1level = powerlevel
                    if self._validatePowerLevelAndPathSelection(powerlevel):
                        return [(powerlevel, None)]
                    else:
                        print(f"Failed to generate: primary path only is not valid at given power level")
                        return []
                else:
                    print(f"Failed to generate: no primary path supplied")
                    return []
            else:
                print(f"Failed to generate: this effect requires a crosspath")
                return []
        else:
            out = []
            totalpts = (powerlevel ** 1.2)
            maxdivert = (totalpts // 2)
            possiblediverts = list(range(1, int(maxdivert) - 1))
            for todivert in possiblediverts:
                divertedpts = todivert ** 1.2
                remainingpts = totalpts - divertedpts
                # Check to make sure that this isn't a better outcome than the next check
                # IE: 9 -> 8+1 shouldn't happen when 9 -> 8+2 is possible
                self.blessobj.path1level = int(round(remainingpts ** (1 / 1.2)))
                self.blessobj.path2level = int(round(divertedpts ** (1 / 1.2)))
                print(f"Try diverting {todivert}: uses {divertedpts}, leaves {remainingpts}...")
                print(f"Results in path1lvl = {self.blessobj.path1level}, path2lvl = "
                      f"{self.blessobj.path2level}")
                if todivert != possiblediverts[-1]:
                    nextremaining = totalpts - ((todivert + 1) ** 1.2)
                    if int(round(remainingpts ** (1/1.2))) == int(round(nextremaining ** (1/1.2))):
                        print(f"Invalid. Path1lvl matches that of the next split!")
                        continue

                if self.blessobj.path1level > 10:
                    print(f"Invalid. Results in 11+ path1lvl")
                elif self.blessobj.path2level > 10:
                    print(f"Invalid. Results in 11+ path2lvl")
                elif self.blessobj.path1level >= powerlevel:
                    print(f"Invalid. Results in path1lvl greater than or equal to value before split")
                    continue
                elif self.blessobj.path2level > self.blessobj.path1level:
                    print(f"Invalid. Results in path2lvl > path1lvl")
                    continue
                elif self._validatePowerLevelAndPathSelection(powerlevel):
                    print(f"Valid!")
                    out.append((self.blessobj.path1level, self.blessobj.path2level))
                else:
                    print(f"Invalid: didn't pass power level + path check.")
        return out
    def _determinePathLevels(self):
        possibilities = self._determineAllowedPathLevelsAtPowerLevel(self.finalpowerlevel)
        if len(possibilities) == 0:
            return False
        random.shuffle(possibilities)
        real = possibilities[0]
        self.blessobj.path1level = real[0]
        if real[1] is None:
            self.blessobj.path2level = 0
        else:
            self.blessobj.path2level = real[1]
        return True


    def _canGenerate(self):
        if len(self.scaleeffects) == 0:
            if self.settings.blesspointcost is not None and self.pathlevel != self.settings.blesspointcost:
                print(f"Fail to generate: no way to reach desired blesspoint cost {self.settings.blesspointcost}")
                return False
        if self.settings.blesspointcost is not None and self.pathlevel > self.settings.blesspointcost:
            print(f"Fail to generate: this effect is too expensive for {self.settings.blesspointcost} blesspoints")
            return False
        if self.settings.primarypath is not None and self.paths & (2**self.settings.primarypath) == 0:
            print(f"Fail to generate: missing primary path {self.settings.primarypath}")
            return False
        if self.settings.secondarypath is not None and self.paths & (2**self.settings.secondarypath) == 0:
            print(f"Fail to generate: missing secondary path {self.settings.primarypath}")
            return False
        return True
    def _determineFinalPowerlevel(self):
        if self.settings.blesspointcost is not None:
            if len(self._determineAllowedPathLevelsAtPowerLevel(self.settings.blesspointcost)) > 0:
                allowedpowerlevels = [self.settings.blesspointcost]
            else:
                return None
        else:
            allowedpowerlevels = []
            for powerLevel in range(1, 15):
                print(f"Test at power level {powerLevel}...")
                if len(self._determineAllowedPathLevelsAtPowerLevel(powerLevel)) > 0:
                    allowedpowerlevels.append(powerLevel)
        if len(allowedpowerlevels) == 0:
            print(f"Fail to generate: no valid power levels")
            return None
        ret = random.choice(allowedpowerlevels)
        print(f"Final power level choices: {allowedpowerlevels} -> {ret}")
        return ret
    def _validatePowerLevelAndPathSelection(self, finalpowerlevel):
        powerlevelOverBase = int(round(finalpowerlevel - self.pathlevel))
        if finalpowerlevel < self.pathlevel:
            return False
        if len(self.scaleeffects) == 0 and finalpowerlevel > self.pathlevel:
            return False

        hasRealEffect = False
        for effectID in self.effects:
            if effectID in self.maxeffectvalues:
                if abs(self._getEffectMagnitudeAtPowerLevel(effectID, finalpowerlevel)) > abs(self.maxeffectvalues[effectID]):
                    print(f"Exceeds maximum effect value of {self.maxeffectvalues[effectID]}, cannot generate "
                          f"at PL{finalpowerlevel}")
                    return False

            if self.scaleeffects.get(effectID, 0.0) > 0.0:
                if self._getEffectMagnitudeAtPowerLevel(effectID, finalpowerlevel) != \
                    self._getEffectMagnitudeAtPowerLevel(effectID, finalpowerlevel - 1):
                        print(f"Effect {effectID} has diff magnitude at powerlevels {finalpowerlevel} + {finalpowerlevel-1}")
                        hasRealEffect = True

        if len(self.scaleeffects) > 0 and not hasRealEffect:
            print(f"Power level {finalpowerlevel} doesn't give this effect anything new")
            return False

        if powerlevelOverBase < 0:
            return False
        # Cannot split a path level of 1 into two
        if finalpowerlevel < 2 and self.settings.secondarypath is not None:
            return False
        return True
    def _getEffectMagnitudeAtPowerLevel(self, effectID, finalpowerlevel):
        powerlevelOverBase = int(round(finalpowerlevel - self.pathlevel))
        baseMagnitude = self.effects.get(effectID, 0.0)
        scaleRate = self.scaleeffects.get(effectID, 0.0)
        scaleMagnitude = scaleRate * powerlevelOverBase
        # Extra bit for things turning incarnate that didn't use to be
        if self.pathlevel < 5 and self.blessobj.path1level >= 5:
            scaleMagnitude *= 1.2
        finalMagnitude = baseMagnitude + int(round(scaleMagnitude))

        print(f"Effect: {effectID} with {baseMagnitude}")
        print(f"+ scalerate {scaleRate} * extra levels {powerlevelOverBase}")
        print(f" = final magnitude {finalMagnitude}")
        return finalMagnitude
    def _scaleToBlesspointCost(self):
        for effectID, baseMagnitude in self.effects.items():
            finalMagnitude = self._getEffectMagnitudeAtPowerLevel(effectID, self.finalpowerlevel)
            self.blessobj.effects[effectID] = finalMagnitude
        self.blessobj.effect10buffs = self.effect10buffs
        self.blessobj.multipick = self.multipick
        self.blessobj.alwaysactive = self.alwaysactive
        self.blessobj.descr = self.descr
        return True
    def __repr__(self):
        return(f"BlessTemplate({self.name})")