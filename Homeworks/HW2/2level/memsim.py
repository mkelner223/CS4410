from Entry import Entry
from PhysicalMemoryManager import PhysicalMemoryManager
from PageTableOuterLevel import PageTableOuterLevel
import sys

# read a memory trace and simulate the action of a virtual memory system 

MAXVIRTUALADDRESS = 1024 * 1024 * 1024 * 4
DEFAULTNUMPHYSPAGES = 1024 * 1024
PAGESIZE = 4 * 1024
PAGEOFFSET_OUTER = 8

def main():
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print "Usage: memsim.py [number of physical pages] tracefilename"
        exit()

    totalphysicalpages = DEFAULTNUMPHYSPAGES
    filenameoffset = 1
    if len(sys.argv) == 3:
        totalphysicalpages = int(sys.argv[1])
        filenameoffset += 1

    tracefile = sys.argv[filenameoffset] + ".trace"
    layoutfile = sys.argv[filenameoffset] + ".layout"

    pmm = PhysicalMemoryManager(totalphysicalpages)
    pt = PageTableOuterLevel(pmm, MAXVIRTUALADDRESS, PAGESIZE, PAGEOFFSET_OUTER)

    # the layout file describes how the program is laid out in memory
    # each line names a range of virtual addresses which contain program
    # content. the code below marks that range as being a memory region
    # that the program can legitimately access. The actual assignment of
    # physical pages to that virtual range is done lazily.
    lf = open(layoutfile, 'r')
    for line in lf.readlines():
        low_vpaddr, dash, high_vpaddr = line.split()
        pt.addRange(int(low_vpaddr, 16), int(high_vpaddr, 16))
    lf.close()
    
    print "Page table is set up"

    # main loop. 
    # read one access, and simulate its effects
    events = 0
    totalTime = eventTime = 0
    f = open(tracefile, 'r')
    for line in f:
        addr, rw = line.split(" ")
        vaddr =  int(addr, 16)
        rw = rw[0]
        #if events < 100:
            #print "addr:", addr
            #print "vaddr: %08X" % vaddr
        if rw[0] == "R":
            eventTime = pt.readMem(vaddr)
        elif rw[0] == "W":
            eventTime = pt.writeMem(vaddr)
        else:
            print "--- ERROR in the trace file"    
        events += 1
        totalTime += eventTime
        if events % 10000 == 0:
            pt.clearAccessBits()
        if events % 100000 == 0:
            print "=========== Current Simulation Time"
            print " =", totalTime, "cycles"
            pmm.printStats()
            pt.printStats()
    f.close()

    print "=========== Current Simulation Time:"
    print " =", totalTime, "cycles"
    print " =", events, "events"
    pmm.printStats()
    pt.printStats()

if __name__=='__main__':
    main()
