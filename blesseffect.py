import re
import utils

EFFECTS_REQURING_MONTAG_DUMMIES = [564, 164]

class BlessEffect(object):
    def __init__(self):
        self.id = None
        self.name = None
        self.effects = {}
        self.scales = {}
        self.effect10buffs = 0
        self.multipick = 0
        self.alwaysactive = 0
        self.path1 = 0
        self.path2 = -1
        self.path1level = 0
        self.path2level = 0
        self.descr = ""
    def processstring(self, string):
        out = string
        while 1:
            m = re.search("\\[EFFECT(\\d*)\\]", out)
            if m is not None:
                effectID = int(m.group(1))
                effectMag = str(self.effects.get(effectID, "???"))
                out = re.sub("\\[EFFECT\\d*\\]", effectMag, out, count=1)
                continue

            m = re.search("\\[EFFECTTIMES25_(\\d*)\\]", out)
            if m is not None:
                effectID = int(m.group(1))
                if effectID in self.effects:
                    effectMag = str(self.effects.get(effectID)*25)
                else:
                    effectMag = "???"
                out = re.sub("\\[EFFECTTIMES25_\\d*\\]", effectMag, out, count=1)
                continue

            m = re.search("\\[EFFECTDIV10_(\\d*)\\]", out)
            if m is not None:
                effectID = int(m.group(1))
                if effectID in self.effects:
                    effectMag = str(round(self.effects.get(effectID) / 10, 1))
                else:
                    effectMag = "???"
                out = re.sub("\\[EFFECTDIV10_\\d*\\]", effectMag, out, count=1)
                continue

            break
        return out
    def _prepareMonsterDummy(self, effectMag):

        s = """
#newmonster {}
#copystats 284
#copyspr 284
#firstshape {}
#secondshape {}
#regeneration -999
#landdamage 100
#uwdamage 100
#drawsize -99
#woundfend 99
#hp 1
#amphibian
#mr 15
#itemslots 262143
#name "{}"
#descr "This unit has no purpose except to spawn in a unit of montag {}."
#end

"""
        s = s.format(utils.START_UNIT_ID, effectMag, effectMag, f"Dummy Montag {effectMag}", effectMag)
        utils.START_UNIT_ID += 1
        return s
    def output(self):
        if len(self.name) < 31 and self.multipick:
            self.name += "*"
        out = f"#selectbless {utils.START_BLESS_ID}\n"
        out += f"#clear\n"
        if self.name is None:
            self.name = f"Unnamed Bless {utils.START_BLESS_ID}"
        out += f'#name "{self.processstring(self.name)}"' + "\n"
        out += f'--#descr "{self.processstring(self.descr)}'
        if self.alwaysactive:
            out += " This effect does not require sacred units to be blessed."
        out += '"'
        out += "\n"
        utils.START_BLESS_ID += 1
        out += f"#path1 {self.path1}\n"
        out += f"#path2 {self.path2}\n"
        out += f"#path1level {self.path1level}\n"
        out += f"#path2level {self.path2level}\n"
        if self.effect10buffs > 0:
            out += f"#effect10buffs {self.effect10buffs}\n"
        if self.multipick:
            out += "#multipick\n"
        if self.alwaysactive:
            out += "#alwaysactive\n"
        for effect, effectMag in self.effects.items():
            # This would work, if .dm commands were also valid in .dbm files
            # potentially useful, but needs converting to write an accompanying .dm file
            #if effect in EFFECTS_REQURING_MONTAG_DUMMIES and effectMag < 0:
            #    out = self._prepareMonsterDummy(effectMag) + out
            #    effectMag = utils.START_UNIT_ID - 1
            out += f"#addeffect {effect} {effectMag} -- {utils.EFFECT_IDS_TO_LABELS.get(effect, 'Unknown Effect')}\n"
        for scale, scaleMag in self.scales.items():
            if scaleMag != 0:
                out += f"#reqscale {scale} {int(scaleMag)}\n"
        out += "#end\n\n"
        return out