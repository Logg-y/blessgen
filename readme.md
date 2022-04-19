# BlessGen

This tool generates semi-random bless effects for Illwinter's Dominions 5. Using its output requires [the Blessmodder tool](https://github.com/Logg-y/blessmodder) I wrote.

Describing this as "procedurally generated" might be a bit of a stretch: essentially this tool draws 99 effects out of a pool of several hundred and presents them as options, in a way that makes a nice spread of paths and point costs. Unlike other similar tools for Dominions, there are (figuratively) not very many possible permutations. While bless effect descriptions remain unmoddable, this will likely not dramatically change: it is very difficult to explain compounded bless effects in a mere 31 characters.

Effects that can be taken multiple times (like vanilla Undying) are marked with an asterisk at the end of their names.

## Answers to anticipated questions

See the caveats section of Blessmodder's readme for side effects relating to modifing bless data within executables.

Test to make sure things work as you'd expect before committing to your build in multiplayer. Please. I won't have caught all my mistakes.

Many bless effects that say +X will stack with attributes on units that have them already. Others, such as "Solar Weapons +5" means that weapons do 5 AP fire damage, x3 vs undead/demons; NOT +8. (The reason one might think this is in the base game Solar Weapons always have a value of three, but in reality there are no hard limits on the damage they can deal!)

"Summon: (Creature)" means that all sacred commanders gain the Summon Allies command to summon one of the named creature type.

"Retinue: (Creature)" means that all sacred units summon one of the named creatures at the start of every battle.

"Prophet" or "Prophet Shape: (Creature)" means that all appointed prophets will immediately become one of the named creature type.

"Temple Train: (Creature)" means that all sacred commanders gain the Temple Trainer command, allowing them to spend a turn at a temple to create one of the named creatures. Only one commander may train at each temple.

Taking multiple of same type of creature related effect is a waste of points: it will cause only the creature with the highest ID to be used. So if you took Summon: Wolf and Summon: Dispossessed Spirit, the summon allies command would yield only a dispossessed spirit (ID 674) over a wolf (ID 284).