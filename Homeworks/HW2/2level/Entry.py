
class Entry():
    def __init__(self):
        self.valid = True
        self.present = False
        self.dirty = False
        self.framenumber = -1
        self.accessed = False

    # assigns a physical page to this virtual page
    def assignPhysicalPage(self, frameno):
        self.framenumber = frameno
        self.present = True
        self.dirty = False

    # return the physcial page currently assigned to this virtual page
    def getPhysicalPageNo(self):
        if self.present:
            return self.framenumber
        else:
            return -1

    # takes away the physical page assigned to this virtual page
    def unassignPhysicalPage(self):
        self.framenumber = -1
        self.present = False
        self.dirty = False

    # update any access statistics, if necessary
    def updateAccessBits(self):
        self.accessed = True

    def clearAccessBits(self):
        self.accessed = False
	
    def __str__(self):
        return "%s %s %s 0x%08xPHYS" % ("V" if self.valid else "X", "P" if self.present else "X", "D" if self.dirty else "-", self.framenumber * 4 * 1024)
