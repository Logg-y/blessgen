import os
import re
import utils
import traceback

from blesstemplate import BlessTemplate
from exceptions import ParseError
import fileparserutils

simple_params_int = ["paths","pathlevel", "effect10buffs", "multipick", "alwaysactive", "reqcrosspath", "skipchance"]
simple_params_str = ["descr"]
simple_params_float = []


def readEffectFile(fp):
	"Read one file and return all the bless effects within."
	try:
		lineno = None
		out = {}
		curreff = None
		with open(fp, "r") as f:
			for lineno, line in enumerate(f):
				line = line.strip()
				if line == "": continue
				if line.startswith("--"): continue

				if line.startswith("#newbless"):
					if curreff is not None:
						raise ParseError(
							f"{fp} line {lineno}: Unexpected #neweffect (still parsing previous effect)")
					m = re.match("#newbless\W+\"(.*)\"\W*$", line)
					if m is None:
						raise ParseError(f"{fp} line {lineno}: Expected an effect name, none was found")
					curreff = BlessTemplate(fp)
					curreff.name = m.groups()[0]
					currPriority = 0

				else:
					if curreff is None:
						raise ParseError(f"{fp} line {lineno}: Expected a #neweffect line")

					sorted = False

					# Params to simply copy
					for simple in simple_params_int:
						if fileparserutils.parsesimpleint(simple, line, curreff):
							sorted = True
							break

					if sorted: continue

					for simple in simple_params_str:
						m = re.match(f"#{simple}" + "\\W+?\"(.*)\"\\W*", line)
						if m is not None:
							pval = m.groups()[0]
							setattr(curreff, simple, pval)
							sorted = True
							continue

					if sorted: continue

					for simple in simple_params_float:
						m = re.match(f"#{simple}\W+?([-.0-9]+)\W*$", line)
						if m is not None:
							pval = float(m.groups()[0])
							setattr(curreff, simple, pval)
							sorted = True
							continue

					if sorted: continue

					if line.startswith("#addeffect"):
						m = re.match('#addeffect\\W+([-0-9]+)\\W+?([-.0-9]+)', line)
						if m is None:
							raise ParseError(f"{fp} line {lineno}: bad #addeffect")
						effect = int(m.groups()[0])
						magnitude = int(m.groups()[1])
						if effect in curreff.effects:
							raise ParseError(f"Attempting to assign effect {effect} to {cureff.name} twice")
						curreff.effects[effect] = magnitude
						continue

					if line.startswith("#scaleeffect"):
						m = re.match('#scaleeffect\\W+([-0-9]+)\\W+?([-.0-9]+)', line)
						if m is None:
							raise ParseError(f"{fp} line {lineno}: bad #scaleeffect")
						effect = int(m.groups()[0])
						magnitude = float(m.groups()[1])
						if effect in curreff.scaleeffects:
							raise ParseError(f"Attempting to set scaling for {effect} on {cureff.name} twice")
						curreff.scaleeffects[effect] = magnitude
						continue

					if line.startswith("#posscaleaffinity"):
						m = re.match('#posscaleaffinity\\W+([-0-9]+)\\W+([-0-9]+)', line)
						if m is None:
							raise ParseError(f"{fp} line {lineno}: bad #posscaleaffinity")
						effect = int(m.groups()[0])
						magnitude = float(m.groups()[1])
						if effect in curreff.posscaleaffinities:
							raise ParseError(f"Attempting to set posscaleaffinity for {effect} on {cureff.name} twice")
						curreff.posscaleaffinities[effect] = magnitude
						continue

					if line.startswith("#negscaleaffinity"):
						m = re.match('#negscaleaffinity\\W+([-0-9]+)\\W+([-0-9]+)', line)
						if m is None:
							raise ParseError(f"{fp} line {lineno}: bad #negscaleaffinity")
						effect = int(m.groups()[0])
						magnitude = int(m.groups()[1])
						if effect in curreff.negscaleaffinities:
							raise ParseError(f"Attempting to set negscaleaffinity for {effect} on {cureff.name} twice")
						curreff.negscaleaffinities[effect] = magnitude
						continue

					if line.startswith("#maxeffectvalue"):
						m = re.match('#maxeffectvalue\\W+([-0-9]+)\\W+([-0-9]+)', line)
						if m is None:
							raise ParseError(f"{fp} line {lineno}: bad #addeffect")
						effect = int(m.groups()[0])
						magnitude = int(m.groups()[1])
						if effect in curreff.maxeffectvalues:
							raise ParseError(f"Attempting to set max value for {effect} on {cureff.name} twice")
						curreff.maxeffectvalues[effect] = magnitude
						continue

					if line.startswith("#name"):
						m = re.match('#name\\W+(.*?)\\W+"(.*)"', line)
						if m is None:
							raise ParseError(f"{fp} line {lineno}: bad #name")
						paths = fileparserutils.parsepathalias(m.groups()[0])
						for path in utils.breakdownflagcomponents(paths):
							if path not in curreff.names:
								curreff.names[path] = []
							curreff.names[path].append(m.groups()[1])
						continue

					if line.startswith("#end"):
						out[curreff.name] = curreff
						curreff = None
						continue

					raise ParseError(f"{fp} line {lineno}: Unrecognised content: {line}")
		return out
	except:
		print(traceback.format_exc())
		if lineno is not None:
			raise ParseError(f"Failed to read {fp}, failed at line {lineno}")
		else:
			raise ParseError(f"Failed to read {fp}, undetermined line")


def readEffectsFromDir(dir):
	out = utils.blesseffects
	new = []
	for f in os.listdir(dir):
		if f.endswith(".txt"):
			c = readEffectFile(os.path.join(dir, f))
			for key in c:
				if key in out:
					raise ParseError(f"Bless named {key} already exists and was redefined in {f}")
				out[key] = c[key]
				new.append(key)
	o = {}
	for key in new:
		o[key] = out[key]
	return o

