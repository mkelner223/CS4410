from Entry import Entry
from PageTableInnerLevel import PageTableSingleLevel
from EvictionDescriptor import EvictionDescriptor

# This class implements a simulates the operation of a single level page table
class PageTableOuterLevel():
    def __init__(self, pmm, maxvsize, pagesize, pageoffset_outer):
        #data that must be passed to second level
        self.pmm = pmm
        self.maxvsize = maxvsize
        self.pagesize = pagesize

        #actual page table pata
        self.nentries = 1 << pageoffset_outer
        self.entries = [None] * self.nentries
        self.pageoffset_outer = pageoffset_outer

        #statistics
        #self.npagefaults = 0
        #self.evictions = 0
        #self.diskwrites = 0

        #extreme ranges for addRange
        self.zeroHighBits = 0x80000000 >> (pageoffset_outer - 1) # addr % self.zeroHighBits zeros top pageoffset_outer bits
        self.addRangeHigh = 0xffffffff >> (pageoffset_outer)
        self.addRangeLow = 0x00000000

    def readMem(self, vaddr):
        pagenumber = vaddr >> (32 - self.pageoffset_outer)
        if self.entries[pagenumber] is None:
            # segmentation fault -- this access occurred to a page that is not legitimately in a 
            # range that can be addressed by the program
            print "Segmentation fault in Outer page table at %08X" % vaddr
            exit(-1)
        return self.entries[pagenumber].readMem(vaddr % self.zeroHighBits, vaddr)
    
    def writeMem(self, vaddr):
        pagenumber = vaddr >> (32 - self.pageoffset_outer)
        if self.entries[pagenumber] is None:
            # segmentation fault -- this access occurred to a page that is not legitimately in a 
            # range that can be addressed by the program
            print "Segmentation fault in Outer page table at %08X" % vaddr
            exit(-1)
        return self.entries[pagenumber].writeMem(vaddr % self.zeroHighBits, vaddr)

    def addRange(self, lo, hi):
        print "Adding range 0x%08X - 0x%08X to the page table" % (lo, hi)
        for index in range(lo >> (32 - self.pageoffset_outer), (hi >> (32 - self.pageoffset_outer)) + 1):
            if self.entries[index] is None:
                #print "Adding second level at index: %d" % index
                self.entries[index] = PageTableSingleLevel(self.pmm, self, self.maxvsize >> self.pageoffset_outer, self.pagesize)
            low = lo % self.zeroHighBits if (index == (lo >> (32 - self.pageoffset_outer))) else self.addRangeLow
            high = hi % self.zeroHighBits if (index == (hi >> (32 - self.pageoffset_outer))) else self.addRangeHigh
            self.entries[index].addRange(low, high, index)

    def clearAccessBits(self):
        for index in range(0, self.nentries):
            if (self.entries[index] is not None):
                self.entries[index].clearAccessBits()

    def findEvictablePage(self):
        lowestCleanEntry = None
        lowestDirtyEntry = None
        lowestPresentEntry = None
        pagesSearched = 0
        for index in range(0, self.nentries):	
            if (self.entries[index] is not None):
                candidate = self.entries[index].findEvictablePage()
                pagesSearched += candidate.pagesSearched
                if (candidate.entry is not None):
	                if (candidate.isClean):
	                    if lowestCleanEntry is None:
	                        lowestCleanEntry = candidate.entry
                            lowestCleanVaddr = (index << (32 - self.pageoffset_outer)) + candidate.vaddr
                            break
	                elif (candidate.isNRU):
	                    if lowestDirtyEntry is None:
	                        lowestDirtyEntry = candidate.entry
                            lowestDirtyVaddr = (index << (32 - self.pageoffset_outer)) + candidate.vaddr
	                elif (candidate.isPresent):
	                    if lowestPresentEntry is None:
	                        lowestPresentEntry = candidate.entry
                            lowestPresentVaddr = (index << (32 - self.pageoffset_outer)) + candidate.vaddr

        if lowestCleanEntry is not None:
            evictablePage = lowestCleanEntry
            evictableVaddr = lowestCleanVaddr
        elif lowestDirtyEntry is not None:
            evictablePage = lowestDirtyEntry
            evictableVaddr = lowestDirtyVaddr
        else:
            evictablePage = lowestPresentEntry
            evictableVaddr = lowestPresentVaddr
        return EvictionDescriptor(evictablePage, evictableVaddr, lowestCleanEntry is not None, lowestDirtyEntry is not None, True, pagesSearched)

    def printStats(self):
        #initialize
        pagesSearched = 0	    
        nentries = 0
        npagefaults = 0	
        evictions = 0	
        diskwrites = 0

        #query inner level for stats	
        for index in range(0, self.nentries):
            if self.entries[index] is not None:
                pagesSearched += self.entries[index].pagesSearched
                nentries += self.entries[index].nentries
                npagefaults += self.entries[index].npagefaults
                evictions += self.entries[index].evictions
                diskwrites += self.entries[index].diskwrites

        #report
        print "=========== Page Table Stats"
        print "- Pages Searched: %d" % pagesSearched
        print "- Page Table Size: %d" % (nentries + self.nentries)
        print "- Page Faults: %d" % npagefaults
        print "- Evictions: %d" % evictions
        print "- Disk Writes: %d" % diskwrites
        print "=--------------------------------------------------------------------"
