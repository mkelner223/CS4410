from Entry import Entry

class EvictionDescriptor():
    def __init__(self, entry, vaddr, isClean, isNRU, isPresent, pagesSearched):
        self.entry = entry
        self.vaddr = vaddr
        self.isClean = isClean
        self.isNRU = isNRU
        self.isPresent = isPresent
        self.pagesSearched = pagesSearched