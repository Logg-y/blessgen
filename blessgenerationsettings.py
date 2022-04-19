

class BlessGenerationSettings(object):
    def __init__(self, path1, path2, level):
        self.blesspointcost = level
        self.primarypath = path1
        self.secondarypath = path2
        self.allowskipchance = True
    def __repr__(self):
        return(f"BlessSettings(path1={self.primarypath}, path2={self.secondarypath}, "
               f"blesspts={self.blesspointcost})")