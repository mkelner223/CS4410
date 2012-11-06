

class PhysicalMemoryManager:
    def __init__(self, numphyspages):
        self.size = numphyspages
        self.pageinuse = [False]*self.size

        self.nallocs = self.ndeallocs = 0
        self.lastallocated = 0

    # find a free physical page to allocate
    def allocatePhysicalPage(self):
        for foffset in range(0, self.size):
            fno = (self.lastallocated + foffset) % self.size
            if not self.pageinuse[fno]:
                self.nallocs += 1
                self.pageinuse[fno] = True
                self.lastallocated = fno
                return fno
        return -1

    def deallocatePhysicalPage(self, fno):
        self.ndeallocs += 1
        self.pageinuse[fno] = False

    def printStats(self):
        print "=========== Physical Memory Statistics"
        print "= Total Number of Physical Pages: %d" % self.size
        print "= Number of Allocations: %d" % self.nallocs
        print "= Number of Deallocations: %d" % self.ndeallocs

            
        
