from Entry import Entry
from EvictionDescriptor import EvictionDescriptor

# This class implements a simulates the operation of a single level page table
class PageTableSingleLevel():
    def __init__(self, pmm, pt_outer, maxvsize, pagesize):
        self.pmm = pmm
        self.pt_outer = pt_outer if pt_outer is not None else self
        self.pagesize = pagesize
        self.nentries = (maxvsize / self.pagesize)

        # this is the single level page table
        self.entries = [None] * self.nentries
        self.pagesSearched = 0
        self.npagefaults = 0
        self.evictions = 0
        self.diskwrites = 0

    def access(self, pagenumber, iswrite, vaddr):
        if pagenumber > self.nentries:
            return None
        else:
            e = self.entries[pagenumber]
            if e is None or not e.valid:
                # segmentation fault -- this access occurred to a page that is not legitimately in a 
                # range that can be addressed by the program
                print "Segmentation fault Inner at %08X" % vaddr
                exit(-1)
            eventTime = 100
            if not e.present:
                # this particular virtual address is valid, but currently has no physical page that 
                # has been assigned to it.
                # allocate a physical page, and assign it to this entry
                eventTime = 10000	
                self.npagefaults += 1
                fpno = self.pmm.allocatePhysicalPage()
                if fpno == -1:
                    # we have no free physical pages! 
                    #
                    # Find a suitable physical page to evict to disk
                    victime = self.pt_outer.findEvictablePage()
                    self.evictions += 1
                    self.pagesSearched += victime.pagesSearched
                    eventTime += victime.pagesSearched * 100

                    print "Evicting page at 0x%08x: %s for vaddr 0x%08x" % (victime.vaddr, victime.entry, vaddr)
                    #
                    # this is the actual physical page we'll reuse
                    # when we come out of this block, we'll assign this page to this 
                    fpno = victime.entry.getPhysicalPageNo()
                    # 
                    # save its current contents to disk if they are dirty (we do not 
                    #    actually do the disk write here, because we're just simulating)
                    if victime.entry.dirty:
                        self.diskwrites += 1
                        eventTime += 50000
                    #
                    # mark this page as no longer present in memory
                    victime.entry.unassignPhysicalPage()

                e.assignPhysicalPage(fpno)
            e.updateAccessBits()
            if iswrite:
                e.dirty = True
            return eventTime

    def readMem(self, vaddr, addr):
        pagenumber = vaddr / self.pagesize
        eventTime = self.access(pagenumber, False, addr)
        return eventTime
    
    def writeMem(self, vaddr, addr):
        pagenumber = vaddr / self.pagesize
        eventTime = self.access(pagenumber, True, addr)
        return eventTime

    def addRange(self, lo, hi, index):
        for vpno in range((lo / self.pagesize), (hi/self.pagesize) + 1):
            self.entries[vpno] = Entry()

    def clearAccessBits(self):
        for index in range(0, self.nentries):
            if (self.entries[index] is not None):
                self.entries[index].clearAccessBits()

    def findEvictablePage(self):
        lowestPresentEntry = None
        lowestDirtyEntry = None
        lowestCleanEntry = None
        pagesSearched = 0
        for candidateIndex in range(0, self.nentries):
            pagesSearched += 1	
            if self.entries[candidateIndex] is not None and self.entries[candidateIndex].present:
                if lowestPresentEntry is None:
                    lowestPresentEntry = candidateIndex
                if not self.entries[candidateIndex].accessed:
                    if lowestDirtyEntry is None:
                        lowestDirtyEntry = candidateIndex
                    if not self.entries[candidateIndex].dirty:
                        if lowestCleanEntry is None:
                            lowestCleanEntry = candidateIndex
                            break

        if lowestCleanEntry is not None:
            candidateIndex = lowestCleanEntry
        elif lowestDirtyEntry is not None:
            candidateIndex = lowestDirtyEntry
        elif lowestPresentEntry is not None:
            candidateIndex = lowestPresentEntry
        else:
            candidateIndex = -1
        candidateEntry = self.entries[candidateIndex] if (candidateIndex != -1) else None
        return EvictionDescriptor(candidateEntry, candidateIndex * self.pagesize, lowestCleanEntry is not None, lowestDirtyEntry is not None, lowestPresentEntry is not None, pagesSearched)
